# -*- coding:utf-8 -*-

import re
import logging
import traceback
from typing import Dict
from collections import defaultdict
from copy import deepcopy
from urllib.parse import unquote, urljoin
from lxml.etree import Comment, strip_elements
from lxml.html import HtmlElement
from haruka_parser.utils import text_strip
from lxml.etree import strip_tags
from haruka_parser.v2.utils.decode_html import read_html, load_html_tree
from haruka_parser.v2.config import MANUALLY_STRIPPED, CUT_EMPTY_ELEMS
from haruka_parser.v2.formatters.ftfy import FTFYFormatter
from haruka_parser.v2.utils.lxml import generate_unique_id, html_tostring, iter_node, remove_node, node_to_text

# from haruka_parser.trafilatura.trafilatura import extract
from haruka_parser.trafilatura.trafilatura.core import _internal_extraction
from haruka_parser.readablity_go import readablity_go_parse

class BaseExtractor:
    def __init__(self):
        self.ftfy_formatter = FTFYFormatter()
        self.ftfy = self.ftfy_formatter.format
        self.read_html = read_html
        self.generate_unique_id = generate_unique_id

    def _extract(self, html, **kwargs) -> Dict:
        raise NotImplementedError("Subclasses must implement this method")
    
    def extract(self, html, **kwargs) -> Dict:
        try:
            return self._extract(html, **kwargs)
        except:
            logging.error(f"Error in {self.__class__.__name__}: {traceback.format_exc()}")
        return None
    # def load_html(self, html, encoding="utf-8"):
    #     html = read_html(html, encoding)
    #     tree = load_html_tree(html)
    #     return tree
    
    # def extract(self, html, encoding="utf-8"):
    #     tree = self.load_html(html, encoding)
    #     return self.extract_tree(tree)

    def tokenize_html(self, html):
        return html

    def detokenize_html(self, html):
        return html

    def restore_html(self, html):
        return html

    def extract_tree(self, html):
        return load_html_tree(html)
    
    def clean_tree(self, tree):
        strip_tags(tree, MANUALLY_STRIPPED)
        for element in tree.xpath(".//*[not(node())]"):
            if element.tag in CUT_EMPTY_ELEMS:
                remove_node(element)

        # Linkdom 预处理
        for nav in tree.xpath('.//nav'):
            remove_node(nav)
    
    def get_base_url(self, tree, manager):
        base_href = tree.xpath("//base/@href")
        if base_href and "http" in base_href[0]:
            manager.base_url = base_href[0]

    def add_title(self, text, manager):
        if manager.add_title and manager.title:
            have_title = False
            first_lines = text.split(manager.separator)[:5]

            for line in first_lines:
                line = line.strip()
                if manager.title in line or line in manager.title:
                    have_title = True
                    break

            if not have_title:
                text = manager.title + manager.separator + text
        return text
    
    def collect_keep_ids(self, element: HtmlElement, keep_ids: set[str], unique_id_attr: str, ancestor_in_keep: bool = False):
        unique_id = element.get(unique_id_attr)
        in_keep = ancestor_in_keep or (unique_id in keep_ids)
        if in_keep and unique_id:
            keep_ids.add(unique_id)
        for child in element:
            self.collect_keep_ids(child, keep_ids, unique_id_attr, in_keep)
    
    def get_keep_ids(self, element: HtmlElement, manager):
        keep_ids = set()
        if element is not None:
            for elem in iter_node(element):
                unique_id = elem.get(manager.unique_id)
                if unique_id:
                    keep_ids.add(unique_id)
        return keep_ids
    
    def get_comment_keep_ids(self, element: HtmlElement, manager, filter_length: int = 10):
        keep_ids = set()
        if element is not None:
            for elem in iter_node(element):
                unique_id = elem.get(manager.unique_id)
                elem_text = node_to_text(elem).strip()
                if unique_id and len(elem_text) > filter_length:
                    keep_ids.add(unique_id)
        return keep_ids

    def trafilatura_parse(self, tree, manager):
        # keep_ids = set()
        # comment_keep_ids = set()
        trafilatura_output = _internal_extraction(tree, output_format="html", fast=True, include_links=True, include_images=True, include_comments=True, include_tables=True)
        # output_xml = trafilatura_output.text if trafilatura_output is not None else None
        # if not output_xml:
        #     return keep_ids
        # output_tree = self.extract_tree(output_xml)

        if trafilatura_output is None:
            return set(), set()

        keep_ids = self.get_keep_ids(trafilatura_output.body, manager)
        comment_keep_ids = self.get_comment_keep_ids(trafilatura_output.commentsbody, manager, filter_length=10)

        # for elem in iter_node(output_tree):
        #     unique_id = elem.get(manager.unique_id)
        #     if unique_id:
        #         keep_ids.add(unique_id)
        
        self.collect_keep_ids(tree, keep_ids, manager.unique_id)
        self.collect_keep_ids(tree, comment_keep_ids, manager.unique_id)
                
        # analyse
        # print(f"输出XML中发现的unique_id数量: {len(keep_ids)}")
        # print(f"unique_id列表: {sorted(keep_ids)}")
        # original_unique_ids = set()
        # for elem in tree.xpath(f'.//*[@{manager.unique_id}]'):
        #     unique_id = elem.get(manager.unique_id)
        #     if unique_id:
        #         original_unique_ids.add(unique_id)
        
        # print(f"原始树中的unique_id数量: {len(original_unique_ids)}")
        
        #         # 分析变化
        # retained_ids = keep_ids & original_unique_ids
        # lost_ids = original_unique_ids - keep_ids
        # new_ids = keep_ids - original_unique_ids
        
        # print(f"保留的unique_id数量: {len(retained_ids)}")
        # print(f"丢失的unique_id数量: {len(lost_ids)}")
        # print(f"新增的unique_id数量: {len(new_ids)}")

        return keep_ids, comment_keep_ids

    def readablity_parse(self, tree, manager):
        keep_ids = set()
        res_html = None
        meta = None
        try:
            data = readablity_go_parse(html_tostring(tree), manager.base_url)
            if data and not data["error"]:
                res_html = f'''<html><body>{data["html"]}</body></html>'''
                meta = data["metadata"]
        except:
            logging.error(f"Error in {self.__class__.__name__}: {traceback.format_exc()}")
        if not res_html:
            return set()
        
        output_tree = self.extract_tree(res_html)
        
        for elem in iter_node(output_tree):
            # if len(elem) == 0 or (elem.text and elem.text.strip()):
            unique_id = elem.get(manager.unique_id)
            if unique_id:
                keep_ids.add(unique_id)
        
        return keep_ids
    
    def merge_inline_code_blocks(self, text):
        # 1. 一行内多个 `code`，合并为多行代码块
        def inline_replacer(match):
            codes = re.findall(r'`([^`]+?)`', match.group())
            return '\n```\n' + '\n'.join(code.strip() for code in codes if code.strip()) + '\n```\n'
        # 只处理一行内有两个及以上 `code` 的情况
        text = re.sub(r'((?:`[^`]+?`\s*){2,})', inline_replacer, text)

        # 2. 多行，每行都是 `开头 `结尾，合并为多行代码块
        # 先找出所有连续的以 ` 开头、以 ` 结尾的行
        def multiline_replacer(match):
            lines = match.group().strip().splitlines()
            codes = [re.sub(r'^`\s*|\s*`$', '', line).strip() for line in lines]
            return '```\n' + '\n'.join(codes) + '\n```'
        # 匹配连续的以 ` 开头、以 ` 结尾的行（2行及以上）
        text = re.sub(r'((?:^\s*`[^`]+?`\s*$\n?){2,})', multiline_replacer, text, flags=re.MULTILINE)

        return text

    
    def text_finalize(self, text, manager):
        text = manager.clear_unique_tags(text)

        text = self.merge_inline_code_blocks(text)
        

        text = text.rstrip()

        return text
