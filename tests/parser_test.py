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
    with pytest.raises(Exception, match=r'Parsing error at 1:2'):
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

def test_parser_if_expression() -> None:
    assert parse(tokenize('if a then b + c else x * y')) == ast.IfExpression(
        condition=ast.Identifier(name="a"),
        then_clause=ast.BinaryOp(
            left=ast.Identifier(name="b"),
            op="+",
            right=ast.Identifier(name="c")
        ),
        else_clause=ast.BinaryOp(
            left=ast.Identifier(name="x"),
            op="*",
            right=ast.Identifier(name="y")
        )
    )
    return None

def test_parser_if_expression_no_else() -> None:
    assert parse(tokenize('if a then b + c')) == ast.IfExpression(
        condition=ast.Identifier(name="a"),
        then_clause=ast.BinaryOp(
            left=ast.Identifier(name="b"),
            op="+",
            right=ast.Identifier(name="c")
        ),
        else_clause=None
    )
    return None

def test_parser_if_as_part_of_other_expression() -> None:
    assert parse(tokenize('1 + if true then 2 else 3')) == ast.BinaryOp(
        left=ast.Literal(value=1),
        op='+',
        right=ast.IfExpression(
            condition=ast.Literal(value=True),
            then_clause=ast.Literal(value=2),
            else_clause=ast.Literal(value=3)
        )
    )
    return None

def test_parser_nested_if() -> None:
    assert parse(tokenize('1 + if if b then c + 1 else d + 3 then 2')) == ast.BinaryOp(
        left=ast.Literal(value=1),
        op='+',
        right=ast.IfExpression(
            condition=ast.IfExpression(
                condition=ast.Identifier(name="b"),
                then_clause=ast.BinaryOp(
                    left=ast.Identifier(name="c"),
                    op="+",
                    right=ast.Literal(value=1)
                    ),
                else_clause=ast.BinaryOp(
                    left=ast.Identifier(name="d"),
                    op="+",
                    right=ast.Literal(value=3)
                    ),
            ),
            then_clause=ast.Literal(value=2),
            else_clause=None
        )
    )
    return None

def test_parser_if_expression_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:16'):
        parse(tokenize('if a then then b + c else x * y'))
    return None

def test_parser_function() -> None:
    assert parse(tokenize('f(x, y + z)')) == ast.Function(
        name='f',
        arguments=[
            ast.Identifier(name="x"),
            ast.BinaryOp(
                left=ast.Identifier(name='y'),
                op='+',
                right=ast.Identifier(name='z')
            )
        ]
    )
    return None

def test_parser_function_arguments_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:5: expected an argument'):
        parse(tokenize('f(x,)'))
    return None

def test_parser_function_parentheses_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:4'):
        parse(tokenize('f(x,'))
    return None