from lxml.html import HtmlElement
from haruka_parser.utils import text_strip
from haruka_parser.v2.manager import ContextManager
import logging
from lxml.html import Element, HtmlElement, HTMLParser, fromstring, tostring
from lxml.etree import _Element

# from haruka_parser.html_text import extract_text as node_to_text

from typing import Dict
from inscriptis import ParserConfig
from inscriptis.css_profiles import CSS_PROFILES
from inscriptis.html_engine import Inscriptis
from inscriptis.model.html_document_state import HtmlDocumentState
from inscriptis.model.tag import CustomHtmlTagHandlerMapping
from inscriptis.html_properties import Display, WhiteSpace
from inscriptis.model.html_element import HtmlElement as InscriptisHtmlElement
from haruka_parser.v2.config import DROP_TAGS, MANUALLY_CLEANED

def is_empty_element(node: HtmlElement):
    return not node.getchildren() and not node.text

def iter_node(element: HtmlElement, skip_drop: bool = True):
    yield element

    if skip_drop and element.tag in DROP_TAGS:
        return

    for sub_element in element:
        if isinstance(sub_element, HtmlElement) or isinstance(sub_element, _Element):
            if skip_drop and sub_element.tag in DROP_TAGS:
                continue
            yield from iter_node(sub_element, skip_drop)

def remove_node(node: HtmlElement, manager: ContextManager = None):
    parent = node.getparent()
    if text_strip(node.tail):
        previous = node.getprevious()
        if previous is None:
            if parent is not None:
                if text_strip(parent.text):
                    parent.text = "".join([parent.text, node.tail])
                else:
                    parent.text = node.tail
        else:
            if text_strip(previous.tail):
                previous.tail = "".join([previous.tail, node.tail])
            else:
                previous.tail = node.tail

    if parent is not None:
        parent.remove(node)
        node.tag = "drop"
        

def generate_unique_id(element: HtmlElement, manager: ContextManager):
    if manager.unique_id_offset > 0:
        logging.warning("Unique ID already generated")
        return
    
    for node in iter_node(element):
        l_tag = node.tag.lower()
        if l_tag not in ["html", "body"]:
            # node.attrib[manager.unique_id] = manager.get_next_unique_id()
            manager.set_unique_id(node)

def check_unique_id_exists(element: HtmlElement, manager: ContextManager):
    for node in iter_node(element):
        l_tag = node.tag.lower()
        if l_tag not in ["html", "body"]:
            # print(node.attrib.get(manager.unique_id, ""))
            if node.attrib.get(manager.unique_id, "") not in manager.unique_ids:
                print(f"{tostring(node)} has no unique id")
                logging.warning(f"{tostring(node)} has no unique id")

def create_new_element(tag: str, manager: ContextManager, **kwargs):
    new_element = Element(tag, **kwargs)
    # new_element.attrib[manager.unique_id] = manager.get_next_unique_id()
    manager.set_unique_id(new_element)
    return new_element

def replace_node(node: HtmlElement, new_node: HtmlElement, manager: ContextManager, tail=True):
    parent = node.getparent()
    if parent is None:
        return
    
    if tail and text_strip(node.tail):
        new_node.tail = node.tail
    parent.replace(node, new_node)

    node_unique_id = node.attrib.get(manager.unique_id, None)
    if node_unique_id in manager.link_list_unique_ids:
        for child_unique_id in iter_unique_ids(new_node, manager):
            manager.link_list_unique_ids.add(child_unique_id)
    
    for child in iter_node(node):
        child.tag = "drop"

def replace_node_with_element(text: str, node: HtmlElement, manager: ContextManager, element_type="code", tail=True):
    new_element = create_new_element(element_type, manager)
    new_element.text = text
    replace_node(node, new_element, manager, tail)
    return new_element

def html_tostring(element: HtmlElement):
    return tostring(element, encoding="unicode")

def _start_li(state: HtmlDocumentState, _: Dict) -> None:
    """Handle the <li> tag."""
    pass

CUSTOM_CSS_PROFILE = CSS_PROFILES["strict"].copy()
CUSTOM_CSS_PROFILE["code"] = InscriptisHtmlElement(display=Display.inline, whitespace=WhiteSpace.pre)

inscriptis_parser_config = ParserConfig(
        css=CUSTOM_CSS_PROFILE, 
        display_images=False,
        custom_html_tag_handler_mapping=CustomHtmlTagHandlerMapping(
            start_tag_mapping={
                "li": _start_li,
            },
            end_tag_mapping={}
        )
    )

def node_to_text_fast(node: HtmlElement, manager: ContextManager):
    texts = []
    unique_id = node.attrib.get(manager.unique_id, None)
    def _get_cache_text(node, manager):
        unique_id = node.attrib.get(manager.unique_id, None)
        if unique_id is not None:
            cache_text = manager.node_to_text_fast_cache.get(unique_id, None)
            if cache_text:
                return cache_text
        return None
    
    def _recurse(n):
        cache_text = _get_cache_text(n, manager)
        if cache_text:
            texts.append(cache_text)
            return
        
        if n.tag in MANUALLY_CLEANED:
            return
        if n.text:
            texts.append(n.text)
        for child in n:
            _recurse(child)
            if child.tail:
                texts.append(child.tail)
    _recurse(node)
    output_text = ''.join(texts)
    if unique_id:
        manager.node_to_text_fast_cache[unique_id] = output_text
    return output_text

def node_to_text(node: HtmlElement):
    return Inscriptis(
        node,
        inscriptis_parser_config,
    ).get_text()

def iter_unique_ids(element: HtmlElement, manager: ContextManager):
    unique_id = element.attrib.get(manager.unique_id, "")
    if unique_id:
        yield unique_id
    for node in iter_node(element):
        l_tag = node.tag.lower()
        if l_tag not in ["html", "body"]:
            unique_id = node.attrib.get(manager.unique_id, "")
            if unique_id:
                yield unique_id