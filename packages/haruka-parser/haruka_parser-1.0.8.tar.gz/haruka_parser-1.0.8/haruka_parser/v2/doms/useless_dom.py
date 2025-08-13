from haruka_parser.v2.manager import ContextManager
from haruka_parser.v2.config import MANUALLY_CLEANED
from urllib.parse import unquote, urljoin
from lxml.html import Element
from haruka_parser.v2.utils.lxml import remove_node
import os
import re
from haruka_parser.v2.doms.base_dom import BaseDom

class UselessDom(BaseDom):
    def __init__(self):
        self.load_selectors()

    def load_selectors(self):

        selectors_path = os.path.join(
            os.path.dirname(__file__), "../..", "dictionary/banned_selectors.txt"
        )
        with open(selectors_path, "r") as f:
            selectors = [line.replace("\n", "").strip() for line in f]
        
        class_selectors = []
        id_selectors = []
        class_wild_selectors = []
        style_wild_selectors = []

        for selector in selectors:
            if selector.startswith("."):
                # class选择器
                sel = selector[1:].lower()
                class_selectors.append(sel)
            elif selector.startswith("#"):
                # id选择器
                sel = selector[1:].lower()
                id_selectors.append(sel)
            elif selector.startswith("[class*="):
                # 属性选择器
                # 例: [class*="promo"]
                m = re.match(r'\[class\*\s*=\s*["\'](.+?)["\']\]', selector)
                if m:
                    substr = m.group(1).lower()
                    class_wild_selectors.append(substr)
            elif selector.startswith("[style*="):
                # 属性选择器
                # 例: [style*="display:none"]
                m = re.match(r'\[style\*\s*=\s*["\'](.+?)["\']\]', selector)
                if m:
                    substr = m.group(1).lower()
                    style_wild_selectors.append(substr)

        # 将选择器编译成集合以提高查找效率
        self.class_selectors = set(class_selectors)
        self.id_selectors = set(id_selectors)
        
        # 将属性选择器编译成正则表达式
        pattern = '|'.join(re.escape(substr) for substr in class_wild_selectors)
        self.class_wild_selectors = re.compile(pattern, re.IGNORECASE)

        pattern = '|'.join(re.escape(substr) for substr in style_wild_selectors)
        self.style_wild_selectors = re.compile(pattern, re.IGNORECASE)

        self.MANUALLY_CLEANED = MANUALLY_CLEANED

    
    def check_selectors(self, node: Element) -> bool:
        tag_name = node.tag.lower()
        class_name = node.get("class", "")
        id_name = node.get("id", "")
        style_name = node.get("style", "")

        # 检查 class 选择器
        if class_name:
            class_list = {c.lower() for c in class_name.split()}
            if self.class_selectors & class_list:
                return True

        # 检查 id 选择器
        if id_name and id_name.lower() in self.id_selectors:
            return True

        # 检查属性选择器 [class*="..."]
        if class_name and self.class_wild_selectors.pattern:
            if self.class_wild_selectors.search(class_name):
                return True
        
        if style_name and self.style_wild_selectors.pattern:
            if self.style_wild_selectors.search(style_name):
                return True

        return False

    def _process(self, node: Element, manager: ContextManager):
        # if self.check_selectors(node): 这个有副作用，先不加
        tag_name = node.tag.lower()
        if tag_name in self.MANUALLY_CLEANED:
            remove_node(node, manager)
            return
        
        if not manager.need_comment and "comment" in node.get("class", ""):
            remove_node(node, manager)
            return