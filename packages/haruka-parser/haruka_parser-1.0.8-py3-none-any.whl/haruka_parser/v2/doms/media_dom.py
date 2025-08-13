from haruka_parser.v2.manager import ContextManager
from haruka_parser.v2.utils.lxml import replace_node_with_element, node_to_text
from urllib.parse import unquote, urljoin
from lxml.html import Element, etree
from copy import deepcopy
from haruka_parser.v2.doms.base_dom import BaseDom

class MediaDom(BaseDom):
    def __init__(self):
        self.xpath = "//svg | //img | //video | //audio"
        self.IMG_SRC_ATTR = [
            "data-src",
            "data-src-fg",
            "data-scroll-image",
            "srcset",
            "data-lateloadsrc",
            "data-img-src",
            "data-original",
            "data-gt-lazy-src",
            "data-lazy",
            "data-lazy-src",
            "src2",
            "src", # 如果没有 lazy 属性，再考虑使用 src
        ]

    def _process(self, node: Element, manager: ContextManager):

        node_attributes = deepcopy(node.attrib)
        node_tag = node.tag
        src = None

        if node_tag == "img":
            fallback_src = ""
            # Check all possible source type, and keep the first valid one
            for source_type in self.IMG_SRC_ATTR:
                if source_type in node_attributes and node_attributes[source_type]:
                    if len(fallback_src) < len(node_attributes[source_type]):
                        fallback_src = node_attributes[source_type]
                    if ("," not in node_attributes[source_type]) and (" " not in node_attributes[source_type]):
                        src = node_attributes[source_type]
                        break
            
            if not src and fallback_src:
                src = fallback_src

        elif node_tag == "video":
            if ("src" in node_attributes) and node_attributes["src"]:
                src = node_attributes["src"]
            else:
                for cnode in node.iterchildren():
                    if not src:
                        if cnode.tag == "source":
                            cnode_attributes = cnode.attrib
                            if ("src" in cnode_attributes) and cnode_attributes["src"]:
                                src = cnode_attributes["src"]

        elif node_tag == "audio":
            if ("src" in node_attributes) and node_attributes["src"]:
                src = node_attributes["src"]
            else:
                for cnode in node.iterchildren():
                    if not src:
                        if cnode.tag == "source":
                            cnode_attributes = cnode.attrib
                            if ("src" in cnode_attributes) and cnode_attributes["src"]:
                                src = cnode_attributes["src"]
        elif node_tag == "svg":
            svg_html = etree.tostring(node, method="html", encoding="utf-8").decode()
            new_element = replace_node_with_element(manager.get_unique_tag("svg"), node, manager, "code")
            manager.add_dom_meta(new_element, node_tag, {
                "data": svg_html,
            }, old_node=node)
            return
        else:
            return  # TODO iframes

        if not src:
            src = node.attrib.get("src", "")
        
        src = src.strip()

        if src and manager.base_url:
            src = urljoin(manager.base_url, src)

        if node_tag in ["img", "video", "audio"]:
            node_attributes.pop(manager.unique_id, None)

            new_element = replace_node_with_element(manager.get_unique_tag(node_tag), node, manager, "code")

            manager.add_dom_meta(new_element, node_tag, {
                "caption": node.attrib.get("alt", ""),
                "url": src,
                "meta": node_attributes, # use original attributes,
                "tail_text": new_element.tail if new_element.tail else "",
            }, old_node=node)

            return
            