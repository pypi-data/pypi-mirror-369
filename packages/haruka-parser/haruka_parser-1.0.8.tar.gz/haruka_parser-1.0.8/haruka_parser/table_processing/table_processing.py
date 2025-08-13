from typing import Callable, Dict

from resiliparse.parse.html import HTMLTree

from haruka_parser.line_processing import have_chinese_characters
from haruka_parser.table_processing.canvas import Canvas
from haruka_parser.table_processing.html_state import (HtmlDocumentState,
                                                       ParserConfig)
from haruka_parser.table_processing.tags.table_tag import (table_end_handler,
                                                           table_start_handler,
                                                           td_end_handler,
                                                           td_start_handler,
                                                           tr_start_handler)
from haruka_parser.line_processing import restore_replacements

def remove_consecutive_blank_lines(table_text: str) -> str:

    lines = [line for line in table_text.split("\n") if line.strip()]

    if not lines:
        return ""

    space_map = [[1 if char == " " else 0 for char in line] for line in lines]

    max_len = max([len(line) for line in lines])

    normalized_space_map = [row + [0] * (max_len - len(row)) for row in space_map]

    column_space_count = [0] * max_len
    for col in range(max_len):
        for row in range(len(normalized_space_map)):
            if normalized_space_map[row][col] == 1:
                column_space_count[col] += 1

    column_all_space = [col for col in range(max_len) if column_space_count[col] == len(normalized_space_map)]

    column_to_append = {}
    column_to_del = []

    # Reduce consecutive columns with spaces to a maximum of 3
    MAX_SPACE_COLUMN = 3
    i = 0
    while i < len(column_all_space):
        start = i
        while (
            i < len(column_all_space) - 1
            and column_all_space[i] + 1 == column_all_space[i + 1]
        ):
            i += 1
        end = i

        if column_all_space[start] == 0:
            for j in range(start, end + 1):
                column_to_del.append(column_all_space[j])
        elif end - start + 1 > MAX_SPACE_COLUMN:
            for j in range(start + MAX_SPACE_COLUMN, end + 1):
                column_to_del.append(column_all_space[j])
        elif end - start + 1 < MAX_SPACE_COLUMN:
            column_to_append[column_all_space[start]] = MAX_SPACE_COLUMN - (end - start + 1)
        i += 1

    optimized_lines = []
    for line in lines:
        optimized_line = ""
        for i, char in enumerate(line):
            if i in column_to_del:
                continue
            # currently not append space
            # if i in column_to_append:
            #     optimized_line += " " * column_to_append[i]
            optimized_line += char
        optimized_lines.append(optimized_line)

    optimized_table_text = "\n".join(optimized_lines)

    return optimized_table_text

class TableExtractor():

    def __init__(self, html_tree, config: ParserConfig = None) -> None:

        config = config or ParserConfig()

        # setup start and end tag call tables
        self.start_tag_handler_dict: Dict[
            str, Callable[[HtmlDocumentState, Dict], None]
        ] = {
            "table": table_start_handler,
            "tr": tr_start_handler,
            "td": td_start_handler,
            "th": td_start_handler,
            # "ul": ul_start_handler,
            # "ol": ol_start_handler,
            # "li": li_start_handler,
            # "br": br_start_handler,
            # "a": a_start_handler if config.parse_a() else None,
            # "img": img_start_handler if config.display_images else None,
        }
        self.end_tag_handler_dict: Dict[str, Callable[[HtmlDocumentState], None]] = {
            "table": table_end_handler,
            # "ul": ul_end_handler,
            # "ol": ol_end_handler,
            "td": td_end_handler,
            "th": td_end_handler,
            # "a": a_end_handler if config.parse_a() else None,
        }

        self.canvas = self._parse_html_tree(HtmlDocumentState(config), html_tree)

    def _parse_html_tree(self, state: HtmlDocumentState, tree) -> Canvas:
        """Parse the HTML tree.

        Args:
            tree: the HTML tree to parse.
        """
        if isinstance(tree.tag, str):
            attrs = {}
            if tree.attrs:
                for attr in tree.attrs:
                    attrs[attr] = tree.getattr(attr)
            state.apply_starttag_layout(tree.tag, attrs)

            if handler := self.start_tag_handler_dict.get(tree.tag):
                handler(state, attrs)
            cur = state.tags[-1]
            cur.canvas.open_tag(cur)

            state.tags[-1].write(tree.value)

            for node in tree.child_nodes:
                self._parse_html_tree(state, node)

            # handle the endtag
            if handler := self.end_tag_handler_dict.get(tree.tag):
                handler(state)
            prev = state.tags.pop()
            prev.canvas.close_tag(prev)

        return state.canvas

    def get_text(self) -> str:
        """Return the text extracted from the HTML page."""
        table_text = self.canvas.get_text()
        try:
            table_text = remove_consecutive_blank_lines(table_text)
        except Exception as e:
            import traceback
            traceback.print_exc()
        return table_text.replace(" ", "[HARUKA_PARSER_BS]").replace(
            "\n", "[HARUKA_PARSER_CHANGE_LINE]"
        )


# Extracting text including tables from HTML
def extract_tables(tree, replacement_manager, config, info):

    # need to think about nested table?
    tables = tree.document.query_selector_all("table")

    for table in tables:
        if table.parent:
            info['table'] += 1
            table_tree = HTMLTree.parse(restore_replacements(str(table), replacement_manager, config, info))
            table_text = TableExtractor(table_tree.body).get_text()
            if have_chinese_characters(table_text):
                info["chinese_table"] += 1
            new_p = tree.create_element('pre')
            new_p.html = replacement_manager.add_replacement(
                table_text, tag="table"
            )
            table.parent.replace_child(new_p, table)
