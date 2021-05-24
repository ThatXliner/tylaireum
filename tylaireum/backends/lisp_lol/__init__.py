import textwrap

from lark import Transformer

from tylaireum.backends import utils


class MainTransformer(Transformer):
    @utils.inline
    def main(self, code_block):
        return f"(main {code_block})"

    @utils.inline
    def code_block(self, *codes):
        return "(\n" + textwrap.indent("\n".join(codes), "    ") + "\n)"

    @utils.inline
    def call_op(self, value, args):
        return f"(call {value} ({', '.join(args.children)}))"

    @utils.inline
    def normal_import(self, *value):
        return f"(import {', '.join(value)})"

    @utils.inline
    def arg(self, keyword_name, value):
        if keyword_name is not None:
            return f"(keyword_arg {keyword_name} {value})"
        return f"(arg {value})"

    @utils.inline
    def namespacing(self, first, second):
        return f"{first}.{second}"

    codes = utils.inline(lambda _, x: x)
    start = lambda _, x: "\n".join(x)
