from abc import ABC, abstractmethod
from typing import Tuple
from dataclasses import dataclass, field
from typing import Generator, NewType
from .data import Document
from typing import Union

class BaseFilter(ABC):
    """Base module for Filters. Filters remove documents.

    Args:
        exclusion_writer: optionally pass in a writer that will save the dropped documents
    """

    type = "🔻 - FILTER"

    def __init__(self):
        pass

    @abstractmethod
    def filter(self, doc: Document) -> Union[bool, Tuple[bool, str]]:
        """Filter modules main method.
        Returns true if a sample should be KEPT, false if it should be REMOVED.

        Args:
            doc: sample to filter

        Returns:
            bool - whether the doc should be kept
            or (False, str), to drop with a specific reason
        """
        raise NotImplementedError

    def better_filter(self, doc: Document) -> Tuple[bool, str]:
        if not doc.text.strip():
            return False, "empty_text"
        res = self.filter(doc)
        result, reason = res, None
        if isinstance(result, tuple):
            result, reason = res
        return result, reason
