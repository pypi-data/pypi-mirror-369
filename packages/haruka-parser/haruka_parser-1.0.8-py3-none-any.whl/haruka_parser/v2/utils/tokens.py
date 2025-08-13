import re

class Token:
    def __init__(self, token: str, replacement: str):
        self.token = token
        self.replacement = replacement

    def __str__(self):
        return self.token

    def __repr__(self):
        return f"Token({self.token!r}, {self.replacement!r})"

class SpecialTokens:
    
    BR_TAG = Token("[br_tag]", "\n")
    EXTRACT_ITEX = Token("[extract_itex]", "$")
    EXTRACT_ITEX_END = Token("[/extract_itex]", "$")
    EXTRACT_TEX = Token("[extract_tex]", "$$")
    EXTRACT_TEX_END = Token("[/extract_tex]", "$$")
    EXTRACT_SINGLE_DOLLAR = Token("[extract_single_dollar]", "$")
    EXTRACT_SINGLE_CHAPTER = Token("[extract_single_chapter]", "§")
    THREE_CODE_DOT = Token("[three_code_dot]", "```")
    SINGLE_CODE_DOT = Token("[single_code_dot]", "`")
    ITEX = Token("[itex]", "$")
    ITEX_END = Token("[/itex]", "$")
    MATH = Token("[math]", "")
    MATH_END = Token("[/math]", "")
    HARUKA_PARSER_BS = Token("[HARUKA_PARSER_BS]", " ")
    HARUKA_PARSER_CHANGE_LINE = Token("[HARUKA_PARSER_CHANGE_LINE]", "\n")

    def __init__(self):
        self.register_tokens = set()

        for token in self.__class__.__dict__.values():
            if isinstance(token, Token):
                self.register_tokens.add(token)
    
    def register(self, token):
        self.register_tokens.add(token)

    def extract_image_tag(self, idx):
        image_token = Token(f"[extract_image_tag_{idx}]", "")
        self.register(image_token)
        return image_token.token

    @classmethod
    def tokenize_html(cls, html):
        html = re.sub(r"<\s*br\s*/?\s*>", cls.BR_TAG.token, html, flags=re.IGNORECASE)
        html = html.replace("$", cls.EXTRACT_SINGLE_DOLLAR.token)
        html = html.replace("§", cls.EXTRACT_SINGLE_CHAPTER.token)
        html = html.replace("```", cls.THREE_CODE_DOT.token)
        html = html.replace("`", cls.SINGLE_CODE_DOT.token)
        return html
    
    @classmethod
    def tokenize_cnki_html(cls, html):
        html = re.sub(r"_(.*?)_", r"\1", html)
        # Replace italic tags
        html = re.sub(r"<i>(.*?)</i>", r"\1", html)
        # latex_str = re.sub(r"<i>(.*?)</i>", r"$\1$", latex_str)

        html = re.sub(
            r"(<sub>(.*?)</sub>)+",
            lambda m: cls.EXTRACT_ITEX.token
            + "_{"
            + "".join(re.findall(r"<sub>(.*?)</sub>", m.group(0)))
            + "}"
            + cls.EXTRACT_ITEX_END.token,
            html,
        )
        html = re.sub(
            r"(<sup>(.*?)</sup>)+",
            lambda m: cls.EXTRACT_ITEX.token
            + "^{"
            + "".join(re.findall(r"<sup>(.*?)</sup>", m.group(0)))
            + "}"
            + cls.EXTRACT_ITEX_END.token,
            html,
        )
        return html
    
    def detokenize_html(self, text):
        """
        将 token 还原为原始符号（如 $、§、换行等），可根据需要扩展
        """
        for token in self.register_tokens:
            text = text.replace(token.token, token.replacement)

        # in case we forget to register some tokens
        text = re.sub(r"\[extract_image_tag_\d+\]", "", text)

        
        return text
        

