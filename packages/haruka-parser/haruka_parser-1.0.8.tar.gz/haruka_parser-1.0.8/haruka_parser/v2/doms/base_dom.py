import traceback
import logging
from haruka_parser.v2.manager import ContextManager

class BaseDom:
    def __init__(self):
        pass

    def _process(self, node, manager: ContextManager):
        raise NotImplementedError("Subclasses must implement this method")

    def process(self, node, manager: ContextManager):
        try:
            self._process(node, manager)
        except:
            logging.error(f"Error in {self.__class__.__name__}: {traceback.format_exc()}")