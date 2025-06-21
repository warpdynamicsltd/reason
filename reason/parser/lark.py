from lark import Lark
from functools import cache


@cache
def get_lark_parser(code: str, start: str, lexer: str) -> Lark:
    return Lark(grammar=code, start=start, lexer=lexer, propagate_positions=True)
