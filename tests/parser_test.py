import pytest
from compiler.tokenizer import tokenize
from compiler.tokenizer import Token
from compiler.tokenizer import Location
from compiler.tokenizer import L
from compiler.parser import parse
import compiler.ast as ast

def test_parser_simple() -> None:
    assert parse(tokenize('a + b')) == ast.BinaryOp(
        left=ast.Identifier(name="a"),
        op="+",
        right=ast.Identifier(name="b")
    )
    return None

def test_parser_multiplication() -> None:
    assert parse(tokenize('a * b')) == ast.BinaryOp(
        left=ast.Identifier(name="a"),
        op="*",
        right=ast.Identifier(name="b")
    )
    return None

def test_parser_multiplication_and_addition() -> None:
    assert parse(tokenize('a + b * c')) == ast.BinaryOp(
        left=ast.Identifier(name="a"),
        op="+",
        right=ast.BinaryOp(
            left=ast.Identifier(name="b"),
            op="*",
            right=ast.Identifier(name="c")
            )
    )
    return None

def test_parser_parentheses() -> None:
    assert parse(tokenize('(a + b) * c')) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name="a"),
            op="+",
            right=ast.Identifier(name="b")
            ),
        op="*",
        right=ast.Identifier(name="c")
    )
    return None

def test_parser_multiple_parentheses() -> None:
    assert parse(tokenize('(a + b) * (c + d)')) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.Identifier(name="a"),
            op="+",
            right=ast.Identifier(name="b")
            ),
        op="*",
        right=ast.BinaryOp(
            left=ast.Identifier(name="c"),
            op="+",
            right=ast.Identifier(name="d")
            )
    )
    return None

def test_parser_parentheses_inside_another() -> None:
    assert parse(tokenize('((a + b) * (4 - 2)) * 7')) == ast.BinaryOp(
        left=ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Identifier(name="a"),
                op="+",
                right=ast.Identifier(name="b")
            ),
            op="*",
            right=ast.BinaryOp(
                left=ast.Literal(value=4),
                op="-",
                right=ast.Literal(value=2)
            )
            ),
        op="*",
        right=ast.Literal(value=7)
    )
    return None

def test_parser_parentheses_close_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:17 expected "\)"'):
        parse(tokenize('(a + b) + ( c * d'))
    return None

def test_parser_parentheses_open_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:8'):
        parse(tokenize('(a + b)) * c'))
    return None

def test_parser_empty_parentheses_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:2: expected an integer literal or an identifier'):
        parse(tokenize('() * c'))
    return None

def test_parser_fail_pm_end() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:7'):
        parse(tokenize('a + b c'))
    return None

def test_parser_fail_pm_beginning() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:3'):
        parse(tokenize('a b - c'))
    return None

def test_parser_fail_proddiv_end() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:7'):
        parse(tokenize('a * b c'))
    return None

def test_parser_fail_proddiv_beginning() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:3'):
        parse(tokenize('a b / c'))
    return None

def test_parser_fail_empty_tokens() -> None:
    with pytest.raises(Exception, match=r'Parsing error: empty input tokens'):
        parse(tokenize(''))
    return None
