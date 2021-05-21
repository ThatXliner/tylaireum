from pathlib import Path
from typing import Iterator, List, Union

import lark
import lark.indenter


class Indenter(lark.indenter.Indenter):  # pylint: disable=C0115
    NL_type = "_NL"
    OPEN_PAREN_types: List[str] = [
        "_LEFT_PAREN",
        "_LEFT_BRACE",
        # "_LEFT_ANGLED",
        "_LEFT_CURLY",
    ]
    CLOSE_PAREN_types: List[str] = [
        "_RIGHT_PAREN",
        "_RIGHT_BRACE",
        # "_RIGHT_ANGLED",
        "_RIGHT_CURLY",
    ]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


class IterableTree(lark.Tree):
    def __iter__(self) -> Iterator[Union[lark.Tree, str]]:
        return iter(self.children)


HERE = Path(__file__).parent
grammar_file = HERE.joinpath("grammar.lark")
grammar = lark.Lark(
    grammar_file.read_text(),
    postlex=Indenter(),
    parser="lalr",
    # ambiguity="explicit",
    tree_class=IterableTree,
    maybe_placeholders=True,
)
