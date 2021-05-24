import functools
from pathlib import Path

import jinja2
import lark


def parse_string(string: str) -> str:
    return string


def get_jinja_env(file: str) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(Path(file).parent / "templates")),
        autoescape=False,
    )


inline = functools.partial(lark.v_args, inline=True)()
