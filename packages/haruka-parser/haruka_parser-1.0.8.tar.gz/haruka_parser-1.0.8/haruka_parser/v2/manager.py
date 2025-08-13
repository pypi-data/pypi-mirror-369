from haruka_parser.v2.config import Unique_ID
from dataclasses import dataclass
from lxml.html import Element
import logging
import json
import re
from collections import Counter
import unicodedata

class TableFormat:
    github = "github"
    grid = "grid"
    simple = "simple"

@dataclass
class DomMeta:
    id: str
    type: str
    data: dict

    def __repr__(self):
        return f"DomMeta(id={self.id},\ntype={self.type},\ndata={json.dumps(self.data, ensure_ascii=False, indent=2)})"


class ContextManager:
    def __init__(self, unique_id: str = Unique_ID, need_comment: bool = True, base_url: str = "", format: str = "markdown", table_format: TableFormat = TableFormat.github, separator: str = "\n\n"):
        self.unique_id = unique_id
        self.need_comment = need_comment
        self.base_url = base_url
        self.unique_id_offset = 0
        self.unique_ids = set()
        self.link_list_unique_ids = set()

        self.format = format

        self.enable_code = True
        self.code_languages = set()
        self.code_block = 0
        self.code_line = 0
        self.code_length = 0

        self.table_format = table_format
        self.table_block = 0

        self.dom_meta = {}
        self.dom_attrs = {}

        self.links = []

        self.math_stats = Counter()

        self.unique_tags = set()

        self.title = ""
        self.add_title = True
        self.time = ""
        self.extract_time = True

        self.encoding = "utf-8"

        self.separator = separator

        self.meta_to_text_func = {
            "math": self.meta_to_math_text,
            "table": self.meta_to_table_text,
            "img": self.meta_to_img_text,
            "svg": self.meta_to_img_text,
            "code": self.meta_to_code_text,
        }

        self.node_to_text_fast_cache = {}

        self.skip_heuristic = False
    
    def meta_to_math_text(self, meta: DomMeta) -> str:
        return meta.data["text"]
    
    # code 段落优化
    def get_bullet_text(self, text: str) -> str:
        lines = text.splitlines()
        # 尝试提取每行的行号
        line_numbers = []
        contents = []
        for line in lines:
            if line.strip() == "":
                continue
            parts = line.lstrip().split(maxsplit=1)
            if len(parts) == 0:
                contents.append(line)
                continue
            # 检查第一个部分是不是数字（可能带点）
            num_part = parts[0].rstrip('.')
            
            num_part_int = None
            if num_part.isdigit():
                try:
                    num_part_int = int(unicodedata.normalize('NFKC', num_part))
                except:
                    pass
            if num_part_int:
                line_numbers.append(num_part_int)
                if len(parts) > 1:
                    contents.append(parts[1].lstrip())
            else:
                # 不是数字开头，直接加入
                contents.append(line)
        # 检查行号是否为不减序列且长度大于等于非空行数
        if (len(line_numbers) >= len(contents) and
            all(line_numbers[i] <= line_numbers[i+1] for i in range(len(line_numbers)-1))):
            return "\n".join(contents)

    def meta_to_table_text(self, meta: DomMeta) -> str:
        bullet_text = self.get_bullet_text(meta.data["text"])
        if bullet_text:
            return bullet_text
        # this is not deterministic
        # if (meta.data["row_count"] == 1 or meta.data["col_count"] == 1):
        #     return ""
        return meta.data["text"]
    
    def meta_to_img_text(self, meta: DomMeta) -> str:
        return ""
    
    def meta_to_code_text(self, meta: DomMeta) -> str:
        return meta.data["text"]
    
    def set_unique_id(self, node: Element):
        unique_id = self.get_next_unique_id()
        node.attrib[self.unique_id] = unique_id

    def get_next_unique_id(self) -> str:
        self.unique_id_offset += 1
        current_id = str(self.unique_id_offset)
        self.unique_ids.add(current_id)
        return current_id
    
    def add_dom_meta(self, node: Element, dom_type: str, meta: dict, old_node: Element = None):
        unique_id = node.attrib.get(self.unique_id, "")
        if not unique_id:
            logging.error(f"Unique ID not found for node {node.tag}")
            return
        
        old_unique_id = None
        if old_node is not None:
            old_unique_id = old_node.attrib.get(self.unique_id, None)
        
        if not old_unique_id:
            old_unique_id = unique_id
        
        if old_unique_id in self.dom_meta:
            existing_meta = self.dom_meta[old_unique_id]
            meta = {**existing_meta.data, **meta}


        self.dom_meta[unique_id] = DomMeta(
            id=unique_id,
            type=dom_type,
            data=meta,
        )

        # 魔法变量，加了以后让 smart_paragraphs_priority 可以自动聚类新增节点
        node.attrib[f"{self.unique_id}_type"] = dom_type

        # print(unique_id, dom_type, meta)
        # if dom_type == "math":
        #     print(self.dom_meta[unique_id].data["text"])
        # if dom_type == "table":
        #     print(meta["text"])
        # if dom_type == "img":
        #     print(unique_id, old_unique_id, meta)
    
    def get_dom_meta(self, node: Element):
        unique_id = node.attrib.get(self.unique_id, "")
        if not unique_id:
            return None
        return self.dom_meta.get(unique_id, None)

    @property
    def found_math(self):
        return sum(self.math_stats.values()) > 0
    
    def get_unique_tag(self, tag: str):
        unique_tag = f"[{self.unique_id}_{tag}]"
        self.unique_tags.add(unique_tag)
        return unique_tag
    
    def clear_unique_tags(self, text):
        # if self.unique_id in text:
        #     for unique_tag in self.unique_tags:
        #         text = text.replace(unique_tag, "")
        pattern = rf'\[{re.escape(self.unique_id)}[^\]]*\]'
        text = re.sub(pattern, '', text)
        return text
    
    def meta_to_text(self, meta: DomMeta) -> str:
        if not meta:
            return None
        func = self.meta_to_text_func.get(meta.type, None)
        if func is None:
            return None
        return func(meta)