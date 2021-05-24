# try:
#     from frosch import hook
#
#     hook()
# except ImportError:
#     pass


import re

import black

from tylaireum import parser
from tylaireum.backends.cpp import ast

DOC = """
import math, io
import time
main:
    print("Hello world!")
    print(
        "Fibbonacci of 3 is",
        math.fib(((2*1 + 1) % 6 % (7 + 8*9) - 1) * 1)
    )
    io.stdout.write("Isn't this cool?")
    input('Even single quotes work! [press enter]')
    io.stdin.readline('C++ RULES!')
    time.sleep(1)
    var integer: int = input('This will error. Everything is explicit! Super strong typing')
    macro THIS_IS_A_MACRO = 3
    print("it's value is determined on compile-time")
    switch THIS_IS_A_MACRO:
        case 3:
            print("MACRO WE GOT IS three!!#$R@``")
        default:
            print("Impossible.")
""".strip(
    "\n"
)

HELLO_WORLD = (
    """
import io
main:
    io.println("hello", "world")

""".strip(
        "\n"
    )
    + "\n"
)
IOPY = R"""
ffi include 'iostream', '../e'

def println(thing):
    std::cout << thing << std::endl

def print(thing):
    std::cout << thing

# const stdout = (def(){throw Error("Not Implemented")})
# const stdin = (def(){throw Error("Not Implemented")})
# const cout = std::cout
# const cin = std::cin
""".strip(
    "\n"
)
INLINE = R"""
main:
    if read() == '2':
        print('2!' + "!"
)
    if read() := 8 == 0:
        print(str(0) + ".")
    e() e_again()
    e(new E("e clas"))

""".strip(
    "\n"
)
CLASSES = R"""
class Animal:
    var name: str
    var steps: int = 0
    def __init__(name: str):
        this.name = name

    def move(meters: int):
        this.steps += 1
        print("moved $meters")

class Snake < Animal:
    def move():
        alert("Slithering...")
        super.move(5)

class Horse < Animal:
    def move():
        alert("Galloping...")
        return super.move(45)
"""
# tree = parser.grammar.parse(HELLO_WORLD)
# print(tree.pretty())
# print(black.format_str(repr(ast.transformer.transform(tree)), mode=black.Mode()))
tree = parser.grammar.parse(HELLO_WORLD)
print(tree.pretty())
# print(repr(ast.transformer.transform(tree)))
SAFE_FOR_BLACK_RE = re.compile(
    r"<(?:(?:(Template) '([^']+?)')|(?:(CompiledFunctionEnum)\.\w+: '([^']+?)'))>"
)
print(
    black.format_str(
        SAFE_FOR_BLACK_RE.sub(
            lambda m: repr(m[2]),
            repr(ast.transformer.transform(tree)),
        ),
        mode=black.Mode(),
    )
)
# print(
#     black.format_str(
#         SAFE_FOR_BLACK_RE.sub(
#             lambda m: repr(m[2]),
#             repr(ast.global_values),
#         ),
#         mode=black.Mode(),
#     )
# )
print(ast.transformer.transform(tree)["main"].code.contents[0].__compile__())
# for i in (HELLO_WORLD, IOPY, DOC, INLINE, CLASSES):
#     print(i)
#     print("---")
#     tree = parser.grammar.parse(i)
#     if tree:
#         print(tree.pretty())
#     else:
#         print("None")
#     print("---")
# print(backends.get_backend().codegen(DOC))
# print([item for item in collapse(tree) if item.startswith("___TMP_")])
