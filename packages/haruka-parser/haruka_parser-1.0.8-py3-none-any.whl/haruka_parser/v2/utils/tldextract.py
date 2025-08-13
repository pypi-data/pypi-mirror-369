from __future__ import annotations

import os
import re
from typing import List

PUBLIC_SUFFIX_RE = re.compile(r"^(?P<suffix>[.*!]*\w[\S]*)", re.UNICODE | re.MULTILINE)
PUBLIC_PRIVATE_SUFFIX_SEPARATOR = "// ===BEGIN PRIVATE DOMAINS==="

tld_suffix_list = os.path.join(
    os.path.dirname(__file__), "../../", "dictionary/public_suffix_list.txt"
)


def get_suffix_lists() -> tuple[list[str], list[str]]:
    """Parse the raw suffix list text for its different designations of suffixes."""
    suffix_list_text = open(tld_suffix_list, "r").read()
    public_text, _, private_text = suffix_list_text.partition(
        PUBLIC_PRIVATE_SUFFIX_SEPARATOR
    )

    public_tlds = [m.group("suffix") for m in PUBLIC_SUFFIX_RE.finditer(public_text)]
    private_tlds = [m.group("suffix") for m in PUBLIC_SUFFIX_RE.finditer(private_text)]
    return public_tlds, private_tlds


from ipaddress import AddressValueError, IPv6Address
from urllib.parse import scheme_chars

IP_RE = re.compile(
    r"^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
    r"{3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
    re.ASCII,
)

scheme_chars_set = set(scheme_chars)


def lenient_netloc(url: str) -> str:
    """Extract the netloc of a URL-like string.

    Similar to the netloc attribute returned by
    urllib.parse.{urlparse,urlsplit}, but extract more leniently, without
    raising errors.
    """
    after_userinfo = (
        _schemeless_url(url)
        .partition("/")[0]
        .partition("?")[0]
        .partition("#")[0]
        .rpartition("@")[-1]
    )

    if after_userinfo and after_userinfo[0] == "[":
        maybe_ipv6 = after_userinfo.partition("]")
        if maybe_ipv6[1] == "]":
            return f"{maybe_ipv6[0]}]"

    hostname = after_userinfo.partition(":")[0].strip()
    without_root_label = hostname.rstrip(".\u3002\uff0e\uff61")
    return without_root_label


def _schemeless_url(url: str) -> str:
    double_slashes_start = url.find("//")
    if double_slashes_start == 0:
        return url[2:]
    if (
        double_slashes_start < 2
        or url[double_slashes_start - 1] != ":"
        or set(url[: double_slashes_start - 1]) - scheme_chars_set
    ):
        return url
    return url[double_slashes_start + 2 :]


def looks_like_ip(maybe_ip: str) -> bool:
    """Check whether the given str looks like an IPv4 address."""
    if not maybe_ip[0].isdigit():
        return False

    return IP_RE.fullmatch(maybe_ip) is not None


def looks_like_ipv6(maybe_ip: str) -> bool:
    """Check whether the given str looks like an IPv6 address."""
    try:
        IPv6Address(maybe_ip)
    except AddressValueError:
        return False
    return True


"""`tldextract` accurately separates a URL's subdomain, domain, and public suffix.

It does this via the Public Suffix List (PSL).

    >>> import tldextract

    >>> tldextract.extract("http://forums.news.cnn.com/")
    ExtractResult(subdomain='forums.news', domain='cnn', suffix='com', is_private=False)

    >>> tldextract.extract("http://forums.bbc.co.uk/")  # United Kingdom
    ExtractResult(subdomain='forums', domain='bbc', suffix='co.uk', is_private=False)

    >>> tldextract.extract("http://www.worldbank.org.kg/")  # Kyrgyzstan
    ExtractResult(subdomain='www', domain='worldbank', suffix='org.kg', is_private=False)

Note subdomain and suffix are _optional_. Not all URL-like inputs have a
subdomain or a valid suffix.

    >>> tldextract.extract("google.com")
    ExtractResult(subdomain='', domain='google', suffix='com', is_private=False)

    >>> tldextract.extract("google.notavalidsuffix")
    ExtractResult(subdomain='google', domain='notavalidsuffix', suffix='', is_private=False)

    >>> tldextract.extract("http://127.0.0.1:8080/deployed/")
    ExtractResult(subdomain='', domain='127.0.0.1', suffix='', is_private=False)

To rejoin the original hostname, if it was indeed a valid, registered hostname:

    >>> ext = tldextract.extract("http://forums.bbc.co.uk")
    >>> ext.top_domain_under_public_suffix
    'bbc.co.uk'
    >>> ext.fqdn
    'forums.bbc.co.uk'
"""

import os
import urllib.parse
import warnings
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from functools import wraps

import idna


class Trie:
    """Trie for storing eTLDs with their labels in reverse-order."""

    def __init__(
        self,
        matches: dict[str, Trie] | None = None,
        end: bool = False,
        is_private: bool = False,
    ) -> None:
        """TODO."""
        self.matches = matches if matches else {}
        self.end = end
        self.is_private = is_private

    @staticmethod
    def create(
        public_suffixes: Collection[str],
        private_suffixes: Collection[str] | None = None,
    ) -> Trie:
        """Create a Trie from a list of suffixes and return its root node."""
        root_node = Trie()

        for suffix in public_suffixes:
            root_node.add_suffix(suffix)

        if private_suffixes is None:
            private_suffixes = []

        for suffix in private_suffixes:
            root_node.add_suffix(suffix, True)

        return root_node

    def add_suffix(self, suffix: str, is_private: bool = False) -> None:
        """Append a suffix's labels to this Trie node."""
        node = self

        labels = suffix.split(".")
        labels.reverse()

        for label in labels:
            if label not in node.matches:
                node.matches[label] = Trie()
            node = node.matches[label]

        node.end = True
        node.is_private = is_private

class _PublicSuffixListTLDExtractor:
    """Wrapper around this project's main algo for PSL lookups."""

    def __init__(
        self,
        public_tlds: list[str],
        private_tlds: list[str],
        extra_tlds: list[str],
        include_psl_private_domains: bool = False,
    ):
        # set the default value
        self.include_psl_private_domains = include_psl_private_domains
        self.public_tlds = public_tlds
        self.private_tlds = private_tlds
        self.tlds_incl_private = frozenset(public_tlds + private_tlds + extra_tlds)
        self.tlds_excl_private = frozenset(public_tlds + extra_tlds)
        self.tlds_incl_private_trie = Trie.create(
            self.tlds_excl_private, frozenset(private_tlds)
        )
        self.tlds_excl_private_trie = Trie.create(self.tlds_excl_private)

    def tlds(self, include_psl_private_domains: bool | None = None) -> frozenset[str]:
        """Get the currently filtered list of suffixes."""
        if include_psl_private_domains is None:
            include_psl_private_domains = self.include_psl_private_domains

        return (
            self.tlds_incl_private
            if include_psl_private_domains
            else self.tlds_excl_private
        )

    def suffix_index(
        self, spl: list[str], include_psl_private_domains: bool | None = None
    ) -> tuple[tuple[int, Trie], tuple[int, Trie]] | None:
        """Return the index of the first public suffix label, the index of the first registry suffix label, and their corresponding trie nodes.

        Returns `None` if no suffix is found.
        """
        if include_psl_private_domains is None:
            include_psl_private_domains = self.include_psl_private_domains

        node = reg_node = (
            self.tlds_incl_private_trie
            if include_psl_private_domains
            else self.tlds_excl_private_trie
        )
        suffix_idx = reg_idx = label_idx = len(spl)
        for label in reversed(spl):
            decoded_label = _decode_punycode(label)
            if decoded_label in node.matches:
                label_idx -= 1
                node = node.matches[decoded_label]
                if node.end:
                    suffix_idx = label_idx
                    if not node.is_private:
                        reg_node = node
                        reg_idx = label_idx
                continue

            is_wildcard = "*" in node.matches
            if is_wildcard:
                is_wildcard_exception = "!" + decoded_label in node.matches
                return (
                    label_idx if is_wildcard_exception else label_idx - 1,
                    node.matches["*"],
                ), (
                    reg_idx,
                    reg_node,
                )

            break

        if suffix_idx == len(spl):
            return None

        return ((suffix_idx, node), (reg_idx, reg_node))


@dataclass(order=True)
class ExtractResult:
    """A URL's extracted subdomain, domain, and suffix.

    These first 3 fields are what most users of this library will care about.
    They are the split, non-overlapping hostname components of the input URL.
    They can be used to rebuild the original URL's hostname.

    Beyond the first 3 fields, the class contains metadata fields, like a flag
    that indicates if the input URL's suffix is from a private domain.
    """

    subdomain: str
    """All subdomains beneath the domain of the input URL, if it contained any such subdomains, or else the empty string."""

    domain: str
    """The topmost domain of the input URL, if it contained a domain name, or else everything hostname-like in the input.

    If the input URL didn't contain a real domain name, the `suffix` field will
    be empty, and this field will catch values like an IP address, or
    private network hostnames like "localhost".
    """

    suffix: str
    """The public suffix of the input URL, if it contained one, or else the empty string.

    If `include_psl_private_domains` was set to `False`, this field is the same
    as `registry_suffix`, i.e. a domain under which people can register
    subdomains through a registrar. If `include_psl_private_domains` was set to
    `True`, this field may be a PSL private domain, like "blogspot.com".
    """

    is_private: bool
    """Whether the input URL belongs in the Public Suffix List's private domains.

    If `include_psl_private_domains` was set to `False`, this field is always
    `False`.
    """

    registry_suffix: str = field(repr=False)
    """The registry suffix of the input URL, if it contained one, or else the empty string.

    This field is a domain under which people can register subdomains through a
    registar.

    This field is unaffected by the `include_psl_private_domains` setting. If
    `include_psl_private_domains` was set to `False`, this field is always the
    same as `suffix`.
    """

    @property
    def fqdn(self) -> str:
        """The Fully Qualified Domain Name (FQDN), if there is a proper `domain` and `suffix`, or else the empty string.

        >>> extract("http://forums.bbc.co.uk/path/to/file").fqdn
        'forums.bbc.co.uk'
        >>> extract("http://localhost:8080").fqdn
        ''
        """
        if self.suffix and (self.domain or self.is_private):
            return ".".join(i for i in (self.subdomain, self.domain, self.suffix) if i)
        return ""

    @property
    def ipv4(self) -> str:
        """The IPv4 address, if that is what the input domain/URL was, or else the empty string.

        >>> extract("http://127.0.0.1/path/to/file").ipv4
        '127.0.0.1'
        >>> extract("http://127.0.0.1.1/path/to/file").ipv4
        ''
        >>> extract("http://256.1.1.1").ipv4
        ''
        """
        if (
            self.domain
            and not (self.suffix or self.subdomain)
            and looks_like_ip(self.domain)
        ):
            return self.domain
        return ""

    @property
    def ipv6(self) -> str:
        """The IPv6 address, if that is what the input domain/URL was, or else the empty string.

        >>> extract(
        ...     "http://[aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1]/path/to/file"
        ... ).ipv6
        'aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1'
        >>> extract(
        ...     "http://[aBcD:ef01:2345:6789:aBcD:ef01:127.0.0.1.1]/path/to/file"
        ... ).ipv6
        ''
        >>> extract("http://[aBcD:ef01:2345:6789:aBcD:ef01:256.0.0.1]").ipv6
        ''
        """
        min_num_ipv6_chars = 4
        if (
            len(self.domain) >= min_num_ipv6_chars
            and self.domain[0] == "["
            and self.domain[-1] == "]"
            and not (self.suffix or self.subdomain)
        ):
            debracketed = self.domain[1:-1]
            if looks_like_ipv6(debracketed):
                return debracketed
        return ""

    @property
    def registered_domain(self) -> str:
        """The `domain` and `suffix` fields joined with a dot, if they're both set, or else the empty string.

        >>> extract("http://forums.bbc.co.uk").registered_domain
        'bbc.co.uk'
        >>> extract("http://localhost:8080").registered_domain
        ''

        .. deprecated:: 6.0.0
           This property is deprecated and will be removed in the next major
           version. Use `top_domain_under_public_suffix` instead, which has the
           same behavior but a more accurate name.

        This is an alias for the `top_domain_under_public_suffix` property.
        `registered_domain` is so called because is roughly the domain the
        owner paid to register with a registrar or, in the case of a private
        domain, "registered" with the domain owner. If the input was not
        something one could register, this property returns the empty string.

        To distinguish the case of private domains, consider Blogspot, which is
        in the PSL's private domains. If `include_psl_private_domains` was set
        to `False`, the `registered_domain` property of a Blogspot URL
        represents the domain the owner of Blogspot registered with a
        registrar, i.e. Google registered "blogspot.com". If
        `include_psl_private_domains=True`, the `registered_domain` property
        represents the "blogspot.com" _subdomain_ the owner of a blog
        "registered" with Blogspot.

        >>> extract(
        ...     "http://waiterrant.blogspot.com", include_psl_private_domains=False
        ... ).registered_domain
        'blogspot.com'
        >>> extract(
        ...     "http://waiterrant.blogspot.com", include_psl_private_domains=True
        ... ).registered_domain
        'waiterrant.blogspot.com'

        To always get the same joined string, regardless of the
        `include_psl_private_domains` setting, consider the
        `top_domain_under_registry_suffix` property.
        """
        warnings.warn(
            "The 'registered_domain' property is deprecated and will be removed in the next major version. "
            "Use 'top_domain_under_public_suffix' instead, which has the same behavior but a more accurate name.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.top_domain_under_public_suffix

    @property
    def reverse_domain_name(self) -> str:
        """The domain name in Reverse Domain Name Notation.

        Joins extracted components of the input URL in reverse domain name
        notation. The suffix is used as the leftmost component, followed by the
        domain, then followed by the subdomain with its parts reversed.

        Reverse Domain Name Notation is typically used to organize namespaces
        for packages and plugins. Technically, a full reversal would reverse
        the parts of the suffix, e.g. "co.uk" would become "uk.co", but this is
        not done in practice when Reverse Domain Name Notation is called for.
        So this property leaves the `suffix` part in its original order.

        >>> extract("login.example.com").reverse_domain_name
        'com.example.login'

        >>> extract("login.example.co.uk").reverse_domain_name
        'co.uk.example.login'
        """
        stack = [self.suffix, self.domain]
        if self.subdomain:
            stack.extend(reversed(self.subdomain.split(".")))
        return ".".join(stack)

    @property
    def top_domain_under_registry_suffix(self) -> str:
        """The rightmost domain label and `registry_suffix` joined with a dot, if such a domain is available and `registry_suffix` is set, or else the empty string.

        The rightmost domain label might be in the `domain` field, or, if the
        input URL's suffix is a PSL private domain, in the public suffix
        `suffix` field.

        If the input was not in the PSL's private domains, this property is
        equivalent to `top_domain_under_public_suffix`.

        >>> extract(
        ...     "http://waiterrant.blogspot.com", include_psl_private_domains=False
        ... ).top_domain_under_registry_suffix
        'blogspot.com'
        >>> extract(
        ...     "http://waiterrant.blogspot.com", include_psl_private_domains=True
        ... ).top_domain_under_registry_suffix
        'blogspot.com'
        >>> extract("http://localhost:8080").top_domain_under_registry_suffix
        ''
        """
        top_domain_under_public_suffix = self.top_domain_under_public_suffix
        if not top_domain_under_public_suffix or not self.is_private:
            return top_domain_under_public_suffix

        num_labels = self.registry_suffix.count(".") + 2
        return ".".join(top_domain_under_public_suffix.split(".")[-num_labels:])

    @property
    def top_domain_under_public_suffix(self) -> str:
        """The `domain` and `suffix` fields joined with a dot, if they're both set, or else the empty string.

        >>> extract("http://forums.bbc.co.uk").top_domain_under_public_suffix
        'bbc.co.uk'
        >>> extract("http://localhost:8080").top_domain_under_public_suffix
        ''
        """
        if self.suffix and self.domain:
            return f"{self.domain}.{self.suffix}"
        return ""


class TLDExtract:
    """A callable for extracting, subdomain, domain, and suffix components from a URL."""

    # TODO: too-many-arguments
    def __init__(
        self,
        include_psl_private_domains: bool = False,
        extra_suffixes: Sequence[str] = (),
    ) -> None:
        """Construct a callable for extracting subdomain, domain, and suffix components from a URL.

        Upon calling it, it first checks for a JSON in `cache_dir`. By default,
        the `cache_dir` will live in the tldextract directory. You can disable
        the caching functionality of this module by setting `cache_dir` to `None`.

        If the cached version does not exist, such as on the first run, HTTP
        request the URLs in `suffix_list_urls` in order, and use the first
        successful response for public suffix definitions. Subsequent, untried
        URLs are ignored. The default URLs are the latest version of the
        Mozilla Public Suffix List and its mirror, but any similar document URL
        could be specified. Local files can be specified by using the `file://`
        protocol (see `urllib2` documentation). To disable HTTP requests, set
        this to an empty sequence.

        If there is no cached version loaded and no data is found from the `suffix_list_urls`,
        the module will fall back to the included TLD set snapshot. If you do not want
        this behavior, you may set `fallback_to_snapshot` to False, and an exception will be
        raised instead.

        The Public Suffix List includes a list of "private domains" as TLDs,
        such as blogspot.com. These do not fit `tldextract`'s definition of a
        suffix, so these domains are excluded by default. If you'd like them
        included instead, set `include_psl_private_domains` to True.

        You can specify additional suffixes in the `extra_suffixes` argument.
        These will be merged into whatever public suffix definitions are
        already in use by `tldextract`, above.

        cache_fetch_timeout is passed unmodified to the underlying request object
        per the requests documentation here:
        http://docs.python-requests.org/en/master/user/advanced/#timeouts

        cache_fetch_timeout can also be set to a single value with the
        environment variable TLDEXTRACT_CACHE_TIMEOUT, like so:

        TLDEXTRACT_CACHE_TIMEOUT="1.2"

        When set this way, the same timeout value will be used for both connect
        and read timeouts
        """

        self.include_psl_private_domains = include_psl_private_domains
        self.extra_suffixes = extra_suffixes
        self._extractor: _PublicSuffixListTLDExtractor | None = None

    def __call__(
        self,
        url: str,
        include_psl_private_domains: bool | None = None,
    ) -> ExtractResult:
        """Alias for `extract_str`."""
        return self.extract_str(url, include_psl_private_domains)

    def extract_str(
        self,
        url: str,
        include_psl_private_domains: bool | None = None,
    ) -> ExtractResult:
        """Take a string URL and splits it into its subdomain, domain, and suffix components.

        I.e. its effective TLD, gTLD, ccTLD, etc. components.

        >>> extractor = TLDExtract()
        >>> extractor.extract_str("http://forums.news.cnn.com/")
        ExtractResult(subdomain='forums.news', domain='cnn', suffix='com', is_private=False)
        >>> extractor.extract_str("http://forums.bbc.co.uk/")
        ExtractResult(subdomain='forums', domain='bbc', suffix='co.uk', is_private=False)

        Allows configuring the HTTP request via the optional `session`
        parameter. For example, if you need to use a HTTP proxy. See also
        `requests.Session`.

        >>> import requests
        >>> session = requests.Session()
        >>> # customize your session here
        >>> with session:
        ...     extractor.extract_str("http://forums.news.cnn.com/", session=session)
        ExtractResult(subdomain='forums.news', domain='cnn', suffix='com', is_private=False)
        """
        return self._extract_netloc(
            lenient_netloc(url), include_psl_private_domains
        )

    def extract_urllib(
        self,
        url: urllib.parse.ParseResult | urllib.parse.SplitResult,
        include_psl_private_domains: bool | None = None
    ) -> ExtractResult:
        """Take the output of urllib.parse URL parsing methods and further splits the parsed URL.

        Splits the parsed URL into its subdomain, domain, and suffix
        components, i.e. its effective TLD, gTLD, ccTLD, etc. components.

        This method is like `extract_str` but faster, as the string's domain
        name has already been parsed.

        >>> extractor = TLDExtract()
        >>> extractor.extract_urllib(
        ...     urllib.parse.urlsplit("http://forums.news.cnn.com/")
        ... )
        ExtractResult(subdomain='forums.news', domain='cnn', suffix='com', is_private=False)
        >>> extractor.extract_urllib(urllib.parse.urlsplit("http://forums.bbc.co.uk/"))
        ExtractResult(subdomain='forums', domain='bbc', suffix='co.uk', is_private=False)
        """
        return self._extract_netloc(
            url.netloc, include_psl_private_domains
        )

    def _extract_netloc(
        self,
        netloc: str,
        include_psl_private_domains: bool | None,
    ) -> ExtractResult:
        netloc_with_ascii_dots = (
            netloc.replace("\u3002", "\u002e")
            .replace("\uff0e", "\u002e")
            .replace("\uff61", "\u002e")
        )

        min_num_ipv6_chars = 4
        if (
            len(netloc_with_ascii_dots) >= min_num_ipv6_chars
            and netloc_with_ascii_dots[0] == "["
            and netloc_with_ascii_dots[-1] == "]"
            and looks_like_ipv6(netloc_with_ascii_dots[1:-1])
        ):
            return ExtractResult(
                "", netloc_with_ascii_dots, "", is_private=False, registry_suffix=""
            )

        labels = netloc_with_ascii_dots.split(".")

        maybe_indexes = self._get_tld_extractor().suffix_index(
            labels, include_psl_private_domains=include_psl_private_domains
        )

        num_ipv4_labels = 4
        if (
            not maybe_indexes
            and len(labels) == num_ipv4_labels
            and looks_like_ip(netloc_with_ascii_dots)
        ):
            return ExtractResult(
                "", netloc_with_ascii_dots, "", is_private=False, registry_suffix=""
            )
        elif not maybe_indexes:
            return ExtractResult(
                subdomain=".".join(labels[:-1]),
                domain=labels[-1],
                suffix="",
                is_private=False,
                registry_suffix="",
            )

        (
            (public_suffix_index, public_suffix_node),
            (registry_suffix_index, registry_suffix_node),
        ) = maybe_indexes

        subdomain = (
            ".".join(labels[: public_suffix_index - 1])
            if public_suffix_index >= 2
            else ""
        )
        domain = labels[public_suffix_index - 1] if public_suffix_index > 0 else ""
        public_suffix = ".".join(labels[public_suffix_index:])
        registry_suffix = (
            ".".join(labels[registry_suffix_index:])
            if public_suffix_node.is_private
            else public_suffix
        )
        return ExtractResult(
            subdomain=subdomain,
            domain=domain,
            suffix=public_suffix,
            is_private=public_suffix_node.is_private,
            registry_suffix=registry_suffix,
        )

    def update(
        self, fetch_now: bool = False
    ) -> None:
        """Force fetch the latest suffix list definitions."""
        self._extractor = None
        if fetch_now:
            self._get_tld_extractor()

    @property
    def tlds(self) -> list[str]:
        """The list of TLDs used by default.

        This will vary based on `include_psl_private_domains` and `extra_suffixes`.
        """
        return list(self._get_tld_extractor().tlds())

    def _get_tld_extractor(
        self
    ) -> _PublicSuffixListTLDExtractor:
        """Get or compute this object's TLDExtractor.

        Looks up the TLDExtractor in roughly the following order, based on the
        settings passed to __init__:

        1. Memoized on `self`
        2. Local system _cache file
        3. Remote PSL, over HTTP
        4. Bundled PSL snapshot file
        """
        if self._extractor:
            return self._extractor

        public_tlds, private_tlds = get_suffix_lists()

        if not any([public_tlds, private_tlds, self.extra_suffixes]):
            raise ValueError("No tlds set. Cannot proceed without tlds.")

        self._extractor = _PublicSuffixListTLDExtractor(
            public_tlds=public_tlds,
            private_tlds=private_tlds,
            extra_tlds=list(self.extra_suffixes),
            include_psl_private_domains=self.include_psl_private_domains,
        )
        return self._extractor


TLD_EXTRACTOR = TLDExtract()



@wraps(TLD_EXTRACTOR.__call__)
def extract(  # noqa: D103
    url: str,
    include_psl_private_domains: bool | None = False,
) -> ExtractResult:
    return TLD_EXTRACTOR(
        url, include_psl_private_domains=include_psl_private_domains
    )


@wraps(TLD_EXTRACTOR.update)
def update(*args, **kwargs):  # type: ignore[no-untyped-def]  # noqa: D103
    return TLD_EXTRACTOR.update(*args, **kwargs)

def _decode_punycode(label: str) -> str:
    lowered = label.lower()
    looks_like_puny = lowered.startswith("xn--")
    if looks_like_puny:
        try:
            return idna.decode(lowered)
        except (UnicodeError, IndexError):
            pass
    return lowered

from functools import lru_cache

@lru_cache(maxsize=10000)
def extract_domain(url):
    """Extract the second-level domain from a URL using tldextract library."""
    try:
        # Use tldextract to extract the registered domain (second-level domain)
        extract_result = TLD_EXTRACTOR(url)
        # Combine domain with suffix to get the registered domain
        return ".".join(filter(lambda x: x, [extract_result.domain, extract_result.suffix]))
    except Exception as e:
        print(f"Error extracting domain: {e}")
        return None
    return None