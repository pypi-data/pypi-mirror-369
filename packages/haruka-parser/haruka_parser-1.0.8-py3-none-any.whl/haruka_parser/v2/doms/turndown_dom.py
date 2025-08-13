from haruka_parser.v2.manager import ContextManager
from lxml.html import Element
from haruka_parser.v2.utils.lxml import remove_node, replace_node_with_element, node_to_text, iter_node, html_tostring
from haruka_parser.line_processing import have_chinese_characters, restore_replacements
from tabulate import tabulate
# from haruka_parser.trafilatura.trafilatura.main_extractor import extract
from copy import deepcopy

import re
import lxml.sax
from xml.sax.handler import ContentHandler
from haruka_parser.v2.config import PARAGRAPH_TAGS, EXCLUDE_WHITESPACE_STRIP_TAGS
from dataclasses import dataclass, field

from lxml.html import fragment_fromstring, Element
from lxml import etree
import re
import lxml.sax
from xml.sax.handler import ContentHandler
from dataclasses import dataclass, asdict
from copy import deepcopy

from difflib import SequenceMatcher
from collections import defaultdict
from haruka_parser.v2.doms.base_dom import BaseDom

HEADINGS_PATTERN = re.compile(r"\bh\d\b")

MULTIPLE_WHITESPACE_PATTERN = re.compile(r"\s+", re.UNICODE)

def normalize_whitespace(text, space_only=True):
    """
    Translates multiple whitespace into single space character.
    If there is at least one new line character chunk is replaced
    by single LF (Unix new line) character.
    """
    if space_only:
        return MULTIPLE_WHITESPACE_PATTERN.sub(lambda x: " ", text)
    else:
        return MULTIPLE_WHITESPACE_PATTERN.sub(_replace_whitespace, text)


def _replace_whitespace(match):
    """Normalize all spacing characters that aren't a newline to a space."""
    text = match.group()
    if text.count("\n") > 1:
        return "\n\n"
    elif text.count("\n") == 1:
        return "\n"
    elif "\r" in text:
        return "\r"
    return " "

def is_blank(string):
    """
    Returns `True` if string contains only white-space characters
    or is empty. Otherwise `False` is returned.
    """
    return not string or string.isspace()

@dataclass
class TextItem:
    text: str
    tag: str
    unique_id: str
    unique_id_meta: dict = None
    priority: list[str] = field(default_factory=list)

class Paragraph(object):
    """Object representing one block of text in HTML."""
    def __init__(self, path):
        self.dom_path = path.dom
        self.xpath = path.xpath
        self.unique_id = path.unique_id
        self.unique_id_meta = None
        self.priority = []
        self.tag = path.tag
        self.items = []

    def to_dict(self):
        return dict({
            "dom_path": self.dom_path,
            "xpath": self.xpath,
            "unique_id": self.unique_id,
            "unique_id_meta": asdict(self.unique_id_meta) if self.unique_id_meta else None,
            "priority": self.priority,
            "tag": self.tag,
            "items": [asdict(item) for item in self.items]
        })

    @property
    def is_heading(self):
        return bool(HEADINGS_PATTERN.search(self.dom_path))
    
    @property
    def text(self):
        return "".join(item.text for item in self.items)

    def contains_text(self):
        return bool(self.items) and any(len(item.text.strip()) > 0 for item in self.items)

    def append_item(self, item: TextItem):
        self.items.append(item)
        return item
    
    def merge(self):
        """合并相邻且具有相同tag和unique_id的TextItem"""
        if not self.items:
            return
        
        merged_items = []
        current_item = self.items[0]

        for i in range(1, len(self.items)):
            next_item = self.items[i]
            
            # 如果相邻item有相同的tag和unique_id，合并text
            if (current_item.tag == next_item.tag and 
                current_item.unique_id == next_item.unique_id):
                current_item.text += next_item.text
            else:
                merged_items.append(current_item)
                current_item = next_item
        
        merged_items.append(current_item)

        if merged_items[0].tag not in EXCLUDE_WHITESPACE_STRIP_TAGS:
            merged_items[0].text = merged_items[0].text.lstrip()
        if merged_items[-1].tag not in EXCLUDE_WHITESPACE_STRIP_TAGS:
            merged_items[-1].text = merged_items[-1].text.rstrip()

        self.items = [item for item in merged_items if len(item.text) > 0]

class PathInfo(object):
    def __init__(self):
        # list of triples (tag name, order, children, attributes)
        self._elements = []

    @property
    def dom(self):
        return ".".join(e[0] for e in self._elements)

    @property
    def xpath(self):
        return "/" + "/".join("%s[%d]" % e[:2] for e in self._elements)

    def append(self, tag_name, unique_id):
        children = self._get_children()
        order = children.get(tag_name, 0) + 1
        children[tag_name] = order

        xpath_part = (tag_name, order, {}, unique_id)
        self._elements.append(xpath_part)

        return self

    def pop(self):
        if self._elements:
            self._elements.pop()
        return self

    def _get_children(self):
        if self._elements:
            return self._elements[-1][2]
        return {}
    
    @property
    def tag(self):
        """获取当前标签名"""
        if self._elements:
            return self._elements[-1][0]
        return None
    
    @property
    def unique_id(self):
        """获取当前元素或最近父元素的unique_id"""
        # 从当前元素开始向上查找id属性
        for element in reversed(self._elements):
            unique_id = element[3]
            if unique_id:
                return unique_id
        return None

class ParagraphMaker(ContentHandler):
    """
    A class for converting a HTML page represented as a DOM object into a list
    of paragraphs.
    """

    @classmethod
    def make_paragraphs(cls, root, manager: ContextManager):
        """Converts DOM into paragraphs."""
        handler = cls(manager)
        lxml.sax.saxify(root, handler)
        return handler.paragraphs

    def __init__(self, manager: ContextManager):
        self.path = PathInfo()
        self.paragraphs = []
        self.paragraph = None
        self.manager = manager
        self._start_new_paragraph()

    def _start_new_paragraph(self):
        if self.paragraph and self.paragraph.contains_text():
            self.paragraph.merge()
            if self.paragraph.contains_text():
                self.paragraphs.append(self.paragraph)

        self.paragraph = Paragraph(self.path)

    def get_attr(self, attrs):
        attr_dict = {}
        for attr_name, attr_value in attrs.items():
            if attr_value:
                if attr_name[1]:
                    attr_dict[attr_name[1]] = attr_value
                else:
                    attr_dict[attr_name[0]] = attr_value
        return attr_dict

    def startElementNS(self, name, qname, attrs):
        name = name[1]

        attr_dict = self.get_attr(attrs)
        unique_id = attr_dict.pop("ciallo_3052e5", None)
        if attr_dict and self.manager.dom_attrs.get(unique_id, None) is None:
            self.manager.dom_attrs[unique_id] = attr_dict
        
        self.path.append(name, unique_id)

        if name in PARAGRAPH_TAGS:
            self._start_new_paragraph()
        
        if name == "br":
            self.paragraph.append_item(TextItem(
                text="\n",
                tag="br",
                unique_id=unique_id
            ))

    def endElementNS(self, name, qname):
        name = name[1]
                    
        self.path.pop()

        if name in PARAGRAPH_TAGS:
            self._start_new_paragraph()

    def endDocument(self):
        if self.paragraph and self.paragraph.contains_text():
            self.paragraphs.append(self.paragraph)

    def characters(self, content):
        if not content:
            return
        
        content = normalize_whitespace(content)

        text_item = TextItem(
            text=content,
            tag=self.path.tag,
            unique_id=self.path.unique_id
        )
        
        self.paragraph.append_item(text_item)

class TurndownDom(BaseDom):
    def __init__(self):
        pass

    def make_paragraphs(self, node: Element, manager: ContextManager):
        paragraphs = ParagraphMaker.make_paragraphs(node, manager)
        return paragraphs
    
    def attach_dom_meta(self, paragraphs: list[Paragraph], manager: ContextManager):
        done_unique_ids = set()
        for paragraph in paragraphs:
            if paragraph.unique_id not in done_unique_ids:
                paragraph.unique_id_meta = manager.dom_meta.get(paragraph.unique_id, None)
                done_unique_ids.add(paragraph.unique_id)
            for item in paragraph.items:
                if item.unique_id not in done_unique_ids:
                    item.unique_id_meta = manager.dom_meta.get(item.unique_id, None)
                    done_unique_ids.add(item.unique_id)

    def paragraphs_todict(self, paragraphs: list[Paragraph]):
        return [paragraph.to_dict() for paragraph in paragraphs]
    
    def paragraph_to_text(self, paragraph: Paragraph, manager: ContextManager) -> str:
        text = manager.meta_to_text(paragraph.unique_id_meta)
        if text is not None:
            return text
        
        text = []
        for item in paragraph.items:
            item_text = manager.meta_to_text(item.unique_id_meta)
            if item_text is not None:
                text.append(item_text)
            else:
                text.append(item.text)
        
        text = "".join(text)
        if paragraph.tag not in EXCLUDE_WHITESPACE_STRIP_TAGS:
            text = normalize_whitespace(text, space_only=False)
            text = text.strip()
        return text


    def set_paragraphs_priority(self, paragraphs: list[Paragraph], manager: ContextManager, keep_ids: set[str], priority_name: str):
        for paragraph in paragraphs:
            if paragraph.unique_id in keep_ids:
                paragraph.priority.append(priority_name)
            for item in paragraph.items:
                if item.unique_id in keep_ids:
                    item.priority.append(priority_name)
                    paragraph.priority.append(priority_name)
            paragraph.priority = list(set(paragraph.priority))
    
    def is_same_attribute(self, a, b):
        if a is None or b is None:
            return a is None and b is None

        a_parts = set(re.findall(r'[^\d\s]+', str(a)))
        b_parts = set(re.findall(r'[^\d\s]+', str(b)))

        return not a_parts.isdisjoint(b_parts)

    def attributes_are_alike(self, original_attributes: dict, candidate_attributes: dict, similarity_threshold: float = 0.999) -> bool:
        """Calculate a score of how much these elements are alike and return True
            if score is higher or equal the threshold"""
        score, checks = 0, 0

        # original_attributes = {
        #     "class": original_attributes.get("class", ""),
        #     "style": original_attributes.get("style", ""),
        # }

        if original_attributes:
            # score += sum(
            #     SequenceMatcher(None, v, candidate_attributes.get(k, '')).ratio()
            #     for k, v in original_attributes.items()
            # )
            score += sum(self.is_same_attribute(candidate_attributes.get(k, ''), v) for k, v in original_attributes.items())
            checks += len(candidate_attributes)
        else:
            if not candidate_attributes:
                # Both doesn't have attributes, this must mean something
                # score += 1
                checks += 1

        if checks:
            return round(score / checks, 2) >= similarity_threshold
        return False

    def deprecated_smart_paragraphs_priority(self, paragraphs: list[Paragraph], manager: ContextManager):
        # 按照dom_path分组段落
        dom_path_groups = defaultdict(list)
        for paragraph in paragraphs:
            dom_path_groups[paragraph.dom_path].append(paragraph)
        
        # 对每个dom_path组进行聚类
        for dom_path, group_paragraphs in dom_path_groups.items():
            if len(group_paragraphs) <= 1:
                continue
                
            # 初始化并查集
            parent = list(range(len(group_paragraphs)))
            
            def find(x):
                if parent[x] != x:
                    parent[x] = find(parent[x])
                return parent[x]
            
            def union(x, y):
                px, py = find(x), find(y)
                if px != py:
                    parent[px] = py
            
            # 根据attributes_are_alike进行连边
            for i in range(len(group_paragraphs)):
                for j in range(i + 1, len(group_paragraphs)):
                    attrs_i = manager.dom_attrs.get(group_paragraphs[i].unique_id, {})
                    attrs_j = manager.dom_attrs.get(group_paragraphs[j].unique_id, {})
                    if self.attributes_are_alike(attrs_i, attrs_j):
                        union(i, j)
                    # elif ((attrs_i.get("class", "") or "attrs_i") == (attrs_j.get("class", "") or "attrs_j")):
                    #     print(attrs_i, attrs_j)
            
            # 收集每个聚类的所有priority
            cluster_priorities = defaultdict(set)
            for i, paragraph in enumerate(group_paragraphs):
                root = find(i)
                cluster_priorities[root].update(paragraph.priority)

            # 为每个段落设置聚类的priority并集
            for i, paragraph in enumerate(group_paragraphs):
                root = find(i)
                paragraph.priority = list(cluster_priorities[root])
    
    def smart_paragraphs_priority(self, paragraphs: list[Paragraph], manager: ContextManager):
        """
        高效地根据段落的DOM属性对段落进行聚类，并合并它们的优先级。
        使用哈希分组代替O(N^2)的循环比较和并查集。
        """
        # 1. 按照 dom_path 对段落进行初步分组
        dom_path_groups = defaultdict(list)
        for paragraph in paragraphs:
            dom_path_groups[paragraph.dom_path].append(paragraph)
        
        # 2. 对每个 dom_path 组内的段落，根据其属性进行再次聚类
        for dom_path, group_paragraphs in dom_path_groups.items():
            # 如果组内只有一个或没有段落，则无需处理
            if len(group_paragraphs) <= 1:
                continue
            
            # 使用字典进行高效聚类。
            # 键是属性的哈希签名，值是具有这些属性的段落列表。
            attribute_clusters = defaultdict(list)
            
            for paragraph in group_paragraphs:
                # 获取属性字典
                attrs = manager.dom_attrs.get(paragraph.unique_id, {})
                if not attrs:
                    continue
                
                attrs_no_digits = []
                for item in attrs.values():
                    if isinstance(item, str):
                        attrs_no_digits.extend(re.findall(r'[^\d\s]+', item))
                if attrs_no_digits:
                    attribute_signature = frozenset(attrs_no_digits)

                    # 将段落添加到对应的聚类中
                    attribute_clusters[attribute_signature].append(paragraph)

            # 3. 遍历聚类结果，合并优先级并更新段落
            for cluster_paragraphs in attribute_clusters.values():
                # 如果一个聚类中只有一个段落，则无需合并
                if len(cluster_paragraphs) <= 1:
                    continue

                # 使用 set 来合并所有段落的 priority，自动去重
                merged_priorities = set()
                for p in cluster_paragraphs:
                    merged_priorities.update(p.priority)
                
                # 将合并后的结果（set）转换回列表
                final_priorities = list(merged_priorities)
                
                # 将合并后的优先级更新到该聚类中的每一个段落
                for p in cluster_paragraphs:
                    p.priority = final_priorities

    def process_paragraphs(self, paragraphs: list[Paragraph], manager: ContextManager, priority_method = None):
        text = []
        for paragraph in paragraphs:
            if priority_method is not None and not priority_method(paragraph.priority):
                continue
            paragraph_text = self.paragraph_to_text(paragraph, manager)
            if paragraph_text:
                text.append(paragraph_text)
        return manager.separator.join(text)
    
    def process_tree(self, node: Element, manager: ContextManager, keep_ids: set[str]):
        result_body = Element('body')
        backup_tree = deepcopy(node)
        for element in iter_node(backup_tree):
            if element.tag == "done":
                continue
            processed_element = deepcopy(element)
            unique_id = element.get(manager.unique_id)
            if unique_id in keep_ids:
                result_body.append(processed_element)
                keep_ids.remove(unique_id)
                for child in element.iter("*"):
                    child.tag = "done"
                
        return result_body
    
    def xor_process_tree(self, node: Element, manager: ContextManager, keep_ids: set[str]):
        result_body = deepcopy(node)
        for element in iter_node(result_body):
            unique_id = element.get(manager.unique_id)
            if unique_id in keep_ids:
                remove_node(element, manager)
                keep_ids.remove(unique_id)
        return result_body