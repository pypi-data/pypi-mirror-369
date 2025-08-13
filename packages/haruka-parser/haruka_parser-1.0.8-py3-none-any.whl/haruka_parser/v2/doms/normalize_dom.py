from haruka_parser.v2.manager import ContextManager
from urllib.parse import unquote, urljoin
from lxml.html import Element
from haruka_parser.v2.utils.lxml import remove_node, node_to_text
from haruka_parser.v2.doms.base_dom import BaseDom

class NormalizeDom(BaseDom):
    def __init__(self):
        self.NORMALIZE_ATTR = {
            # "frameset",
            # "template",
        }

    def _process(self, node: Element, manager: ContextManager):
        if node.tag.lower() in self.NORMALIZE_ATTR:
            node.tag = "div"
        
        if node.tag.lower() == "div" and not node.getchildren():
            node.tag = "p"

        if node.tag.lower() == "figure":
            # 使用xpath查找所有img子元素
            img_nodes = node.xpath('.//img')
            if len(img_nodes) == 1:
                img_node = img_nodes[0]
                manager.add_dom_meta(img_node, "img", {
                    "figure_text": node_to_text(node),
                })
            node.tag = "div"