import re
import gzip

from lxml.html import Element, HtmlElement, HTMLParser, fromstring, tostring
from lxml.html.clean import Cleaner
from urllib3.response import HTTPResponse

try:
    import brotli
except ImportError:
    brotli = None

try:
    from cchardet import detect as cchardet_detect
except ImportError:
    cchardet_detect = None

from difflib import SequenceMatcher

from charset_normalizer import from_bytes
from haruka_parser.tree_processing import fix_encode_html

HTML_PARSER = HTMLParser(
    collect_ids=False,
    default_doctype=False,
    encoding="utf-8",
    remove_comments=True,
    remove_pis=True,
)

DOCTYPE_TAG = re.compile("^< ?! ?DOCTYPE.+?/ ?>", re.I)

from re import sub

# Entities to be converted
HTML_TAG_ENTITIES = (
	# ISO-8895-1 (most common)
	("&#228;", u"ä"),
	("&auml;", u"ä"),
	("&#252;", u"ü"),
	("&uuml;", u"ü"),
	("&#246;", u"ö"),
	("&ouml;", u"ö"),
	("&#196;", u"Ä"),
	("&Auml;", u"Ä"),
	("&#220;", u"Ü"),
	("&Uuml;", u"Ü"),
	("&#214;", u"Ö"),
	("&Ouml;", u"Ö"),
	("&#223;", u"ß"),
	("&szlig;", u"ß"),

	# Rarely used entities
	("&#8230;", u"..."),
	("&#8211;", u"-"),
	("&#160;", u" "),
	("&#34;", u"\""),
	("&#38;", u"&"),
	("&#39;", u"'"),
	("&#60;", u"<"),
	("&#62;", u">"),

	# Common entities
	("&lt;", u"<"),
	("&gt;", u">"),
	("&nbsp;", u" "),
	("&amp;", u"&"),
	("&quot;", u"\""),
	("&apos;", u"'"),
)

def replace_tags(html, old, new):
    pattern = re.compile(old, re.IGNORECASE)
    return pattern.sub(new, html)

def fromstring_bytes(htmlobject):
    tree = None
    try:
        tree = fromstring(
            htmlobject.encode("utf8", "surrogatepass"), parser=HTML_PARSER
        )
    except Exception as err:
        pass
    return tree

def is_dubious_html(beginning: str) -> bool:
    return "html" not in beginning

def strip_faulty_doctypes(htmlstring: str, beginning: str) -> str:
    if "doctype" in beginning:
        firstline, _, rest = htmlstring.partition("\n")
        return DOCTYPE_TAG.sub("", firstline, count=1) + "\n" + rest
    return htmlstring

def handle_compressed_file(filecontent):
    if isinstance(filecontent, bytes):
        if filecontent[:2] == b"\x1f\x8b":
            try:
                filecontent = gzip.decompress(filecontent)
            except (EOFError, OSError):
                pass
        elif brotli is not None:
            try:
                filecontent = brotli.decompress(filecontent)
            except brotli.error:
                pass
    return filecontent

def decode_file(filecontent, encoding="utf-8"):
    if isinstance(filecontent, str):
        return filecontent, "utf-8"
    htmltext = None
    filecontent = handle_compressed_file(filecontent)
    htmltext, encoding = fix_encode_html(filecontent, encoding)
    if htmltext:
        return htmltext, encoding
    else:
        return str(filecontent, encoding="utf-8", errors="replace"), "utf-8"

def strip_html(htmlobject):
    for escaped, unescaped in HTML_TAG_ENTITIES:
        htmlobject = replace_tags(htmlobject, escaped, unescaped)
    htmlobject = replace_tags(htmlobject, "<template", "<div")
    htmlobject = replace_tags(htmlobject, "</template", "</div")
    htmlobject = replace_tags(htmlobject, "<frameset", "<div")
    htmlobject = replace_tags(htmlobject, "</frameset>", "</div>")
    return htmlobject

def read_html(htmlobject, encoding="utf-8"):
    if isinstance(htmlobject, HtmlElement):
        return htmlobject, encoding
    if isinstance(htmlobject, HTTPResponse) or hasattr(htmlobject, "data"):
        htmlobject = htmlobject.data
    if not isinstance(htmlobject, (bytes, str)):
        raise TypeError("incompatible input type", type(htmlobject))
    htmlobject, encoding = decode_file(htmlobject, encoding)
    # htmlobject = strip_html(htmlobject)
    return htmlobject, encoding

def load_html_tree(htmlobject):
    tree = None
    beginning = htmlobject[:100].lower()
    check_flag = is_dubious_html(beginning)
    htmlobject = strip_faulty_doctypes(htmlobject, beginning)
    fallback_parse = False
    try:
        tree = fromstring(htmlobject, parser=HTML_PARSER)
    except ValueError:
        tree = fromstring_bytes(htmlobject)
        fallback_parse = True
    except Exception as err:
        pass
    if (tree is None or len(tree) < 1) and not fallback_parse:
        tree = fromstring_bytes(htmlobject)
    # if tree is not None and check_flag is True and len(tree) < 2:
    #     tree = None
    if check_flag and tree is None:
        try:
            tree = fromstring("<pre>" + htmlobject + "</pre>")
        except Exception as err:
            pass
    return tree
