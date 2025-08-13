from haruka_parser.v2.manager import ContextManager
from urllib.parse import unquote, urljoin
from lxml.html import Element
from haruka_parser.v2.utils.lxml import remove_node, node_to_text_fast, iter_unique_ids
from haruka_parser.v2.doms.base_dom import BaseDom
from haruka_parser.v2.doms.turndown_dom import Paragraph
import re
import string
import unicodedata

class LinkDom(BaseDom):
    def __init__(self):
        self.BLACKLIST_END_SYMBOL = {"…", "...", "。。。", "．．．"}
        self.spaceRe = re.compile("\s+", re.UNICODE)
        PUNCTUATION = string.punctuation
        PUNCTUATION += "0123456789！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
        PUNCTUATION = re.escape(PUNCTUATION)
        self.nonAlphaRe = re.compile(f"[{PUNCTUATION}]")

    def normalize_text(self, text):
        if not text:
            return ""
        
        filtered_lines = []
        for line in text.split("\n"):
            if any(line.endswith(blacklist) for blacklist in self.BLACKLIST_END_SYMBOL):
                continue
            filtered_lines.append(line)
        text = "\n".join(filtered_lines)

        text = unicodedata.normalize("NFC", text)
        text = self.nonAlphaRe.sub(" ", text)
        text = self.spaceRe.sub(" ", text)
        text = text.strip()
        
        return re.sub(r"\s+", "", text).strip()
    
    # 直到 parent 的覆盖率低于 70%，否则始终认为属于 list
    def recursive_check_parent(self, list_node: Element, list_node_text: str, manager: ContextManager, link_density_threshold = 0.7):
        parent_node = list_node.getparent()
        if parent_node is not None:
            parent_node_text = self.normalize_text(node_to_text_fast(parent_node, manager))
            if len(parent_node_text) > 0 and len(list_node_text) / len(parent_node_text) >= link_density_threshold:
                return self.recursive_check_parent(parent_node, list_node_text, manager, link_density_threshold)
        return list_node


    def preprocess(self, node: Element, manager: ContextManager, link_density_threshold = 0.7):
        lists = node.xpath('.//ul | .//ol | .//nav | .//table')
        # lists = node.xpath('.//ul | .//ol | .//div | .//span | .//nav | .//table | .//p')
        to_remove = []
        for _list in lists:
            children = _list.getchildren()
            if len(children) == 0 or len(children) == 1:
                continue

            # All <a> descendants
            links = _list.xpath('.//a')
            
            # All text in direct children (not just links)
            total_children_text = self.normalize_text(node_to_text_fast(_list, manager))

            # All text in links
            total_links_text = "".join([node_to_text_fast(a, manager) for a in links])
            total_links_text = self.normalize_text(total_links_text)

            if len(total_children_text) == 0 or len(total_links_text) == 0:
                continue

            ratio = len(total_links_text) / len(total_children_text)

            if ratio >= link_density_threshold:
                to_remove.append(self.recursive_check_parent(_list, total_children_text, manager, link_density_threshold))

        for _list in to_remove:
            # remove_node(_list, manager)
            for unique_id in iter_unique_ids(_list, manager):
                manager.link_list_unique_ids.add(unique_id)

    def _process(self, node: Element, manager: ContextManager):
        # node_tag = node.tag.lower()
        href = node.get("href")
        if href and not href.startswith(('mailto:', 'tel:', '#', 'javascript:', 'data:')):
            if manager.base_url:
                href = urljoin(manager.base_url, href)
            manager.links.append(href)
    
    def paragraphs_process(self, paragraphs: list[Paragraph], manager: ContextManager, link_density_threshold = 0.9, min_paragraph_length = 3):
        link_list = []
        for paragraph in paragraphs:
            if paragraph.tag == "a":
                link_list.append((paragraph.unique_id, 1.0))
            else:
                total_links_text = ""
                total_children_text = ""
                for item in paragraph.items:
                    if item.tag == "a":
                        total_links_text += item.text
                    total_children_text += item.text
                total_links_text = self.normalize_text(total_links_text)
                total_children_text = self.normalize_text(total_children_text)
                if len(total_children_text) > 0:
                    ratio = len(total_links_text) / len(total_children_text)
                    link_list.append((paragraph.unique_id, ratio))
                else:
                    link_list.append((paragraph.unique_id, 1.0))
        
        streak = []
        for unique_id, ratio in link_list:
            if ratio >= link_density_threshold:
                streak.append(unique_id)
            else:
                if len(streak) >= min_paragraph_length:
                    for uid in streak:
                        manager.link_list_unique_ids.add(uid)
                streak = []
        if len(streak) >= 3:
            for uid in streak:
                manager.link_list_unique_ids.add(uid)