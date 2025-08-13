import re
from html import unescape
from typing import List, Set, Optional
from lxml.html import HtmlElement
from haruka_parser.v2.utils.lxml import node_to_text
import html
from urllib.parse import unquote
from difflib import SequenceMatcher
from haruka_parser.v2.manager import ContextManager

# META标签XPath表达式
METAS_XPATH = '//meta[starts-with(@property, "og:title") or starts-with(@name, "og:title") or starts-with(@property, "title") or starts-with(@name, "title") or starts-with(@property, "page:title") or starts-with(@name, "page:title")]/@content'

def _normalize(s):
    s = unquote(s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def norm_title(s, max_retries=10) -> str:
    last_s = s
    for _ in range(max_retries):
        s = _normalize(s)
        if last_s == s:
            break
        last_s = s
    return s


def lcs_of_2(a, b):
    if a in b:
        return a
    if b in a:
        return b
    
    return None


def similarity2(s1, s2):
    if not s1 or not s2:
        return 0
    s1_set = set(list(s1))
    s2_set = set(list(s2))
    intersection = s1_set.intersection(s2_set)
    union = s1_set.union(s2_set)
    return len(intersection) / len(union)

class TitleExtractor:
    """针对lxml节点的HTML标题提取器"""
    
    def __init__(self):
        self.fallback_tags = set(["title", "head", "heading", "pagetitle", "newstitle", "contentheading", "small_header_red"])
    
    
    def extract_by_meta(self, element: HtmlElement):
        titles = element.xpath(METAS_XPATH)
        if titles and len(titles):
            return titles[0]
    
    def extract_by_title(self, element: HtmlElement):
        return "".join(element.xpath("//title//text()")).strip()
    
    def extract_by_hs(self, element: HtmlElement):
        hs = element.xpath("//h1//text()|//h2//text()|//h3//text()")
        return hs or []
    
    def extract_by_h(self, element: HtmlElement):
        for xpath in ["//h1", "//h2", "//h3"]:
            children = element.xpath(xpath)
            if not children:
                continue
            child = children[0]
            texts = child.xpath("./text()")
            if texts and len(texts):
                return texts[0].strip()
    
    def get_title(self, element: HtmlElement):
        title_extracted_by_meta = self.extract_by_meta(element)
        if title_extracted_by_meta:
            return title_extracted_by_meta
        title_extracted_by_h = self.extract_by_h(element)
        title_extracted_by_hs = self.extract_by_hs(element)
        title_extracted_by_title = self.extract_by_title(element)
        title_extracted_by_hs = sorted(
            title_extracted_by_hs,
            key=lambda x: similarity2(x, title_extracted_by_title),
            reverse=True,
        )
        if title_extracted_by_hs:
            title = lcs_of_2(title_extracted_by_hs[0], title_extracted_by_title)
            if title:
                return title
        
        candidates = []
        if title_extracted_by_title:
            candidates.append(title_extracted_by_title)
        if title_extracted_by_h:
            candidates.append(title_extracted_by_h)
        
        if candidates:
            return max(candidates, key=len)
        
        return None

    def process(self, element: HtmlElement, manager: ContextManager):
        if manager.title:
            return
        title = self.get_title(element)
        if title:
            title = norm_title(title)
            manager.title = title
    
    def split_name(self, name):
        """按照空格、下划线、中划线分割名称"""
        # 使用正则表达式按照空格、下划线、中划线分割
        parts = re.split(r'[\s_-]+', name)
        # 过滤掉空字符串
        return [part for part in parts if part.strip()] + [name]

    def fallback_process(self, element: HtmlElement, manager: ContextManager):
        if manager.title:
            return
        class_name = element.get("class", "").lower()
        id_name = element.get("id", "").lower()
        element_tag = set()
        for tag in [class_name, id_name]:
            for name in self.split_name(tag):
                if name:
                    element_tag.add(name)
        
        if element_tag & self.fallback_tags:
            title = node_to_text(element)
            title = norm_title(title)
            if title:
                manager.title = title
