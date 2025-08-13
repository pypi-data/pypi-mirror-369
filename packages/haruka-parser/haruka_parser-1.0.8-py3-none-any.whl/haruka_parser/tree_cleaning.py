from collections import defaultdict
from copy import deepcopy

from lxml.etree import XPath, strip_tags

from .utils import IMG_SRC_ATTR, trim, uniquify_list

# order could matter, using lists to keep extraction deterministic
MANUALLY_CLEANED = [
    # important
    'aside', 'embed', 'footer', 'form', 'head', 'iframe', 'menu',
    # other content
    'applet', 'canvas', 'map',
    # secondary
    'area', 'blink', 'button', 'datalist', 'dialog',
    'frame', 'frameset', 'fieldset', 'link', 'input', 'ins', 'label', 'legend',
    'marquee', 'menuitem', 'nav', 'optgroup', 'option',
    'output', 'param', 'progress', 'rp', 'rt', 'rtc', 'select',
    'style', 'track', 'textarea', 'time', 'use',
]
# 'meta', 'hr', 'img', 'data', 'details', 'summary', 'math', 'script'

MANUALLY_STRIPPED = [
    'abbr', 'acronym', 'address', 'bdi', 'bdo', 'big', 'cite', 'data', 'dfn',
    'font', 'hgroup', 'ins', 'kbd', 'mark', 'meta', 'ruby', 'small', 'tbody',
    'template', 'tfoot', 'thead', 's', 'samp', 'shadow', 'small', 'strike',
    'tt', 'u', 'var'
]
# 'center', 'rb', 'wbr'

# filters
CUT_EMPTY_ELEMS = {'article', 'b', 'blockquote', 'dd', 'div', 'dt', 'em',
                   'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'li', 'main',
                   'p', 'pre', 'q', 'section', 'span', 'strong'}
                   # 'meta', 'td', 'a', 'caption', 'dl', 'header',
                   # 'colgroup', 'col',
#CUT_EMPTY_ELEMS = {'div', 'span'}

# learn from obelics
MEDIA_CONTAIN_INTERESTING_ATTRIBUTES_SET = [
    "audio", "embed", "figure", "iframe",
    "img", "object", "picture", "video", "source",
]

OVERALL_DISCARD_XPATH = [XPath(x) for x in (
    # navigation + footers, news outlets related posts, sharing, jp-post-flair jp-relatedposts
    '''.//*[(self::div or self::item or self::list
             or self::p or self::section or self::span)][
    contains(translate(@id, "F","f"), "footer") or contains(translate(@class, "F","f"), "footer")
    or contains(@id, "related") or contains(translate(@class, "R", "r"), "related") or
    contains(@id, "viral") or contains(@class, "viral") or
    starts-with(@id, "shar") or starts-with(@class, "shar") or
    contains(@class, "share-") or
    contains(translate(@id, "S", "s"), "share") or
    contains(@id, "social") or contains(@class, "social") or contains(@class, "sociable") or
    contains(@id, "syndication") or contains(@class, "syndication") or
    starts-with(@id, "jp-") or starts-with(@id, "dpsp-content") or
    contains(@class, "embedded") or contains(@class, "embed")
    or contains(@id, "newsletter") or contains(@class, "newsletter")
    or contains(@class, "subnav") or
    contains(@id, "cookie") or contains(@class, "cookie") or contains(@id, "tags")
    or contains(@class, "tags")  or contains(@id, "sidebar") or
    contains(@class, "sidebar") or contains(@id, "banner") or contains(@class, "banner")
    or contains(@class, "meta") or
    contains(@id, "menu") or contains(@class, "menu") or
    contains(translate(@id, "N", "n"), "nav") or contains(translate(@role, "N", "n"), "nav")
    or starts-with(@class, "nav") or contains(translate(@class, "N", "n"), "navigation") or
    contains(@class, "navbar") or contains(@class, "navbox") or starts-with(@class, "post-nav")
    or contains(@id, "breadcrumb") or contains(@class, "breadcrumb") or
    contains(@id, "bread-crumb") or contains(@class, "bread-crumb") or
    contains(@id, "author") or contains(@class, "author") or
    contains(@id, "button") or contains(@class, "button")
    or contains(translate(@class, "B", "b"), "byline")
    or contains(@class, "rating") or starts-with(@class, "widget") or
    contains(@class, "attachment") or contains(@class, "timestamp") or
    contains(@class, "user-info") or contains(@class, "user-profile") or
    contains(@class, "-ad-") or contains(@class, "-icon")
    or contains(@class, "article-infos") or
    contains(translate(@class, "I", "i"), "infoline")
    or contains(@data-component, "MostPopularStories")
    or contains(@class, "outbrain") or contains(@class, "taboola")
    or contains(@class, "criteo") or contains(@class, "options")
    or contains(@class, "consent") or contains(@class, "modal-content")
    or contains(@class, "paid-content") or contains(@class, "paidcontent")
    or contains(@id, "premium-") or contains(@id, "paywall")
    or contains(@class, "obfuscated") or contains(@class, "blurred")
    or contains(@class, " ad ")
    or contains(@class, "next-post") or contains(@class, "side-stories")
    or contains(@class, "related-stories") or contains(@class, "most-popular")
    or contains(@class, "mol-factbox") or starts-with(@class, "ZendeskForm")
    or contains(@class, "message-container") or contains(@id, "message_container")
    or contains(@class, "yin") or contains(@class, "zlylin") or
    contains(@class, "xg1") or contains(@id, "bmdh")
    or @data-lp-replacement-content or @data-testid]''',

    # comment debris + hidden parts
    '''.//*[@class="comments-title" or contains(@class, "comments-title") or
    contains(@class, "nocomments") or starts-with(@id, "reply-") or starts-with(@class, "reply-") or
    contains(@class, "-reply-") or contains(@class, "message") or contains(@id, "reader-comments")
    or contains(@id, "akismet") or contains(@class, "akismet") or contains(@class, "suggest-links") or
    starts-with(@class, "hide-") or contains(@class, "hide-print") or contains(@id, "hidden")
    or contains(@style, "hidden") or contains(@hidden, "hidden") or contains(@class, "noprint")
    or contains(@style, "display:none") or contains(@style, "display: none") or contains(@class, " hidden") or @aria-hidden="true"
    or contains(@class, "notloaded")]''',
)]
# conflicts:
# contains(@id, "header") or contains(@class, "header") or
# class contains "cats" (categories, also tags?)
# or contains(@class, "hidden ")  or contains(@class, "-hide")
# or contains(@class, "paywall")
# contains(@class, "content-info") or contains(@class, "content-title")
# contains(translate(@class, "N", "n"), "nav") or

PAYWALL_DISCARD_XPATH = [XPath(
    '''.//*[(self::div or self::p)][
    contains(@id, "paywall") or contains(@id, "premium") or
    contains(@class, "paid-content") or contains(@class, "paidcontent") or
    contains(@class, "obfuscated") or contains(@class, "blurred") or
    contains(@class, "restricted") or contains(@class, "overlay")
    ]'''
)]

# the following conditions focus on extraction precision
TEASER_DISCARD_XPATH = [XPath(
    '''.//*[(self::div or self::item or self::list
             or self::p or self::section or self::span)][
        contains(translate(@id, "T", "t"), "teaser") or contains(translate(@class, "T", "t"), "teaser")
    ]'''
)]

def delete_element(element):
    "Remove the element from the LXML tree."
    try:
        element.drop_tree()  # faster when applicable
    except AttributeError:  # pragma: no cover
        element.getparent().remove(element)


def tree_cleaning(tree):
    "Prune the tree by discarding unwanted elements."
    # determine cleaning strategy, use lists to keep it deterministic
    cleaning_list, stripping_list = \
        MANUALLY_CLEANED.copy(), MANUALLY_STRIPPED.copy()
    
    # prevent this issue: https://github.com/adbar/trafilatura/issues/301
    for elem in tree.xpath('.//figure[descendant::table]'):
        elem.tag = 'div'
        
    # strip targeted elements
    strip_tags(tree, stripping_list)

    # delete targeted elements
    for expression in cleaning_list:
        for element in tree.getiterator(expression):
            delete_element(element)
            
    tree = remove_empty_nodes(tree)

    return prune_html(tree)


def prune_html(tree):
    "Delete selected empty elements to save space and processing time."
    # //comment() needed for date extraction
    for element in tree.xpath("//processing-instruction()|//*[not(node())]"):
        if element.tag in CUT_EMPTY_ELEMS:
            delete_element(element)
    return tree

def prune_unwanted_nodes(tree, nodelist, with_backup=False):
    '''Prune the HTML tree by removing unwanted sections.'''
    if with_backup is True:
        old_len = len(tree.text_content())  # ' '.join(tree.itertext())
        backup = deepcopy(tree)
    for expression in nodelist:
        for subtree in expression(tree):
            # preserve tail text from deletion
            if subtree.tail is not None:
                previous = subtree.getprevious()
                if previous is None:
                    previous = subtree.getparent()
                if previous is not None:
                    # There is a previous node, append text to its tail
                    if previous.tail is not None:
                        previous.tail = ' '.join([previous.tail, subtree.tail])
                    else:
                        previous.tail = subtree.tail
            # remove the node
            subtree.getparent().remove(subtree)
    if with_backup is False:
        return tree
    # else:
    new_len = len(tree.text_content())
    # todo: adjust for recall and precision settings
    if new_len > old_len/7:
        return tree
    return backup

def collect_link_info(links_xpath, favor_precision=False):
    '''Collect heuristics on link text'''
    # init
    shortelems, mylist = 0, []
    # longer strings impact recall in favor of precision
    threshold = 10 if not favor_precision else 50
    # examine the elements
    for subelem in links_xpath:
        subelemtext = trim(subelem.text_content())
        if subelemtext:
            mylist.append(subelemtext)
            if len(subelemtext) < threshold:
                shortelems += 1
    lengths = sum(len(text) for text in mylist)
    return lengths, len(mylist), shortelems, mylist

def link_density_test(element, text, favor_precision=False):
    '''Remove sections which are rich in links (probably boilerplate)'''
    links_xpath, mylist = element.findall('.//ref'), []
    if links_xpath:
        if element.tag == 'p': #  and not element.getparent().tag == 'item'
            if favor_precision is False:
                if element.getnext() is None:
                    limitlen, threshold = 60, 0.8
                else:
                    limitlen, threshold = 30, 0.8
            else:
                limitlen, threshold = 200, 0.8
            #if 'hi' in list(element):
            #    limitlen, threshold = 100, 0.8
        #elif element.tag == 'head':
        #    limitlen, threshold = 50, 0.8
        else:
            if element.getnext() is None:
                limitlen, threshold = 300, 0.8
            #elif re.search(r'[.?!:]', elemtext):
            #    limitlen, threshold = 150, 0.66
            else:
                limitlen, threshold = 100, 0.8
        elemlen = len(text)
        if elemlen < limitlen:
            linklen, elemnum, shortelems, mylist = collect_link_info(links_xpath, favor_precision)
            if elemnum == 0:
                return True, mylist
            # (elemnum > 1 and shortelems/elemnum > 0.8):
            if linklen > threshold*elemlen or (elemnum > 1 and shortelems/elemnum > 0.8):
                return True, mylist
    return False, mylist

def delete_by_link_density(subtree, tagname, backtracking=False, favor_precision=False):
    '''Determine the link density of elements with respect to their length,
       and remove the elements identified as boilerplate.'''
    myelems, deletions = defaultdict(list), []
    for elem in subtree.iter(tagname):
        elemtext = trim(elem.text_content())
        result, templist = link_density_test(elem, elemtext, favor_precision)
        if result is True:
            deletions.append(elem)
        elif backtracking is True and len(templist) > 0:  # if?
            myelems[elemtext].append(elem)
    # summing up
    if backtracking is True:
        if favor_precision is False:
            threshold = 100
        else:
            threshold = 200
        for text, elem in myelems.items():
            if 0 < len(text) < threshold and len(elem) >= 3:
                deletions.extend(elem)
                # print('backtrack:', text)
            # else: # and not re.search(r'[?!.]', text):
            # print(elem.tag, templist)
    for elem in uniquify_list(deletions):
        try:
            elem.getparent().remove(elem)
        except AttributeError:
            pass
    return subtree

def get_media_src(node):
    node_attributes = node.attrib
    node_tag = node.tag
    src = None

    if node_tag == "img":
        # Check all possible source type, and keep the first valid one
        for source_type in IMG_SRC_ATTR:
            if source_type in node_attributes and node_attributes[source_type]:
                if ("," not in node_attributes[source_type]) and (" " not in node_attributes[source_type]):
                    src = node_attributes[source_type]
                    break

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
    else:
        return None  # TODO iframes

    # Check on comma because it's non-canonical and should not be used anyway in urls.
    # TODO: have checks on valid URLs
    # Useless (at least for images) since already checked
    if src is not None and (("," in src) or (" " in src)):
        return None

    return src


def remove_empty_nodes(tree):
    """
    Function used to remove empty leaves iteratively, so it also ends up also removing nodes
    that are higher up in the tree.
    """
    modification = True
    while modification:
        nodes_to_remove = [
            node
            for node in tree.getroot().iter()
            if (
                (node.tag not in MEDIA_CONTAIN_INTERESTING_ATTRIBUTES_SET)
                and (not [child for child in node.iterchildren()])
                and (not node.text.strip())
                and (node.tag != "html")
            )
            or (
                (node.tag in MEDIA_CONTAIN_INTERESTING_ATTRIBUTES_SET)
                and not get_media_src(node)
            )
        ]
        if nodes_to_remove:
            for node in nodes_to_remove:
                node.getparent().remove(node)
        else:
            modification = False
    return tree