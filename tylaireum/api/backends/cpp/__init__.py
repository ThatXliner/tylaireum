import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import List, Optional

import jinja2
import lark
from lark import Transformer

from tylaireum import parser
from tylaireum.api.backends import utils

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(Path(__file__).parent.joinpath("templates"))),
    autoescape=False,
)


def codegen(doc: str) -> str:
    # TODO: Convert to AST first, then transpile (so we can validate the tree, etc)
    return "#include <iostream>\n" + R'int main(){std::cout << "Hello world!\n";}'
    # return INJECT_ME + MainTransformer().transform(parser.grammar.parse(doc))


# TODO: Make eval func
def evaluate(doc: str) -> subprocess.CompletedProcess:
    compiler = (
        shutil.which("c++") or shutil.which("g++") or shutil.which("clang++") or None
    )
    # C++ 11 or C++ 17? I haven't learned C++17 yet-
    # TODO: Learn C++17
    if compiler is None:
        raise RuntimeError(
            "Could not find a C++ compiler. Make sure it is on your $PATH"
        )
    assert compiler is not None
    infile = Path(".") / ".tylaireum_infile.cpp"
    infile.touch()
    infile.write_text(codegen(doc))
    subprocess.run([compiler, infile], check=True)
    # if not os.access(outfile, os.X_OK):
    #     os.chmod(outfile, os.X_OK)
    os.remove(infile)
    output = subprocess.run(["./a.out"], check=True, capture_output=True)
    os.remove("a.out")
    return output


INJECT_ME = textwrap.dedent(
    """\
    // Generated by tylaireum
    #include <iostream>
    """
)  # QUESTION: Is <string> unnecessary?


class ASTtransformer(Transformer):  # TODO: ast_utils ftw
    ...


class MainTransformer(Transformer):
    # pylint: disable=R0201,C0116
    STRING = lambda _, x: "u8" + utils.parse_string(x)  # UTF 8!

    @utils.inline
    def ffi(self, ffi_string: str) -> str:
        return ffi_string[3:-3]

    @utils.inline
    def call_op(self, name: str, args: lark.Tree) -> str:
        ...

    # if name not in SPECIAL_FUNC:
    #     return f"{name}({', '.join(str(arg) for arg in args.children)})"  # TODO: Do stuff with keyword arguments
    # return env.get_template(f"{name}.jinja").render(args=args)

    @utils.inline
    def main(self, code: List[str]) -> str:
        return env.get_template("main.jinja").render(codes=code)

    start = lambda _, x: "\n".join([repr(x)] if not isinstance(x, str) else x)
