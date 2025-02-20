import pytest
from compiler.tokenizer import tokenize
from compiler.parser import parse
import compiler.ast as ast
from compiler.tokenizer import L


def test_parser_simple() -> None:
    assert parse(tokenize("a + b")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Identifier(name="a", location=L()),
                op="+",
                right=ast.Identifier(name="b", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_multiplication() -> None:
    assert parse(tokenize("a * b")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Identifier(name="a", location=L()),
                op="*",
                right=ast.Identifier(name="b", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_multiplication_and_addition() -> None:
    assert parse(tokenize("a + b * c")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Identifier(name="a", location=L()),
                op="+",
                right=ast.BinaryOp(
                    left=ast.Identifier(name="b", location=L()),
                    op="*",
                    right=ast.Identifier(name="c", location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_parentheses() -> None:
    assert parse(tokenize("(a + b) * c")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.BinaryOp(
                    left=ast.Identifier(name="a", location=L()),
                    op="+",
                    right=ast.Identifier(name="b", location=L()),
                    location=L(),
                ),
                op="*",
                right=ast.Identifier(name="c", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_multiple_parentheses() -> None:
    assert parse(tokenize("(a + b) * (c + d)")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.BinaryOp(
                    left=ast.Identifier(name="a", location=L()),
                    op="+",
                    right=ast.Identifier(name="b", location=L()),
                    location=L(),
                ),
                op="*",
                right=ast.BinaryOp(
                    left=ast.Identifier(name="c", location=L()),
                    op="+",
                    right=ast.Identifier(name="d", location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_parentheses_inside_another() -> None:
    assert parse(tokenize("((a + b) * (4 - 2)) * 7")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.BinaryOp(
                    left=ast.BinaryOp(
                        left=ast.Identifier(name="a", location=L()),
                        op="+",
                        right=ast.Identifier(name="b", location=L()),
                        location=L(),
                    ),
                    op="*",
                    right=ast.BinaryOp(
                        left=ast.Literal(value=4, location=L()),
                        op="-",
                        right=ast.Literal(value=2, location=L()),
                        location=L(),
                    ),
                    location=L(),
                ),
                op="*",
                right=ast.Literal(value=7, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_parentheses_close_fail() -> None:
    with pytest.raises(Exception, match=r'Parsing error at 1:17 expected "\)"'):
        parse(tokenize("(a + b) + ( c * d"))
    return None


def test_parser_parentheses_open_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:8"):
        parse(tokenize("(a + b)) * c"))
    return None


def test_parser_empty_parentheses_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:2"):
        parse(tokenize("() * c"))
    return None


def test_parser_fail_pm_end() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:7"):
        parse(tokenize("a + b c"))
    return None


def test_parser_fail_pm_beginning() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:3"):
        parse(tokenize("a b - c"))
    return None


def test_parser_fail_proddiv_end() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:7"):
        parse(tokenize("a * b c"))
    return None


def test_parser_fail_proddiv_beginning() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:3"):
        parse(tokenize("a b / c"))
    return None


def test_parser_fail_empty_tokens() -> None:
    with pytest.raises(Exception, match=r"Parsing error: empty input tokens"):
        parse(tokenize(""))
    return None


def test_parser_if_expression() -> None:
    assert parse(tokenize("if a then b + c else x * y")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.IfExpression(
                condition=ast.Identifier(name="a", location=L()),
                then_clause=ast.BinaryOp(
                    left=ast.Identifier(name="b", location=L()),
                    op="+",
                    right=ast.Identifier(name="c", location=L()),
                    location=L(),
                ),
                else_clause=ast.BinaryOp(
                    left=ast.Identifier(name="x", location=L()),
                    op="*",
                    right=ast.Identifier(name="y", location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_if_expression_no_else() -> None:
    assert parse(tokenize("if a then b + c")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.IfExpression(
                condition=ast.Identifier(name="a", location=L()),
                then_clause=ast.BinaryOp(
                    left=ast.Identifier(name="b", location=L()),
                    op="+",
                    right=ast.Identifier(name="c", location=L()),
                    location=L(),
                ),
                else_clause=None,
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_if_as_part_of_other_expression() -> None:
    assert parse(tokenize("1 + if true then 2 else 3")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Literal(value=1, location=L()),
                op="+",
                right=ast.IfExpression(
                    condition=ast.Literal(value=True, location=L()),
                    then_clause=ast.Literal(value=2, location=L()),
                    else_clause=ast.Literal(value=3, location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_nested_if() -> None:
    assert parse(tokenize("1 + if if b then c + 1 else d + 3 then 2")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Literal(value=1, location=L()),
                op="+",
                right=ast.IfExpression(
                    condition=ast.IfExpression(
                        condition=ast.Identifier(name="b", location=L()),
                        then_clause=ast.BinaryOp(
                            left=ast.Identifier(name="c", location=L()),
                            op="+",
                            right=ast.Literal(value=1, location=L()),
                            location=L(),
                        ),
                        else_clause=ast.BinaryOp(
                            left=ast.Identifier(name="d", location=L()),
                            op="+",
                            right=ast.Literal(value=3, location=L()),
                            location=L(),
                        ),
                        location=L(),
                    ),
                    then_clause=ast.Literal(value=2, location=L()),
                    else_clause=None,
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_if_expression_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:16"):
        parse(tokenize("if a then then b + c else x * y"))
    return None


def test_parser_function() -> None:
    assert parse(tokenize("f(x, y + z)")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Function(
                name="f",
                arguments=[
                    ast.Identifier(name="x", location=L()),
                    ast.BinaryOp(
                        left=ast.Identifier(name="y", location=L()),
                        op="+",
                        right=ast.Identifier(name="z", location=L()),
                        location=L(),
                    ),
                ],
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_function_no_args() -> None:
    assert parse(tokenize("f()")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Function(name="f", arguments=[], location=L()),
            location=L(),
        ),
    )
    return None


def test_parser_function_arguments_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:5: expected an argument"):
        parse(tokenize("f(x,)"))
    return None


def test_parser_function_parentheses_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:4"):
        parse(tokenize("f(x,"))
    return None


def test_parser_remainder() -> None:
    assert parse(tokenize("a % 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Identifier(name="a", location=L()),
                op="%",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_bool_opers_eq_neq() -> None:
    assert parse(tokenize("a == 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op="==",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    assert parse(tokenize("a != 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op="!=",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_rest_bool_opers() -> None:
    assert parse(tokenize("a < 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op="<",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    assert parse(tokenize("a <= 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op="<=",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    assert parse(tokenize("a > 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op=">",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    assert parse(tokenize("a >= 5")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryComp(
                left=ast.Identifier(name="a", location=L()),
                op=">=",
                right=ast.Literal(value=5, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_bool_log_opers() -> None:
    assert parse(tokenize("a and b")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryLogical(
                left=ast.Identifier(name="a", location=L()),
                op="and",
                right=ast.Identifier(name="b", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_new_opers_with_other() -> None:
    assert parse(tokenize("if a or (b - 5 < 5) then c % 3")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.IfExpression(
                condition=ast.BinaryLogical(
                    left=ast.Identifier(name="a", location=L()),
                    op="or",
                    right=ast.BinaryComp(
                        left=ast.BinaryOp(
                            left=ast.Identifier(name="b", location=L()),
                            op="-",
                            right=ast.Literal(value=5, location=L()),
                            location=L(),
                        ),
                        op="<",
                        right=ast.Literal(value=5, location=L()),
                        location=L(),
                    ),
                    location=L(),
                ),
                then_clause=ast.BinaryOp(
                    left=ast.Identifier(name="c", location=L()),
                    op="%",
                    right=ast.Literal(value=3, location=L()),
                    location=L(),
                ),
                else_clause=None,
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_assignement() -> None:
    assert parse(tokenize("a=b=c")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Assignement(
                left=ast.Identifier(name="a", location=L()),
                right=ast.Assignement(
                    left=ast.Identifier(name="b", location=L()),
                    right=ast.Identifier(name="c", location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_unary() -> None:
    assert parse(tokenize("if not - c then b")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.IfExpression(
                condition=ast.UnaryOp(
                    op="not",
                    operand=ast.UnaryOp(
                        op="-",
                        operand=ast.Identifier(name="c", location=L()),
                        location=L(),
                    ),
                    location=L(),
                ),
                then_clause=ast.Identifier(name="b", location=L()),
                else_clause=None,
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_block() -> None:
    assert parse(tokenize("{a = 1; x}")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.Assignement(
                        left=ast.Identifier(name="a", location=L()),
                        right=ast.Literal(value=1, location=L()),
                        location=L(),
                    )
                ],
                result=ast.Identifier(name="x", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_while() -> None:
    assert parse(tokenize("while x < 10 do { x = x + 1; }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.While(
                condition=ast.BinaryComp(
                    left=ast.Identifier(name="x", location=L()),
                    op="<",
                    right=ast.Literal(value=10, location=L()),
                    location=L(),
                ),
                do_clause=ast.Block(
                    expressions=[
                        ast.Assignement(
                            left=ast.Identifier(name="x", location=L()),
                            right=ast.BinaryOp(
                                left=ast.Identifier(name="x", location=L()),
                                op="+",
                                right=ast.Literal(value=1, location=L()),
                                location=L(),
                            ),
                            location=L(),
                        )
                    ],
                    result=ast.Literal(value=None, location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_variable() -> None:
    assert parse(tokenize("var x = 123")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Variable(
                ident=ast.Identifier(name="x", location=L()),
                type_declaration=None,
                value=ast.Literal(value=123, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_variable_inside_expression_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:11"):
        parse(tokenize("if x then var x = 123"))
    return None


def test_parser_variable_inside_block_fail() -> None:
    with pytest.raises(Exception, match=r"Parsing error at 1:13"):
        parse(tokenize("{ if x then var x = 123 }"))
    return None


def test_parser_variable_inside_block() -> None:
    assert parse(tokenize("{ var x = 123; var y = 123; }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.Variable(
                        ident=ast.Identifier(name="x", location=L()),
                        type_declaration=None,
                        value=ast.Literal(value=123, location=L()),
                        location=L(),
                    ),
                    ast.Variable(
                        ident=ast.Identifier(name="y", location=L()),
                        type_declaration=None,
                        value=ast.Literal(value=123, location=L()),
                        location=L(),
                    ),
                ],
                result=ast.Literal(value=None, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_variable_with_type() -> None:
    assert parse(tokenize("var x: int = 123")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Variable(
                ident=ast.Identifier(name="x", location=L()),
                type_declaration=ast.Identifier(name="int", location=L()),
                value=ast.Literal(value=123, location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_multiple_top_level() -> None:
    assert parse(tokenize("x; y; z")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[
                ast.Identifier(name="x", location=L()),
                ast.Identifier(name="y", location=L()),
            ],
            result=ast.Identifier(name="z", location=L()),
            location=L(),
        ),
    )
    return None


def test_parser_expression_many_operators() -> None:
    assert parse(tokenize("1 + if true then 2 else 3")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.BinaryOp(
                left=ast.Literal(value=1, location=L()),
                op="+",
                right=ast.IfExpression(
                    condition=ast.Literal(value=True, location=L()),
                    then_clause=ast.Literal(value=2, location=L()),
                    else_clause=ast.Literal(value=3, location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_semicolons() -> None:
    assert parse(tokenize("{ { x } { y } }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.Block(
                        expressions=[],
                        result=ast.Identifier(name="x", location=L()),
                        location=L(),
                    )
                ],
                result=ast.Block(
                    expressions=[],
                    result=ast.Identifier(name="y", location=L()),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )

    with pytest.raises(Exception, match=r"Parsing error at 1:5"):
        parse(tokenize("{ a b}"))

    assert parse(tokenize("{ if true then { a } b }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.IfExpression(
                        condition=ast.Literal(value=True, location=L()),
                        then_clause=ast.Block(
                            expressions=[],
                            result=ast.Identifier(name="a", location=L()),
                            location=L(),
                        ),
                        else_clause=None,
                        location=L(),
                    )
                ],
                result=ast.Identifier(name="b", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )

    assert parse(tokenize("{ if true then { a }; b }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.IfExpression(
                        condition=ast.Literal(value=True, location=L()),
                        then_clause=ast.Block(
                            expressions=[],
                            result=ast.Identifier(name="a", location=L()),
                            location=L(),
                        ),
                        else_clause=None,
                        location=L(),
                    )
                ],
                result=ast.Identifier(name="b", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )

    with pytest.raises(Exception, match=r"Parsing error at 1:24"):
        parse(tokenize("{ if true then { a } b c }"))

    assert parse(tokenize("{ if true then { a } b; c }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.IfExpression(
                        condition=ast.Literal(value=True, location=L()),
                        then_clause=ast.Block(
                            expressions=[],
                            result=ast.Identifier(name="a", location=L()),
                            location=L(),
                        ),
                        else_clause=None,
                        location=L(),
                    ),
                    ast.Identifier(name="b", location=L()),
                ],
                result=ast.Identifier(name="c", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )

    assert parse(tokenize("{ if true then { a } else { b } c }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Block(
                expressions=[
                    ast.IfExpression(
                        condition=ast.Literal(value=True, location=L()),
                        then_clause=ast.Block(
                            expressions=[],
                            result=ast.Identifier(name="a", location=L()),
                            location=L(),
                        ),
                        else_clause=ast.Block(
                            expressions=[],
                            result=ast.Identifier(name="b", location=L()),
                            location=L(),
                        ),
                        location=L(),
                    )
                ],
                result=ast.Identifier(name="c", location=L()),
                location=L(),
            ),
            location=L(),
        ),
    )

    assert parse(tokenize("x = { { f(a) } { b } }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.Assignement(
                left=ast.Identifier(name="x", location=L()),
                right=ast.Block(
                    expressions=[
                        ast.Block(
                            expressions=[],
                            result=ast.Function(
                                name="f",
                                arguments=[ast.Identifier(name="a", location=L())],
                                location=L(),
                            ),
                            location=L(),
                        )
                    ],
                    result=ast.Block(
                        expressions=[],
                        result=ast.Identifier(name="b", location=L()),
                        location=L(),
                    ),
                    location=L(),
                ),
                location=L(),
            ),
            location=L(),
        ),
    )


def test_parser_break_continue() -> None:
    assert parse(tokenize("while true do { break }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.While(
                condition=ast.Literal(value=True, location=L()),
                do_clause=ast.Block(
                    expressions=[], result=ast.Break(location=L()), location=L()
                ),
                location=L(),
            ),
            location=L(),
        ),
    )

    assert parse(tokenize("while true do { continue }")) == ast.Module(
        funs=[],
        body=ast.Block(
            expressions=[],
            result=ast.While(
                condition=ast.Literal(value=True, location=L()),
                do_clause=ast.Block(
                    expressions=[], result=ast.Continue(location=L()), location=L()
                ),
                location=L(),
            ),
            location=L(),
        ),
    )
    return None


def test_parser_function_def() -> None:
    assert parse(
        tokenize("fun square(x: Int): Int { return x * x; } square(2);")
    ) == ast.Module(
        funs=[
            ast.FunDef(
                location=L(),
                name="square",
                params=[
                    ast.FunDefArg(
                        name="x", type=ast.Identifier(name="Int", location=L())
                    )
                ],
                return_type=ast.Identifier(name="Int", location=L()),
                body=ast.Block(
                    expressions=[
                        ast.ReturnExpression(
                            value=ast.BinaryOp(
                                left=ast.Identifier(name="x", location=L()),
                                op="*",
                                right=ast.Identifier(name="x", location=L()),
                                location=L(),
                            ),
                            location=L(),
                        )
                    ],
                    result=ast.Literal(value=None, location=L()),
                    location=L(),
                ),
            )
        ],
        body=ast.Block(
            expressions=[
                ast.Function(
                    name="square",
                    arguments=[ast.Literal(value=2, location=L())],
                    location=L(),
                )
            ],
            result=ast.Literal(value=None, location=L()),
            location=L(),
        ),
    )
    return None
