import enum
import sys
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union,
    Callable,
)

import jinja2
import lark
from lark import Transformer, ast_utils, v_args

from . import env

this_module = sys.modules[__name__]


class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


_StmtImport = _Declaration = _Action = _Value = _Ast


class Xlist(list, _Ast, ast_utils.AsList):
    pass


Args = FdecArgs = GenTypes = Xlist


class ArgType(enum.Enum):
    NORMAL = enum.auto()
    VARIADIC = enum.auto()
    KEYWORD_VARIADIC = enum.auto()


@dataclass
class FdecArg(_Ast):
    name: str
    arg_type: ArgType = ArgType.NORMAL
    default: Optional[_Value] = None


class _Computed(_Ast):
    ...


class CompiledFunctionEnum(enum.Enum):
    INLINE = "INLINE"
    DEFINED = "DEFINED"


@dataclass
class Namespacing(ast_utils.AsList, _Value):
    path: List[str]


class FunctionSignature(NamedTuple):
    name: str
    args: FdecArgs
    doc: Optional[str] = None


@dataclass
class ComputedFunction(_Computed):
    compiled_format: Union[jinja2.Template, Callable[[Any], str]]
    path: Namespacing
    signature: FunctionSignature
    type_of_function: CompiledFunctionEnum = CompiledFunctionEnum.INLINE


class Module(NamedTuple):
    name: str
    path: str
    contents: List[_Value]


global global_values
global_values = []  # type: List[Union[_Value, _Computed]]


def import_resolve(module_name: str) -> Module:
    if module_name in STDLIB:

        add_this = [
            item
            for item in STDLIB[module_name]
            if isinstance(item, ComputedFunction)  # TODO: "Exported"
        ]
        global_values.extend(add_this)
        return Module(
            module_name,
            "<stdlib>",
            add_this,
        )
    else:
        raise RuntimeError(f"Could not resolve module {module_name}")


@dataclass
class NormalImport(_Ast):
    imported_list: List[Module]

    def __init__(self, *import_names: str) -> None:
        self.imported_list = list(map(import_resolve, import_names))


T = TypeVar("T")
A = TypeVar("A")


class StaticNamespacing(Namespacing):
    pass


@dataclass
class Lshift(_Action):
    left: _Value
    right: _Value


@dataclass
class Arg(_Ast):
    keyword_name: Optional[str]
    value: Namespacing


def _(x: lark.Tree) -> List[Union[str, lark.Tree]]:
    return x.children


def resolve_for(name: Namespacing) -> _Computed:
    output = [value for value in global_values if value.path == name]
    # assert len(output) == 1, (name, output)
    return output[0]


@dataclass
class CallOp(_Action):
    name: Namespacing
    args: Args

    def __compile__(self) -> str:
        resolved_func = resolve_for(self.name)
        assert isinstance(resolved_func, ComputedFunction)
        return resolved_func.compiled_format.render(args=(self.args))


@dataclass
class FunctionDeclaration(_Declaration):
    name: str
    generic_types: Optional[str]
    args: List[FdecArg]
    output_type: str = "None"


@dataclass
class CodeBlock(_Ast, ast_utils.AsList, Generic[A]):
    contents: Tuple[A]


@dataclass
class FfiImport(_Ast, ast_utils.AsList):
    imported: List[str]


@dataclass(init=False)
class GenType(_Ast):
    name: str
    args: List[str]

    def __init__(self, name: str, *args: str):
        self.name = name
        self.args = list(args)


class RefType(_Ast, NamedTuple):
    inner_type: str


@dataclass
class Main(_Ast):
    code: CodeBlock[Union[_Declaration, _StmtImport]]


class ToAst(Transformer):
    IDENTIFIER = str

    @v_args(inline=True)
    def IMPORTABLE(self, thing: str) -> str:
        if thing[0] == thing[-1] and thing[0] in {"'", '"'}:
            return str(thing)[1:-1]
        return str(thing)

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    @v_args(inline=True)
    def start(
        self,
        program_decl: Optional[List[Any]],
        main: Optional[Main],
    ):
        return {"main": main, "code": program_decl.children}


transformer = ast_utils.create_transformer(this_module, ToAst())
STDLIB: Dict[str, List[Union[ComputedFunction]]] = {
    "io": [
        ComputedFunction(
            env.get_template("stdlib/io/println.jinja"),
            Namespacing(["io", "println"]),
            FunctionSignature(
                "println", FdecArgs([FdecArg("objects", arg_type=...)]), "DOCS HERE"
            ),
        ),
        ComputedFunction(
            env.get_template("stdlib/io/print.jinja"),
            Namespacing(["io", "print"]),
            FunctionSignature(
                "print", FdecArgs([FdecArg("objects", arg_type=...)]), "DOCS HERE"
            ),
        ),
    ]
}
