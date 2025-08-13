import re
from functools import lru_cache
from html import unescape
from collections import Counter

import numpy as np
import yaml

LINES_TRIMMING = re.compile(r'(?<![p{P}>])\n', flags=re.UNICODE|re.MULTILINE)

AUTHOR_PREFIX = re.compile(r'^([a-zäöüß]+(ed|t))? ?(written by|words by|words|by|von|from) ', flags=re.IGNORECASE)
AUTHOR_REMOVE_NUMBERS = re.compile(r'\d.+?$')
AUTHOR_TWITTER = re.compile(r'@[\w]+')
AUTHOR_REPLACE_JOIN = re.compile(r'[._+]')
AUTHOR_REMOVE_NICKNAME = re.compile(r'["‘({\[’\'][^"]+?[‘’"\')\]}]')
AUTHOR_REMOVE_SPECIAL = re.compile(r'[^\w]+$|[:()?*$#!%/<>{}~¿]')
AUTHOR_REMOVE_PREPOSITION = re.compile(r'\b\s+(am|on|for|at|in|to|from|of|via|with|—|-|–)\s+(.*)', flags=re.IGNORECASE)
AUTHOR_EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
AUTHOR_SPLIT = re.compile(r'/|;|,|\||&|(?:^|\W)[u|a]nd(?:$|\W)', flags=re.IGNORECASE)
AUTHOR_EMOJI_REMOVE = re.compile(
    "["
    u"\U00002700-\U000027BF"  # Dingbats
    u"\U0001F600-\U0001F64F"  # Emoticons
    u"\U00002600-\U000026FF"  # Miscellaneous Symbols
    u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
    u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    "]+", flags=re.UNICODE)
AUTHOR_REMOVE_HTML = re.compile(r'<[^>]+>')
CLEAN_META_TAGS = re.compile(r'["\']')

PARSER_TAG = re.compile(r"\[[^\]]{1,49}\]")
END_SYMBOL = {'!', '"', "'", ',', '.', ';', '?', '״', '،', '؛', '۔', '।', '॥', '၊', '။', '។', '៕', '’', '‚', '”', '„', '。', '！', '，', '；', '？', '．'}
BLACKLIST_END_SYMBOL = {"…","...","。。。","．．．"}

IMG_SRC_ATTR = [
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
    "src",
]

@lru_cache(maxsize=2**14)  # sys.maxunicode = 1114111
def return_printables_and_spaces(char):
    'Return a character if it belongs to certain classes'
    return char if char.isprintable() or char.isspace() else ''

def remove_control_characters(string):
    '''Prevent non-printable and XML invalid character errors'''
    return ''.join(map(return_printables_and_spaces, string))

def line_processing(line, preserve_space=False, trailing_space=False):
    '''Remove HTML space entities, then discard incompatible unicode
       and invalid XML characters on line level'''
    # spacing HTML entities: https://www.w3.org/MarkUp/html-spec/html-spec_13.html
    # unique code spaces
    new_line = remove_control_characters(line.replace('&#13;', '\r').replace('&#10;', '\n').replace('&nbsp;', '\u00A0'))
    if not preserve_space:
        # remove newlines that are not related to punctuation or markup
        # remove non-printable chars and normalize space characters (including Unicode spaces)
        new_line = trim(LINES_TRIMMING.sub(r" ", new_line))
        # prune empty lines
        if all(map(str.isspace, new_line)):
            new_line = None
        elif trailing_space:
            space_before = " " if line[0] == " " else ""
            space_after = " " if line[-1] == " " else ""
            new_line = "".join([space_before, new_line, space_after])
    return new_line

def normalize_authors(current_authors, author_string):
    '''Normalize author info to focus on author names only'''
    new_authors = []
    if author_string.lower().startswith('http') or AUTHOR_EMAIL.match(author_string):
        return current_authors
    if current_authors is not None:
        new_authors = current_authors.split('; ')
    # fix to code with unicode
    if '\\u' in author_string:
        author_string = author_string.encode().decode('unicode_escape')
    # fix html entities
    if '&#' in author_string or '&amp;' in author_string:
        author_string = unescape(author_string)
    # remove html tags
    author_string = AUTHOR_REMOVE_HTML.sub('', author_string)
    # examine names
    for author in AUTHOR_SPLIT.split(author_string):
        author = trim(author)
        # remove emoji
        author = AUTHOR_EMOJI_REMOVE.sub('', author)
        # remove @username
        author = AUTHOR_TWITTER.sub('', author)
        # replace special characters with space
        author = trim(AUTHOR_REPLACE_JOIN.sub(' ', author))
        author = AUTHOR_REMOVE_NICKNAME.sub('', author)
        # remove special characters
        author = AUTHOR_REMOVE_SPECIAL.sub('', author)
        author = AUTHOR_PREFIX.sub('', author)
        author = AUTHOR_REMOVE_NUMBERS.sub('', author)
        author = AUTHOR_REMOVE_PREPOSITION.sub('', author)
        # skip empty or improbably long strings
        if len(author) == 0 or (
            # simple heuristics, regex or vowel tests also possible
            ' ' not in author and '-' not in author and len(author) >= 50
            ):
            continue
        # title case
        if not author[0].isupper() or sum(1 for c in author if c.isupper()) < 1:
            author = author.title()
        # safety checks
        if author not in new_authors and (len(new_authors) == 0 or all(new_author not in author for new_author in new_authors)):
            new_authors.append(author)
    if len(new_authors) == 0:
        return current_authors
    return '; '.join(new_authors).strip('; ')

def normalize_tags(tags):
    '''Remove special characters of tags'''
    tags = CLEAN_META_TAGS.sub(r'', trim(unescape(tags)))
    return ", ".join(filter(None, tags.split(", ")))

def uniquify_list(l):
    """
    Remove duplicates from a list while keeping order in an efficient way.
    Dictionaries preserve insertion order since Python 3.6.

    https://www.peterbe.com/plog/fastest-way-to-uniquify-a-list-in-python-3.6
    """
    return list(dict.fromkeys(l))

def has_style(style, styles):
    """Does the style string contain any of the styles?
    This function is robust to variations in the spaces between the styles.
    """
    # Remove any spaces.
    style = style.replace(" ", "")
    styles = [s.replace(" ", "") for s in styles]
    for s in styles:
        if s in style:
            return True
    return False


def word_wrap(text, char_width=20):
    """Wrap text to a given width, not breaking words."""
    if not text:
        return ""

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        if len(" ".join(current_line + [word])) <= char_width:
            current_line.append(word)
        else:
            if current_line:  # Check if current_line is not empty
                lines.append(" ".join(current_line))
            current_line = [word]

            # Handle the case when the word is longer than the character width
            while len(current_line[0]) > char_width:
                lines.append(current_line[0][:char_width])
                current_line[0] = current_line[0][char_width:]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


class ReplacementManager:
    """This replacement manager simply adds tags next to the instances of the text.
    It contains a method to remove these tags."""

    def __init__(self):
        self.tags = set()

    def add_replacement(self, text, tag="default"):
        self.tags.add(tag)
        return f"§§{tag}§§" + text

    def remove_tags(self, text):
        tag_regex = "|".join(f"§§{tag}§§" for tag in self.tags)
        return re.sub(tag_regex, "", text)

    def has_tag(self, text, tag):
        return f"§§{tag}§§" in text


class Config:
    """A simple config object that loads a config from a YAML file and
    presents as a dictionary"""

    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

    def sample_from_list(self, list):
        """Sample from a list of (probability, value) tuples."""
        probabilities = [p for p, _ in list]
        values = [v for _, v in list]
        probabilities = np.array(probabilities)
        probabilities /= probabilities.sum()
        return np.random.choice(values, p=probabilities)

    def _sample(self, config):
        # For every value that has a type of list, first check it is in the format of:
        # - (probability, value)
        # - (probability, value)
        # - ...
        # And the probabilities sum to 1.
        # Then sample from the list.
        sampled_config = {}
        for key, value in config.items():
            # print the type of the value
            if isinstance(value, list):
                # Check the format of the list.
                # Check the probabilities sum to 1.
                # Sample from the list.
                sampled_config[key] = self.sample_from_list(value)
            elif isinstance(value, dict):
                sampled_config[key] = self._sample(value)
            else:
                sampled_config[key] = value
        return sampled_config

    def sample(self):
        return self._sample(self.config)


def trim(string):
    """Remove unnecessary spaces within a text string"""
    try:
        # remove newlines that are not related to punctuation or markup + proper trimming
        # return LINES_TRIMMING.sub(r' ', string).strip(' \t\n\r\v')
        # faster:
        return " ".join(string.split()).strip()
    except (AttributeError, TypeError):
        return None

# import html2text
# html2text_parser = html2text.HTML2Text()
# html2text_parser.ignore_links = True
# html2text_parser.ignore_images = True
# html2text_handler = html2text_parser.handle

# import html2text_rs
# html2text_handler = html2text_rs.text_plain

from haruka_parser.html_text import extract_text as html2text_handler

def fast_html2text(html, filter_length=None, filter_end_symbol=False, turndown=False):
    text = html2text_handler(html)
    if turndown:
        text = PARSER_TAG.sub("", text)
    if filter_length is not None:
        text = text.split("\n")
        text = [i for i in text if len(i) > filter_length]
        text = "\n".join(text)
    if filter_end_symbol:
        filtered_lines = []

        for line in text.split("\n"):
            if any(line.endswith(blacklist) for blacklist in BLACKLIST_END_SYMBOL):
                continue
            if any(line.endswith(symbol) for symbol in END_SYMBOL):
                filtered_lines.append(line)

        text = "\n".join(filtered_lines)

    return text


from haruka_parser.dictionary import highlightjs

CODING_LANGUAGES = {lang.name.lower(): lang.alias.lower() for lang in highlightjs.languages}
CODING_LANGUAGES_NAMES = list(CODING_LANGUAGES.keys())
CODING_LANGUAGES_ALIAS = list(CODING_LANGUAGES.values())


def extract_code_languages(class_text):
    res = []
    languages = re.findall(r"language-(.+?) ", class_text)
    if languages:
        res.extend(languages)
    else:
        class_list = re.sub(r"[_\- ]", " ", class_text).split()
        for class_name in class_list:
            class_name_lower = class_name.lower()
            if class_name_lower in CODING_LANGUAGES_ALIAS:
                res.append(class_name_lower)
            if class_name_lower in CODING_LANGUAGES_NAMES:
                res.append(CODING_LANGUAGES[class_name_lower])
    return sorted(res, key=len, reverse=True)

def is_slow_html(html: str) -> bool:
    tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]{0,20})[^>]*>', html)
    tag_counts = Counter(tags)
    return max(tag_counts.values()) > 2000

def text_strip(text):
    return text.strip() if text else text

def str_contains(text: str, keywords: list) -> bool:
    for keyword in keywords:
        if keyword in text:
            return True
    return False