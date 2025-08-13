from haruka_parser.v2.manager import ContextManager
from lxml.html import Element
from haruka_parser.v2.utils.lxml import replace_node_with_element, iter_node, node_to_text, remove_node
from haruka_parser.utils import extract_code_languages, str_contains
import re
from haruka_parser.v2.doms.base_dom import BaseDom

class CodeDom(BaseDom):
    def __init__(self):
        self.check_code = re.compile(
            r'[\(\)\{\}\[\];]'           # 括号和分号
            r'|^\s{4,}'                  # 行首缩进（4个及以上空格）
            r'|\b(def|class|if|for|while|return|function)\b',  # 关键字
            re.MULTILINE
        )
    
    def preprocess(self, html, tree, manager):
        have_crayon = False
        if "crayon-table" in html:
            cryan_tables = tree.xpath('//table[@class="crayon-table"]')
            if cryan_tables:
                for table in cryan_tables:
                    remove_node(table, manager)
                    have_crayon = True


        for textarea in tree.xpath('//textarea'):
            if have_crayon or (textarea.text and self.check_code.search(textarea.text) is not None):
                textarea.tag = "pre"

    def _process(self, node: Element, manager: ContextManager):
        
        tag_name = node.tag.lower()
        class_name = node.get("class", "").lower()
        if not (str_contains(class_name, ["wp_syntax", "code_responsive", "language-", "codeblock", "code_block"]) or tag_name in ["pre", "code"]):
            return
        
        if node.xpath(
            ".//*[not(self::pre or self::code or self::span or self::b or self::br or self::strong or self::i or self::em or self::a or self::mark or self::kbd or self::samp or self::var)][1]"
        ):
            return
        
        code_text = node_to_text(node).lstrip("\n").rstrip()
        dom_meta = manager.get_dom_meta(node)
        multiline = code_text.count("\n") > 0
        # have_code = self.check_code.search(code_text) is not None
        have_code = True # 检查可能导致非预期格式，例如 fandom.0001.html，连续 pre 会在最后文本处理时自动合并成大的 code block
        
        # or (manager.unique_id in code_text)
        if (dom_meta and dom_meta.type != "code") or (not multiline and not have_code):
            return
        
        cur_code_languages = []
        for child in iter_node(node, skip_drop=True):
            sub_code_languages = extract_code_languages(child.get("class", "").lower())
            cur_code_languages.extend(sub_code_languages)
        
        cur_code_languages = sorted(list(set(filter(lambda x: x, cur_code_languages))), key=len, reverse=True)
        
        for cur_code_language in cur_code_languages:
            manager.code_languages.add(cur_code_language)

        cur_code_language_text = ""
        if cur_code_languages:
            cur_code_language_text = cur_code_languages[0]

        if len(code_text) > 0:
            manager.code_block += 1
            manager.code_line += code_text.count("\n") + 1
            manager.code_length += len(code_text)
            if manager.enable_code:
                if multiline:
                    code_text = f"```{cur_code_language_text}\n{code_text}\n```"
                else:
                    code_text = f"`{code_text}`"
                new_element = replace_node_with_element(code_text, node, manager, "pre" if multiline else "code")
                manager.add_dom_meta(new_element, "code", {
                    "text": code_text,
                    "languages": cur_code_languages
                }, old_node=node)

        