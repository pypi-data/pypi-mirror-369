# Haruka Parser

A simple HTML Parser

## Install

```bash
pip install haruka-parser
```

## Usage

```python3
from haruka_parser.extract import extract_text

html = """<!DOCTYPE html>
<html>
<body>
<!-- Using MathML -->
<p>Using MathJax:</p>
<script type="math/tex; mode=display" id="MathJax-Element-1">{e}^{i\pi }=-1</script>
<!-- Using MathML -->
<p>Using MathML:</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <msup>
    <mi>e</mi>
    <mrow>
      <mi>i</mi>
      <mi>&#x03C0;</mi>
    </mrow>
  </msup>
  <mo>=</mo>
  <mn>-1</mn>
</math>

<!-- Using AsciiMath -->
<p>Using AsciiMath:</p>
<script type="math/asciimath">
e^(i*pi) = -1
</script>

</body>
</html>"""

text, info = extract_text(html)
print(text)
print(info)
```

## Configurations

```python3
from haruka_parser.extract import DEFAULT_CONFIG
DEFAULT_CONFIG = {
    "readability": False,
    "skip_large_links": False,
    "extract_latex": True,
    "extract_cnki_latex": False,
    "escape_dollars": True,
    "remove_buttons": True,
    "remove_edit_buttons": True,
    "remove_image_figures": True,
    "markdown_code": True,
    "markdown_headings": True,
    "remove_chinese": False,
    "boilerplate_config": {
        "enable": False,
        "ratio_threshold": 0.18,
        "absolute_threshold": 10,
        "end_threshold": 15,
    },
}
```

## Parsing speed

10k Page:
| method | haruka-parser 0.5.2 | haruku-parser 0.4.9 | html2text | inscriptis | trafilatura |
| ------- | --------- | ------- | ------- | -------- | ----- |
| Speed   | 379.4s | 391.6s | 272.8s | 114.7s | 343.9s |
