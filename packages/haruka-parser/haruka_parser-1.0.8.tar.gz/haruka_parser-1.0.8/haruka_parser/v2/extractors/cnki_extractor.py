import re
from haruka_parser.v2.extractors.base_extractor import BaseExtractor


class CnkiExtractor(BaseExtractor):
    def __init__(self) -> None:
        super().__init__()

    def tokenize_html(self, html):
        # Replace consecutive subscript tags
        html = re.sub(r"_(.*?)_", r"\1", html)
        # Replace italic tags
        html = re.sub(r"<i>(.*?)</i>", r"\1", html)
        # latex_str = re.sub(r"<i>(.*?)</i>", r"$\1$", latex_str)

        html = re.sub(
            r"(<sub>(.*?)</sub>)+",
            # lambda m: "_{" + "".join(re.findall(r"<sub>(.*?)</sub>", m.group(0))) + "}",
            lambda m: "[extract_itex]"
            + "_{"
            + "".join(re.findall(r"<sub>(.*?)</sub>", m.group(0)))
            + "}"
            + "[/extract_itex]",
            html,
        )
        html = re.sub(
            r"(<sup>(.*?)</sup>)+",
            lambda m: "[extract_itex]"
            + "^{"
            + "".join(re.findall(r"<sup>(.*?)</sup>", m.group(0)))
            + "}"
            + "[/extract_itex]",
            html,
        )
        return super().tokenize_html(html)