"""
Functions needed to scrape metadata from JSON-LD format.
For reference, here is the list of all JSON-LD types: https://schema.org/docs/full.html
"""

import json
import re
from copy import deepcopy
from html import unescape

from courlan.filters import is_valid_url
from lxml.html import tostring

from .utils import (line_processing, normalize_authors, normalize_tags, trim,
                    unescape)

JSON_ARTICLE_SCHEMA = {"article", "backgroundnewsarticle", "blogposting", "medicalscholarlyarticle", "newsarticle", "opinionnewsarticle", "reportagenewsarticle", "scholarlyarticle", "socialmediaposting", "liveblogposting"}
JSON_OGTYPE_SCHEMA = {"aboutpage", "checkoutpage", "collectionpage", "contactpage", "faqpage", "itempage", "medicalwebpage", "profilepage", "qapage", "realestatelisting", "searchresultspage", "webpage", "website", "article", "advertisercontentarticle", "newsarticle", "analysisnewsarticle", "askpublicnewsarticle", "backgroundnewsarticle", "opinionnewsarticle", "reportagenewsarticle", "reviewnewsarticle", "report", "satiricalarticle", "scholarlyarticle", "medicalscholarlyarticle", "socialmediaposting", "blogposting", "liveblogposting", "discussionforumposting", "techarticle", "blog", "jobposting"}
JSON_PUBLISHER_SCHEMA = {"newsmediaorganization", "organization", "webpage", "website"}
JSON_AUTHOR_1 = re.compile(r'"author":[^}[]+?"name?\\?": ?\\?"([^"\\]+)|"author"[^}[]+?"names?".+?"([^"]+)', re.DOTALL)
JSON_AUTHOR_2 = re.compile(r'"[Pp]erson"[^}]+?"names?".+?"([^"]+)', re.DOTALL)
JSON_AUTHOR_REMOVE = re.compile(r',?(?:"\w+":?[:|,\[])?{?"@type":"(?:[Ii]mageObject|[Oo]rganization|[Ww]eb[Pp]age)",[^}[]+}[\]|}]?')
JSON_PUBLISHER = re.compile(r'"publisher":[^}]+?"name?\\?": ?\\?"([^"\\]+)', re.DOTALL)
JSON_TYPE = re.compile(r'"@type"\s*:\s*"([^"]*)"', re.DOTALL)
JSON_CATEGORY = re.compile(r'"articleSection": ?"([^"\\]+)', re.DOTALL)
JSON_NAME = re.compile(r'"@type":"[Aa]rticle", ?"name": ?"([^"\\]+)', re.DOTALL)
JSON_HEADLINE = re.compile(r'"headline": ?"([^"\\]+)', re.DOTALL)
JSON_MATCH = re.compile(r'"author":|"person":', flags=re.IGNORECASE)
JSON_REMOVE_HTML = re.compile(r'<[^>]+>')
JSON_SCHEMA_ORG = re.compile(r"^https?://schema\.org", flags=re.IGNORECASE)
JSON_UNICODE_REPLACE = re.compile(r'\\u([0-9a-fA-F]{4})')


def extract_json(schema, metadata):
    '''Parse and extract metadata from JSON-LD data'''
    if isinstance(schema, dict):
        schema = [schema]

    for parent in filter(lambda p: '@context' in p and isinstance(p['@context'], str) and JSON_SCHEMA_ORG.match(p['@context']), schema):
        try:
            if '@graph' in parent:
                parent = parent['@graph'] if isinstance(parent['@graph'], list) else [parent['@graph']]
            elif '@type' in parent and isinstance(parent['@type'], str) and 'liveblogposting' in parent['@type'].lower() and 'liveBlogUpdate' in parent:
                parent = parent['liveBlogUpdate'] if isinstance(parent['liveBlogUpdate'], list) else [parent['liveBlogUpdate']]
            else:
                parent = schema

            for content in filter(None, parent):
                try:
                    # try to extract publisher
                    if 'publisher' in content and 'name' in content['publisher']:
                        metadata.sitename = content['publisher']['name']

                    if '@type' not in content or len(content["@type"]) == 0:
                        continue
                    if isinstance(content["@type"], list):
                        # some websites are using ['Person'] as type
                        content_type = content["@type"][0].lower()
                    else:
                        content_type = content["@type"].lower()

                    # The "pagetype" should only be returned if the page is some kind of an article, category, website...
                    if content_type in JSON_OGTYPE_SCHEMA and not metadata.pagetype:
                        metadata.pagetype = normalize_json(content_type)

                    if content_type in JSON_PUBLISHER_SCHEMA:
                        candidate = next((content[candidate] for candidate in ("name", "legalName", "alternateName") if content.get(candidate)), None)
                        if candidate and isinstance(candidate, str):
                            if metadata.sitename is None or (len(metadata.sitename) < len(candidate) and content_type != "webpage"):
                                metadata.sitename = candidate
                            if metadata.sitename is not None and metadata.sitename.startswith('http') and not candidate.startswith('http'):
                                metadata.sitename = candidate

                    elif content_type == "person":
                        if content.get('name') and not content['name'].startswith('http'):
                            metadata.author = normalize_authors(metadata.author, content['name'])

                    elif content_type in JSON_ARTICLE_SCHEMA:
                        # author and person
                        if 'author' in content:
                            list_authors = content['author']
                            if isinstance(list_authors, str):
                                # try to convert to json object
                                try:
                                    list_authors = json.loads(list_authors)
                                except json.JSONDecodeError:
                                    # it is a normal string
                                    metadata.author = normalize_authors(metadata.author, list_authors)

                            if not isinstance(list_authors, list):
                                list_authors = [list_authors]
                            for author in list_authors:
                                if '@type' not in author or author['@type'] == 'Person':
                                    # error thrown: author['name'] can be a list (?)
                                    if 'name' in author and author['name'] is not None:
                                        author_name = author['name']
                                        if isinstance(author_name, list):
                                            author_name = '; '.join(author_name).strip('; ')
                                        elif isinstance(author_name, dict) and "name" in author_name:
                                            author_name = author_name["name"]
                                        # check for no more bugs on json
                                        if isinstance(author_name, str):
                                            metadata.author = normalize_authors(metadata.author, author_name)
                                    elif 'givenName' in author and 'familyName' in author:
                                        name = [author['givenName'], author.get('additionalName'), author['familyName']]
                                        metadata.author = normalize_authors(metadata.author, ' '.join(filter(None, name)))

                        # category
                        if metadata.categories is None and 'articleSection' in content:
                            if isinstance(content['articleSection'], str):
                                metadata.categories = [content['articleSection']]
                            else:
                                metadata.categories = list(filter(None, content['articleSection']))

                        # try to extract title
                        if metadata.title is None:
                            if 'name' in content and content_type == 'article':
                                metadata.title = content['name']
                            elif 'headline' in content:
                                metadata.title = content['headline']
                except:
                    pass
        except:
            pass
    return metadata


def extract_json_author(elemtext, regular_expression):
    '''Crudely extract author names from JSON-LD data'''
    authors = None
    mymatch = regular_expression.search(elemtext)
    while mymatch is not None and mymatch[1] and ' ' in mymatch[1]:
        authors = normalize_authors(authors, mymatch[1])
        elemtext = regular_expression.sub(r'', elemtext, count=1)
        mymatch = regular_expression.search(elemtext)
    return authors or None


def extract_json_parse_error(elem, metadata):
    '''Crudely extract metadata from JSON-LD data'''
    # author info
    element_text_author = JSON_AUTHOR_REMOVE.sub('', elem)
    if any(JSON_MATCH.findall(element_text_author)):
        author = extract_json_author(element_text_author, JSON_AUTHOR_1) or extract_json_author(element_text_author, JSON_AUTHOR_2)
        if author:
            metadata.author = author

    # try to extract page type as an alternative to og:type
    if "@type" in elem:
        mymatch = JSON_TYPE.search(elem)
        candidate = normalize_json(mymatch[1].lower())
        if mymatch and candidate in JSON_OGTYPE_SCHEMA:
            metadata.pagetype = candidate

    # try to extract publisher
    if '"publisher"' in elem:
        mymatch = JSON_PUBLISHER.search(elem)
        if mymatch and ',' not in mymatch[1]:
            candidate = normalize_json(mymatch[1])
            if metadata.sitename is None or len(metadata.sitename) < len(candidate):
                metadata.sitename = candidate
            if metadata.sitename.startswith('http') and not candidate.startswith('http'):
                metadata.sitename = candidate

    # category
    if '"articleSection"' in elem:
        mymatch = JSON_CATEGORY.search(elem)
        if mymatch:
            metadata.categories = [normalize_json(mymatch[1])]

    # try to extract title
    if '"name"' in elem and metadata.title is None:
        mymatch = JSON_NAME.search(elem)
        if mymatch:
            metadata.title = normalize_json(mymatch[1])
    if '"headline"' in elem and metadata.title is None:
        mymatch = JSON_HEADLINE.search(elem)
        if mymatch:
            metadata.title = normalize_json(mymatch[1])

    # exit if found
    return metadata


def normalize_json(inputstring):
    'Normalize unicode strings and trim the output'
    if '\\' in inputstring:
        inputstring = inputstring.replace('\\n', '').replace('\\r', '').replace('\\t', '')
        inputstring = JSON_UNICODE_REPLACE.sub(lambda match: chr(int(match.group(1), 16)), inputstring)
        inputstring = ''.join(c for c in inputstring if ord(c) < 0xD800 or ord(c) > 0xDFFF)
        inputstring = unescape(inputstring)
    return trim(JSON_REMOVE_HTML.sub('', inputstring))


class Document:
    "Defines a class to store all necessary data and metadata fields for extracted information."
    __slots__ = [
    'title', 'author', 'url', 'hostname', 'description', 'sitename',
    'date', 'categories', 'tags', 'fingerprint', 'id', 'license',
    'body', 'comments', 'commentsbody', 'raw_text', 'text',
    'language', 'image', 'pagetype'  # 'locale'?
    ]
    # consider dataclasses for Python 3.7+
    def __init__(self):
        for slot in self.__slots__:
            setattr(self, slot, None)

    def set_attributes(self, title, author, url, description, site_name, image, pagetype, tags, date):
        "Helper function to (re-)set a series of attributes."
        if title:
            self.title = title
        if author:
            self.author = author
        if url:
            self.url = url
        if description:
            self.description = description
        if site_name:
            self.sitename = site_name
        if image:
            self.image = image
        if pagetype:
            self.pagetype = pagetype
        if tags:
            self.tags = tags
        if date:
            self.date = date

    def clean_and_trim(self):
        "Limit text length and trim the attributes."
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, str):
                # length
                if len(value) > 10000:
                    new_value = value[:9999] + '…'
                    setattr(self, slot, new_value)
                    value = new_value
                # HTML entities, remove spaces and control characters
                value = line_processing(unescape(value))
                setattr(self, slot, value)

    def as_dict(self):
        "Convert the document to a dictionary."
        return {
            attr: getattr(self, attr)
            for attr in self.__slots__
            if hasattr(self, attr)
        }


HTMLDATE_CONFIG_FAST = {'extensive_search': False, 'original_date': True}
HTMLDATE_CONFIG_EXTENSIVE = {'extensive_search': True, 'original_date': True}

JSON_MINIFY = re.compile(r'("(?:\\"|[^"])*")|\s')

HTMLTITLE_REGEX = re.compile(r'^(.+)?\s+[–•·—|⁄*⋆~‹«<›»>:-]\s+(.+)$')  # part without dots?
HTML_STRIP_TAG = re.compile(r'(<!--.*?-->|<[^>]*>)')

LICENSE_REGEX = re.compile(r'/(by-nc-nd|by-nc-sa|by-nc|by-nd|by-sa|by|zero)/([1-9]\.[0-9])')
TEXT_LICENSE_REGEX = re.compile(r'(cc|creative commons) (by-nc-nd|by-nc-sa|by-nc|by-nd|by-sa|by|zero) ?([1-9]\.[0-9])?', re.I)

METANAME_AUTHOR = {
    'article:author', 'atc-metaauthor', 'author', 'authors', 'byl', 'citation_author',
    'creator', 'dc.creator', 'dc.creator.aut', 'dc:creator',
    'dcterms.creator', 'dcterms.creator.aut', 'dcsext.author', 'parsely-author',
    'rbauthors', 'sailthru.author', 'shareaholic:article_author_name'
}  # questionable: twitter:creator
METANAME_DESCRIPTION = {
    'dc.description', 'dc:description',
    'dcterms.abstract', 'dcterms.description',
    'description', 'sailthru.description', 'twitter:description'
}
METANAME_PUBLISHER = {
    'article:publisher', 'citation_journal_title', 'copyright',
    'dc.publisher', 'dc:publisher', 'dcterms.publisher',
    'publisher', 'sailthru.publisher', 'rbpubname', 'twitter:site'
}  # questionable: citation_publisher
METANAME_TAG = {
    'citation_keywords', 'dcterms.subject', 'keywords', 'parsely-tags',
    'shareaholic:keywords', 'tags'
}
METANAME_TITLE = {
    'citation_title', 'dc.title', 'dcterms.title', 'fb_title',
    'headline', 'parsely-title', 'sailthru.title', 'shareaholic:title',
    'rbtitle', 'title', 'twitter:title'
}
METANAME_URL = {
    'rbmainurl', 'twitter:url'
}
METANAME_IMAGE = {
    'image', 'og:image', 'og:image:url', 'og:image:secure_url',
    'twitter:image', 'twitter:image:src'
}
METANAME_TIME = {
    'og:time', 'PubDate', 'pubtime', '_pubtime', 'apub:time', 'pubdate', 'publishdate', 'PublishDate', 'sailthru.date', 'dateUpdate', 'publication_date', 
    'datePublished', 'og:release_date', 'article_date_original', 'og:published_time', 'rnews:datePublished', 'OriginalPublicationDate', 'weibo: article:create_at', 'article:published_time'
}
OG_AUTHOR = {'og:author', 'og:article:author'}
PROPERTY_AUTHOR = {'author', 'article:author'}
TWITTER_ATTRS = {'twitter:site', 'application-name'}

# also interesting: article:section

EXTRA_META = {'charset', 'http-equiv', 'property'}

def extract_meta_json(tree, metadata):
    '''Parse and extract metadata from JSON-LD data'''
    for elem in tree.xpath('.//script[@type="application/ld+json" or @type="application/settings+json"]'):
        if not elem.text:
            continue
        element_text = normalize_json(JSON_MINIFY.sub(r'\1', elem.text))
        try:
            schema = json.loads(element_text)
            metadata = extract_json(schema, metadata)
        except json.JSONDecodeError:
            metadata = extract_json_parse_error(element_text, metadata)
    return metadata

def extract_opengraph(tree):
    '''Search meta tags following the OpenGraph guidelines (https://ogp.me/)'''
    title, author, url, description, site_name, image, pagetype, date = (None,) * 8
    # detect OpenGraph schema
    for elem in tree.xpath('.//head/meta[starts-with(@property, "og:")]'):
        # safeguard
        if not elem.get('content'):
            continue
        # site name
        if elem.get('property') == 'og:site_name':
            site_name = elem.get('content')
        # blog title
        elif elem.get('property') == 'og:title':
            title = elem.get('content')
        # orig URL
        elif elem.get('property') == 'og:url':
            if is_valid_url(elem.get('content')):
                url = elem.get('content')
        # description
        elif elem.get('property') == 'og:description':
            description = elem.get('content')
        # og:author
        elif elem.get('property') in OG_AUTHOR:
            author = normalize_authors(None, elem.get('content'))
        # image default
        elif elem.get('property') == 'og:image':
            image = elem.get('content')
        # image url
        elif elem.get('property') == 'og:image:url':
            image = elem.get('content')
        # image secure url
        elif elem.get('property') == 'og:image:secure_url':
            image = elem.get('content')
        # og:type
        elif elem.get('property') == 'og:type':
            pagetype = elem.get('content')
        elif elem.get('property') == 'og:time':
            date = elem.get('content')
        # og:locale
        # elif elem.get('property') == 'og:locale':
        #    pagelocale = elem.get('content')
    return title, author, url, description, site_name, image, pagetype, date


def examine_meta(tree):
    '''Search meta tags for relevant information'''
    metadata = Document()  # alt: Metadata()
    # bootstrap from potential OpenGraph tags
    title, author, url, description, site_name, image, pagetype, date = extract_opengraph(tree)
    # test if all values not assigned in the following have already been assigned
    if all((title, author, url, description, site_name, image)):
        metadata.set_attributes(title, author, url, description, site_name, image, pagetype, tags=None, date=date)  # tags
        return metadata
    tags, backup_sitename = [], None
    # skim through meta tags
    for elem in tree.iterfind('.//head/meta[@content]'):
        try:
            # content
            if not elem.get('content'):
                continue
            content_attr = HTML_STRIP_TAG.sub('', elem.get('content'))
            # image info
            # ...
            # property
            if 'property' in elem.attrib:
                # no opengraph a second time
                if elem.get('property').startswith('og:'):
                    continue
                if elem.get('property') == 'article:tag':
                    tags.append(normalize_tags(content_attr))
                elif elem.get('property') in PROPERTY_AUTHOR:
                    author = normalize_authors(author, content_attr)
                elif elem.get('property') == 'article:publisher':
                    site_name = site_name or content_attr
                elif elem.get('property') in METANAME_IMAGE:
                    image = image or content_attr
            # name attribute
            elif 'name' in elem.attrib:
                name_attr = elem.get('name').lower()
                # author
                if name_attr in METANAME_AUTHOR:
                    author = normalize_authors(author, content_attr)
                # title
                elif name_attr in METANAME_TITLE:
                    title = title or content_attr
                # description
                elif name_attr in METANAME_DESCRIPTION:
                    description = description or content_attr
                # site name
                elif name_attr in METANAME_PUBLISHER:
                    site_name = site_name or content_attr
                # twitter
                elif name_attr in TWITTER_ATTRS or 'twitter:app:name' in elem.get('name'):
                    backup_sitename = content_attr
                # url
                elif name_attr == 'twitter:url':
                    if url is None and is_valid_url(content_attr):
                        url = content_attr
                # keywords
                elif name_attr in METANAME_TAG:  # 'page-topic'
                    tags.append(normalize_tags(content_attr))
                elif name_attr in METANAME_TIME:
                    date = content_attr
            elif 'itemprop' in elem.attrib:
                if elem.get('itemprop') == 'author':
                    author = normalize_authors(author, content_attr)
                elif elem.get('itemprop') == 'description':
                    description = description or content_attr
                elif elem.get('itemprop') == 'headline':
                    title = title or content_attr
                # to verify:
                # elif elem.get('itemprop') == 'name':
                #    if title is None:
                #        title = elem.get('content')
            # other types
            # elif all(
            #     key not in elem.attrib
            #     for key in EXTRA_META
            # ):
            #     LOGGER.debug('unknown attribute: %s',
            #                  tostring(elem, pretty_print=False, encoding='unicode').strip())
        except:
            pass
    # backups
    if site_name is None and backup_sitename is not None:
        site_name = backup_sitename
    # copy
    metadata.set_attributes(title, author, url, description, site_name, image, pagetype, tags, date)
    return metadata


def extract_metainfo(tree, expressions, len_limit=200):
    '''Extract meta information'''
    # try all XPath expressions
    for expression in expressions:
        # examine all results
        i = 0
        for elem in expression(tree):
            content = trim(' '.join(elem.itertext()))
            if content and 2 < len(content) < len_limit:
                return content
            i += 1
        # if i > 1:
        #     LOGGER.debug('more than one invalid result: %s %s', expression, i)
    return None


def extract_metadata(tree, default_url=None, date_config=None, fastmode=False, author_blacklist=None):
    """Main process for metadata extraction.

    Args:
        filecontent: HTML code as string.
        default_url: Previously known URL of the downloaded document.
        date_config: Provide extraction parameters to htmldate as dict().
        author_blacklist: Provide a blacklist of Author Names as set() to filter out authors.

    Returns:
        A trafilatura.metadata.Document containing the extracted metadata information or None.
        trafilatura.metadata.Document has .as_dict() method that will return a copy as a dict.
    """
    # init
    if author_blacklist is None:
        author_blacklist = set()
    # initialize dict and try to strip meta tags
    metadata = examine_meta(tree)
    # to check: remove it and replace with author_blacklist in test case
    if metadata.author is not None and ' ' not in metadata.author:
        metadata.author = None
    # fix: try json-ld metadata and override
    try:
        metadata = extract_meta_json(tree, metadata)
    # todo: fix bugs in json_metadata.py
    except TypeError as err:
        pass
        # LOGGER.warning('error in JSON metadata extraction: %s', err)
    
    # safety checks
    metadata.clean_and_trim()
    # return result
    return metadata.as_dict()
