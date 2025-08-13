import re
import os
import traceback
import html
from haruka_parser.utils import text_strip
from haruka_parser.v2.doms.base_dom import BaseDom
from lxml.html import Element, HtmlElement, HTMLParser, fromstring, tostring
from urllib.parse import unquote, urljoin
import logging
from lxml import etree
from copy import deepcopy
import json

from haruka_parser.v2.utils.lxml import remove_node, create_new_element, replace_node_with_element, node_to_text
from haruka_parser.v2.manager import ContextManager

from haruka_parser.mathml2latex.mathml2latex import mathml2latex, unicode2latex

def _translator():
    old_log_level = logging.getLogger().level
    try:
        import py_asciimath.translator.translator as _translator
        return _translator
    finally:
        logging.getLogger().setLevel(old_log_level)

def ASCIIMath2Tex(*args, **kwargs):
    return _translator().ASCIIMath2Tex(*args, **kwargs)

def MathML2Tex(*args, **kwargs):
    return _translator().MathML2Tex(*args, **kwargs)

class MathDom(BaseDom):
    def __init__(self):
        super().__init__()
        self.color_regex = re.compile(r"\\textcolor\[.*?\]\{.*?\}")
        self.dollar_regex = re.compile(r'(?<!\\)\$')
        self.latex_image_class_names = [
            "latexcenter", "latex", "tex", "latexdisplay", 
            "latexblock", "latexblockcenter"
        ]
        self.asciimath2tex = ASCIIMath2Tex(log=False)

        cur_file = os.path.abspath(__file__)
        xsl_path = os.path.join(os.path.dirname(cur_file), "../..", "mmltex/mmltex.xsl")
        xslt = etree.parse(xsl_path)
        self.mathml_transform = etree.XSLT(xslt)
    
    def retry_normalize(self, s, max_retries=10):
        last_s = s
        for _ in range(max_retries):
            s = unquote(s)
            s = html.unescape(s)
            if last_s == s:
                break
            last_s = s
        return s

    def decode_latex(self, s):
        try:
            s = json.loads(s)["string"]
        except:
            pass
        return self.retry_normalize(s.replace(r"\&quot;", "").replace("&quot;", ""))

    def extract_asciimath(self, s):
        parsed = self.asciimath2tex.translate(s)
        return parsed
    
    def remove_math_styles(self, latex_text):
        """移除LaTeX中的显示样式"""
        if "display" not in latex_text and "textstyle" not in latex_text:
            return latex_text

        pattern = r"\$\{?(\\(?:display|text)style)\s*(.+?)\}?\$"

        def replace_func(match):
            content = match.group(2)
            content = re.sub(r"^\{(.+)\}$", r"\1", content)
            return f"${content}$"

        cleaned_text = re.sub(pattern, replace_func, latex_text)
        return cleaned_text

    def clean_latex(self, latex_text):
        """清理LaTeX文本"""
        latex_text = latex_text.strip()
        if latex_text.startswith("{\\displaystyle"):
            latex_text = latex_text.replace("{\\displaystyle", "")
            if latex_text.endswith("}"):
                latex_text = latex_text[:-1]
        if latex_text.strip() == "":
            return ""
        return f"${latex_text.strip()}$"

    def clean_mathml(self, mathml_block):
        """清理MathML代码"""
        if "oldsymbol{" in mathml_block and "boldsymbol{" not in mathml_block:
            mathml_block = mathml_block.replace("oldsymbol", "\\boldsymbol")
        mathml_block = re.sub(r"<\?xml[^>]+\?>\s*", "", mathml_block)
        if 'xmlns="http://www.w3.org/1998/Math/MathML"' not in mathml_block:
            mathml_block = mathml_block.replace(
                "<math", '<math xmlns="http://www.w3.org/1998/Math/MathML"', 1
            )
        return mathml_block
    
    def wrap_math(self, s, display=False):
        s = re.sub(r"\s+", " ", s)
        s = self.color_regex.sub("", s)
        s = self.dollar_regex.sub("", s)
        s = s.replace("\n", " ").replace("\\n", "")
        s = s.strip()
        if len(s) == 0:
            return s
        # Don't wrap if it's already in \align
        if "align" in s:
            return s
        if display:
            return "$$" + s + "$$"
        return "$" + s + "$"

    def old_mml_to_latex(self, mml_code):
        # Remove any attributes from the math tag
        mml_code = re.sub(r"(<math.*?>)", r"\1", mml_code)
        mml_ns = mml_code.replace(
            "<math>", '<math xmlns="http://www.w3.org/1998/Math/MathML">'
        )
        
        mml_ns = mml_ns.replace("&quot;", '"')
        mml_ns = mml_ns.replace("'\\\"", '"').replace("\\\"'", '"')
        
        # 修复引号问题
        pattern = r'"([^"]+?)\''
        mml_ns = re.sub(pattern, r'"\1"', mml_ns)
        
        mml_dom = etree.fromstring(mml_ns)
        mmldom = self.mathml_transform(mml_dom)
        latex_code = str(mmldom)
        return latex_code
    
    def mml_to_latex(self, mathml_str):
        try:
            mathml_str = self.clean_mathml(mathml_str)
            latex_block = mathml2latex(mathml_str)
            latex_text = unicode2latex(latex_block)
            latex_text = self.remove_math_styles(latex_text)
            return latex_text
        except:
            return self.old_mml_to_latex(mathml_str)

    def replace_with_math_span(self, node, text, display=False, manager=None):
        """用数学公式span替换节点"""
        text = self.decode_latex(text)
        wrapped_text = self.wrap_math(text, display=display)
        new_span = replace_node_with_element(wrapped_text, node, manager, "code")
        manager.add_dom_meta(new_span, "math", {"text": wrapped_text, "display": display}, old_node=node)
        return new_span

    def parse_katex_html(self, element):
        """递归解析 KaTeX HTML 结构，精准提取上下标"""
        text = ""
        
        # 获取子节点 - 使用lxml的方式
        children = list(element)
        for child in children:
            if child.tag != "span":
                continue

            classes = child.get("class", "").split() if child.get("class") else []
            if "mord" in classes:  # mo character (e.g. F)
                child_text = self.parse_katex_html(child)
                if not child_text and child.text:
                    child_text = child.text
                text += child_text or ""
            elif "msupsub" in classes:  # sup/sub container
                subscript = ""
                # 查找包含下标内容的vlist结构
                vlist_t_nodes = child.xpath('.//span[@class="vlist-t"]')
                if vlist_t_nodes:
                    vlist_t = vlist_t_nodes[0]
                    vlist_r_nodes = vlist_t.xpath('.//span[contains(@class, "vlist-r")]')
                    for vlist_r in vlist_r_nodes:
                        vlist_nodes = vlist_r.xpath('.//span[contains(@class, "vlist")]')
                        for vlist in vlist_nodes:
                            # 提取所有大小层中的内容
                            sizing_nodes = vlist.xpath('.//span[contains(@class, "sizing")]')
                            for sizing in sizing_nodes:
                                subscript += self.parse_katex_html(sizing)
                
                # 过滤零宽空格并连接下标
                subscript = subscript.replace("​", "")  # 移除Unicode零宽空格
                if subscript:
                    text += f"_{{{subscript}}}"
            else:
                # 递归处理其他嵌套结构
                text += self.parse_katex_html(child)

        # 优先使用子节点的内容，然后是自身的文本
        if not text.strip() and element.text:
            text = element.text.strip()
        
        return text

    def process_katex_container(self, katex_elem, manager):
        """处理KaTeX容器"""
        # 首先尝试处理mathml
        mathml_nodes = katex_elem.xpath('.//span[@class="katex-mathml"]/math')
        if mathml_nodes:
            mathml_elem = mathml_nodes[0]
            # 提取LaTeX
            try:
                latex = self.extract_latex_from_mathml(mathml_elem)
                if latex:
                    self.replace_with_math_span(katex_elem, latex, manager=manager)
                    manager.math_stats["katex_mathml"] += 1
                    return True
            except:
                pass

        # 处理katex-html
        html_katex_nodes = katex_elem.xpath('.//span[@class="katex-html"]')
        for html_katex in html_katex_nodes:
            math_text = self.parse_katex_html(html_katex)
            math_text = math_text.replace("\u200b", " ")  # 移除零宽空格

            if math_text.strip():
                self.replace_with_math_span(katex_elem, math_text, manager=manager)
                manager.math_stats["katex_html"] += 1
                return True
        
        return False

    def process_math_html_entities(self, node, manager):
        """处理数学HTML实体和标签"""
        # 处理sup和sub标签
        if node.tag == "sup":
            if node.text and not node.text.startswith("^{"):
                node.text = f"^{{{node.text}}}"
        elif node.tag == "sub":
            if node.text and not node.text.startswith("_{"):
                node.text = f"_{{{node.text}}}"

        # 处理分数 <span class="intbl">
        if node.tag == "span" and "intbl" in node.get("class", ""):
            numerator_nodes = node.xpath('.//em')
            denominator_nodes = node.xpath('.//strong')
            
            if numerator_nodes and denominator_nodes:
                numerator = numerator_nodes[0].text or ""
                denominator = denominator_nodes[0].text or ""
                if numerator and denominator:
                    fraction_latex = f"\\frac{{{numerator}}}{{{denominator}}}"
                    self.replace_with_math_span(node, fraction_latex, manager=manager)
                    manager.math_stats["html_fraction"] += 1
                    return True
        
        return False

    def process_tex_math(self, node, manager) -> bool:
        """处理tex错误元素"""
        if "texerror" not in node.get("class", "").lower():
            return False
        
        # 查找{}中的文本内容（最大长度匹配）并替换texerror
        node_text = node_to_text(node)
        match = re.search(r"\{(.{1,})\}", node_text)
        if match:
            latex = match.group(1)
            if text_strip(latex):
                manager.math_stats["texerror"] += 1
                self.replace_with_math_span(node, latex, manager=manager)
                return True
        return False

    def process_math_images(self, node, manager):
        """处理包含数学公式的图片"""
        if node.tag != "img":
            return False
        
        node_class = node.get("class", "")
        src = node.get("src", "")
        
        # 处理特定class的图片
        if node_class:
            class_list = node_class.split(" ")
            if any(img_class in class_list for img_class in self.latex_image_class_names):
                alt = node.get("alt")
                if text_strip(alt):
                    self.replace_with_math_span(node, alt, manager=manager)
                    manager.math_stats["img_math"] += 1
                    return True
        
        # 处理各种数学公式图片服务
        if src:
            success = self._process_math_image_sources(node, src, manager)
            if success:
                return True

        for latex_signal in ["tex", "latex"]:
            try:
                # they usually have "alt='-i u_t + &#92;Delta u = |u|^2 u'"
                alt = node.getattr(latex_signal)
                if text_strip(alt):
                    self.replace_with_math_span(node, alt, manager=manager)
                    manager.math_stats["other_latex_img"] += 1
                    return True
            except:
                pass
        
        # 处理特殊class
        if node_class and "x-ck12" in node_class:
            try:
                latex = node.get("alt")
                if text_strip(latex):
                    self.replace_with_math_span(node, latex, manager=manager)
                    manager.math_stats["x-ck12"] += 1
                    return True
            except:
                pass
        
        return False

    def _process_math_image_sources(self, node, src, manager):
        """处理各种数学公式图片源"""

        # codecogs.com
        if "codecogs.com" in src:
            try:
                latex = src.split("?")[1:]
                latex = "?".join(latex)
                if text_strip(latex):
                    self.replace_with_math_span(node, latex, manager=manager)
                    manager.math_stats["codecogs_latex"] += 1
                    return True
            except:
                pass
        
        # latex.php
        if "latex.php" in src:
            try:
                alt = node.get("alt")
                if text_strip(alt):
                    self.replace_with_math_span(node, alt, manager=manager)
                    manager.math_stats["wp_latex"] += 1
                    return True
            except:
                pass
        
        # /images/math/codecogs
        if "/images/math/codecogs" in src:
            try:
                alt = node.get("alt")
                if text_strip(alt):
                    self.replace_with_math_span(node, alt, manager=manager)
                    manager.math_stats["other_latex_img"] += 1
                    return True
            except:
                pass
        
        # mimetex.cgi
        if "mimetex.cgi" in src:
            try:
                latex = src.split("?")[1:]
                latex = "?".join(latex)
                if text_strip(latex):
                    self.replace_with_math_span(node, latex, manager=manager)
                    manager.math_stats["mimetex_cgi"] += 1
                    return True
            except:
                pass
        
        # mathtex.cgi
        if "mathtex.cgi" in src:
            try:
                latex = src.split("?")[1:]
                latex = "?".join(latex)
                if text_strip(latex):
                    self.replace_with_math_span(node, latex, manager=manager)
                    manager.math_stats["mathtex_cgi"] += 1
                    return True
            except:
                pass
        
        # 通用latex信号处理
        else:
            for latex_signal in ["tex?", "?latex=", "?tex="]:
                if latex_signal in src:
                    try:
                        latex = src.split(latex_signal, 1)[1]
                        if text_strip(latex):
                            self.replace_with_math_span(node, latex, manager=manager)
                            manager.math_stats["other_latex_img"] += 1
                            return True
                    except:
                        pass
        
        return False

    def process_math_containers(self, node, manager) -> bool:
        """处理各种数学容器"""
        node_class = node.get("class", "").strip()
        
        # katex容器
        if node_class == "katex":
            success = self.process_katex_container(node, manager)
            if success:
                return True
        
        # math-container
        if node_class.startswith("math-container"):
            try:
                text = node_to_text(node)
                if text_strip(text):
                    self.replace_with_math_span(node, text, display=True, manager=manager)
                    manager.math_stats["math-container"] += 1
                    return True
            except:
                pass
        
        # wp-katex-eq
        elif node_class.startswith("wp-katex-eq"):
            try:
                text = node_to_text(node)
                if text_strip(text):
                    display_attr = node.get("data-display")
                    display = display_attr == "true" if display_attr else False
                    self.replace_with_math_span(node, text, display=display, manager=manager)
                    manager.math_stats["wp-katex-eq"] += 1
                    return True
            except:
                pass
        
        # tex class
        elif node_class == "tex":
            try:
                expr = node.get("data-expr")
                if text_strip(expr):
                    self.replace_with_math_span(node, expr, manager=manager)
                    manager.math_stats["katex"] += 1
                    return True
            except:
                pass
        
        # x-ck12-mathEditor
        elif node_class and "x-ck12" in node_class.lower():
            try:
                expr = node.get("data-tex")
                if text_strip(expr):
                    self.replace_with_math_span(node, expr, manager=manager)
                    manager.math_stats["katex"] += 1
                    return True
            except:
                pass
        
        return False

    def process_script_math(self, node, manager) -> bool:
        """处理script标签中的数学公式"""
        if node.tag != "script":
            return False
        
        script_type = node.get("type", "").lower()
        display = "display" in script_type
        
        # math/tex
        if "math/tex" in script_type:
            try:
                text = node_to_text(node)
                if text_strip(text):
                    self.replace_with_math_span(node, text, display=display, manager=manager)
                    manager.math_stats["script_math_tex"] += 1
                    return True
            except:
                remove_node(node, manager)
        
        # math/asciimath
        elif "math/asciimath" in script_type:
            try:
                text = node_to_text(node)
                if text_strip(text):
                    translated_text = self.extract_asciimath(text)
                    self.replace_with_math_span(node, translated_text, display=display, manager=manager)
                    manager.math_stats["script_math_asciimath"] += 1
                    return True
            except:
                remove_node(node, manager)
        
        # math/mml
        elif "math/mml" in script_type:
            try:
                mathml = node_to_text(node)
                if text_strip(mathml):
                    mathml = self.decode_latex(mathml)
                    if "xmlns:mml" in mathml:
                        mathml = mathml.replace("mml:", "")
                        # replace xmlns:mml="..." with nothing
                        mathml = re.sub(r'xmlns:mml=".*?"', "", mathml)
                    latex = self.mml_to_latex(mathml)
                    if text_strip(latex):
                        self.replace_with_math_span(node, latex, display=display, manager=manager)
                        manager.math_stats["mathml"] += 1
                        return True
            except:
                remove_node(node, manager)
        return False

    def process_math_attributes(self, node, manager) -> bool:
        """处理包含数学公式属性的元素"""
        # 处理各种tex属性
        for tex_attr in ["tex", "data-tex", "data-formula", "data-expr"]:
            try:
                tex_value = node.get(tex_attr)
                if text_strip(tex_value):
                    self.replace_with_math_span(node, tex_value, manager=manager)
                    manager.math_stats["katex"] += 1
                    return True
            except:
                pass
        
        # 处理mathml属性
        for mathml_attr in ["mathml", "data-mathml"]:
            mathml_value = node.get(mathml_attr)
            if text_strip(mathml_value):
                try:
                    mathml = self.decode_latex(mathml_value)
                    if "xmlns:mml" in mathml:
                        mathml = mathml.replace("mml:", "")
                        mathml = re.sub(r'xmlns:mml=".*?"', "", mathml)
                    latex = self.mml_to_latex(mathml)
                    if text_strip(latex):
                        self.replace_with_math_span(node, latex, manager=manager)
                        manager.math_stats["mathml"] += 1
                        return True
                except:
                    pass
        
        return False
        
    def process_formula_tags(self, node, manager) -> bool:
        """处理formula标签"""
        if node.tag != "formula":
            return False
        
        if "math" in node.get("class", "").lower():
            expr = node_to_text(node)
            if text_strip(expr):
                self.replace_with_math_span(node, expr, manager=manager)
                manager.math_stats["formula"] += 1
                return True
        
        return False

    def process_math_tags(self, node, manager):
        """处理math标签"""
        if node.tag != "math":
            return False
        
        parent = node.getparent()
        
        # 首先尝试annotation标签
        annotation_tags = node.xpath('.//annotation[@encoding="application/x-tex"]')
        if annotation_tags:
            annotation_tag = annotation_tags[0]
            text = node_to_text(annotation_tag)
            if text_strip(text):
                self.replace_with_math_span(node, text, manager=manager)
                manager.math_stats["math_annotations"] += 1
                
                # 处理父元素的display:none样式
                if parent is not None:
                    style_value = parent.get("style")
                    if style_value:
                        normalized_style = style_value.lower().strip().replace(" ", "").replace(";", "")
                        if "display:none" in normalized_style:
                            parent.set("style", "")
                
                return True
        
        # 尝试alttext属性
        alttext = node.get("alttext") or node.get("data-code")
        if text_strip(alttext):
            alttext = self.decode_latex(alttext)
            
            # 根据数学语言类型处理
            math_lang = node.get("data-math-language")
            if math_lang == "asciimath":
                try:
                    alttext = self.extract_asciimath(alttext)
                except:
                    pass
            elif math_lang == "mathml":
                try:
                    alttext = self.mml_to_latex(alttext)
                except:
                    pass
            if text_strip(alttext):
                self.replace_with_math_span(node, alttext, manager=manager)
                manager.math_stats["math_alttext"] += 1
                return True
        
        # 最后尝试MathML转换
        try:
            tmp_node = deepcopy(node)
            tmp_node.tail = None
            mathml = tostring(tmp_node, encoding=str)
            
            if "xmlns:mml" in mathml:
                mathml = mathml.replace("mml:", "")
                mathml = re.sub(r'xmlns:mml=".*?"', "", mathml)
            
            latex = self.mml_to_latex(mathml)
            if text_strip(latex):
                self.replace_with_math_span(node, latex, manager=manager)
                manager.math_stats["mathml"] += 1
                return True
        except:
            remove_node(node, manager)
        
        return False

    def process_mathjax_elements(self, node, manager):
        """处理MathJax相关元素"""
        if node.tag == "mathjax":
            try:
                text = node_to_text(node)
                if text_strip(text):
                    text = self.decode_latex(text)
                    # 处理#包围的asciimath
                    def replace_asciimath(match):
                        try:
                            latex = self.extract_asciimath(match.group(1))
                            return latex
                        except:
                            return match.group(1)
                    
                    text = re.sub(r"#(.+?)#", replace_asciimath, text)
                    
                    self.replace_with_math_span(node, text, manager=manager)
                    manager.math_stats["mathjax"] += 1
                    return True
            except:
                pass
        
        return False

    def _process(self, node: Element, manager: ContextManager):
        """主处理函数"""
        node_class = node.get("class", "")
        if "jax_ignore" in node_class.lower():
            remove_node(node, manager)
            return
          
        # 移除katex的mathml部分（避免重复处理）
        if node.tag == "span" and node_class == "katex-mathml":
            return  # 跳过katex-mathml，在katex容器中统一处理
        
        # 处理katex容器
        if node.tag == "span" and node_class == "katex":
            katex_html_spans = node.xpath('.//span[@class="katex-html"]')
            for katex_html_span in katex_html_spans:
                remove_node(katex_html_span, manager)
        
        # 移除MathJax预览
        if node.tag == "span" and node_class == "MathJax_Preview":
            remove_node(node, manager)
        
        # 处理m:math标签
        if node.tag and (node.tag.startswith("m:") or node.tag.startswith("mml:")):
            node.tag = node.tag.split(":", 1)[1]
        # 按类型处理数学公式
        for process_func in [
            self.process_math_html_entities,
            self.process_tex_math,
            self.process_math_images,
            self.process_math_containers,
            self.process_script_math,
            self.process_math_attributes,
            self.process_formula_tags,
            self.process_math_tags,
            self.process_mathjax_elements,
        ]:
            try:
                success = process_func(node, manager)
                if success:
                    break
            except:
                logging.error(f"process_func: {process_func.__name__} failed, error: {traceback.format_exc()}")