from compiler import ast
from compiler.tokenizer import Token, L


def parse(tokens: list[Token]) -> ast.Module:
    if len(tokens) == 0:
        raise Exception("Parsing error: empty input tokens")

    depth = 0
    pos = 0
    prev_block = False
    in_then_expr = False
    if_then_block = False
    in_else_expr = False
    if_else_block = False
    if_ends_in_block = False
    while_ends_in_block = False
    var_ends_in_block = False

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(loc=tokens[-1].loc, type="end", text="")

    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(
                f'Parsing error at {token.loc.line}:{token.loc.column} expected "{expected}"'
            )
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(
                f"Parsing error at {token.loc.line}:{token.loc.column} expected one of: {comma_separated}"
            )
        nonlocal pos
        pos += 1
        return token

    def parse_int_literal() -> ast.Literal:
        if peek().type != "int_literal":
            raise Exception(
                f"Parsing error at {peek().loc.line}:{peek().loc.column}: expected an integer literal"
            )
        token = consume()
        return ast.Literal(value=int(token.text), location=token.loc)

    def parse_identifier() -> ast.Identifier:
        if peek().type != "identifier":
            raise Exception(
                f"Parsing error at {peek().loc.line}:{peek().loc.column}: expected an identifier"
            )
        token = consume()
        return ast.Identifier(name=token.text, location=token.loc)

    def parse_boolean() -> ast.Literal:
        if peek().type != "boolean":
            raise Exception(
                f"Parsing error at {peek().loc.line}:{peek().loc.column}: expected a boolean"
            )
        token = consume()
        if token.text == "true":
            return ast.Literal(value=True, location=token.loc)
        return ast.Literal(value=False, location=token.loc)

    def parse_expression() -> ast.Expression:
        nonlocal \
            depth, \
            prev_block, \
            if_ends_in_block, \
            while_ends_in_block, \
            var_ends_in_block
        depth += 1
        left = parse_or()

        while peek().text in ["="]:
            consume("=")
            right = parse_expression()
            left = ast.Assignement(left=left, right=right, location=left.location)
        if (
            peek().type == "end"
            or peek().text
            in [
                ")",
                "then",
                "else",
                ",",
                ";",
                "}",
                "do",
                "print_int",
                "print_bool",
                "read_int",
            ]
            or prev_block
            or if_ends_in_block
            or while_ends_in_block
            or var_ends_in_block
        ):
            while_ends_in_block = False
            if_ends_in_block = False
            prev_block = False
            var_ends_in_block = False
            depth -= 1
            return left
        else:
            raise Exception(f"Parsing error at {peek().loc.line}:{peek().loc.column}")

    def parse_or() -> ast.Expression:
        left = parse_and()

        while peek().text in ["or"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_and()
            left = ast.BinaryLogical(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_and() -> ast.Expression:
        left = parse_bool_opers_eq_neq()

        while peek().text in ["and"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_bool_opers_eq_neq()
            left = ast.BinaryLogical(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_bool_opers_eq_neq() -> ast.Expression:
        left = parse_bool_opers()

        while peek().text in ["==", "!="]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_bool_opers()
            left = ast.BinaryComp(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_bool_opers() -> ast.Expression:
        left = parse_pm()

        while peek().text in ["<", "<=", ">", ">="]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_pm()
            left = ast.BinaryComp(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_pm() -> ast.Expression:
        left = parse_term()

        while peek().text in ["+", "-"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = ast.BinaryOp(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_term() -> ast.Expression:
        left = parse_unary()

        while peek().text in ["*", "/", "%"]:
            operator_token = consume()
            operator = operator_token.text
            right = parse_unary()
            left = ast.BinaryOp(
                left=left, op=operator, right=right, location=left.location
            )
        return left

    def parse_unary() -> ast.Expression:
        while peek().text in ["-", "not"]:
            operator_token = consume()
            operator = operator_token.text
            operand = parse_unary()
            return ast.UnaryOp(op=operator, operand=operand, location=operand.location)
        return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == "(":
            return parse_parenthesized()
        elif peek().text == "return":
            return parse_return_expression()
        elif peek().text == "var":
            return parse_variable()
        elif peek().text == "if":
            return parse_if_expression()
        elif peek().text == "while":
            return parse_while()
        elif peek().text == "break":
            return parse_break()
        elif peek().text == "continue":
            return parse_continue()
        elif peek().type == "int_literal":
            return parse_int_literal()
        elif peek().type == "identifier":
            ident = parse_identifier()
            if peek().text == "(":
                return parse_function(ident=ident)
            return ident
        elif peek().type == "boolean":
            return parse_boolean()
        elif peek().text == "{":
            return parse_block()
        else:
            raise Exception(f"Parsing error at {peek().loc.line}:{peek().loc.column}")

    def parse_return_expression() -> ast.ReturnExpression:
        consume("return")
        expression = parse_expression()
        return ast.ReturnExpression(value=expression, location=expression.location)

    def parse_break() -> ast.Break:
        token = consume("break")
        return ast.Break(location=token.loc)

    def parse_continue() -> ast.Continue:
        token = consume("continue")
        return ast.Continue(location=token.loc)

    def parse_parenthesized() -> ast.Expression:
        consume("(")
        expression = parse_expression()
        consume(")")
        return expression

    def parse_variable() -> ast.Expression:
        nonlocal var_ends_in_block
        if depth > 1:
            raise Exception(f"Parsing error at {peek().loc.line}:{peek().loc.column}")
        consume("var")
        ident = parse_identifier()
        type = None
        if peek().text == ":":
            consume(":")
            type = parse_identifier()
        consume("=")
        value = parse_expression()
        if isinstance(value, ast.Block):
            var_ends_in_block = True
        return ast.Variable(
            ident=ident, type_declaration=type, value=value, location=ident.location
        )

    def parse_if_expression() -> ast.Expression:
        nonlocal \
            in_then_expr, \
            in_else_expr, \
            if_then_block, \
            if_else_block, \
            if_ends_in_block
        consume("if")
        condition = parse_expression()

        in_then_expr = True
        consume("then")
        then_clause = parse_expression()
        in_then_expr = False

        if peek().text == "else":
            consume("else")
            in_else_expr = True
            else_clause = parse_expression()
            in_else_expr = False

            if if_else_block:
                if_ends_in_block = True
            if_else_block = False
        else:
            if if_then_block:
                if_ends_in_block = True
            if_then_block = False
            else_clause = None

        return ast.IfExpression(
            condition=condition,
            then_clause=then_clause,
            else_clause=else_clause,
            location=condition.location,
        )

    def parse_function(ident: ast.Identifier) -> ast.Expression:
        args = []
        consume("(")
        while peek().text != ")":
            args.append(parse_expression())
            if peek().text == ",":
                consume(",")
                if peek().text == ")":
                    raise Exception(
                        f"Parsing error at {peek().loc.line}:{peek().loc.column}: expected an argument"
                    )
        consume(")")
        return ast.Function(name=ident.name, arguments=args, location=ident.location)

    def parse_block() -> ast.Block:
        nonlocal \
            depth, \
            prev_block, \
            in_then_expr, \
            in_else_expr, \
            if_then_block, \
            if_else_block
        if in_then_expr:
            if_then_block = True
        if in_else_expr:
            if_else_block = True

        old_depth = depth
        depth = 0

        expressions = []
        consume("{")
        res: ast.Expression = ast.Literal(value=None, location=L())
        exp: ast.Expression = ast.Literal(value=None, location=L())
        last_result = False
        while peek().text != "}":
            last_result = True
            exp = parse_expression()
            if peek().text == ";":
                consume(";")
                last_result = False
            if peek().text == "}":
                break
            expressions.append(exp)
        if last_result:
            res = exp
        else:
            expressions.append(exp)
        consume("}")

        loc = expressions[0].location if expressions else peek().loc

        depth = old_depth
        prev_block = True
        return ast.Block(expressions=expressions, result=res, location=loc)

    def parse_while() -> ast.While:
        nonlocal while_ends_in_block
        consume("while")
        condition = parse_expression()
        consume("do")
        do_clause = parse_expression()
        if isinstance(do_clause, ast.Block):
            while_ends_in_block = True
        return ast.While(
            condition=condition, do_clause=do_clause, location=condition.location
        )

    def parse_top_level() -> ast.Expression:
        expressions = []
        res: ast.Expression = ast.Literal(value=None, location=L())
        while pos < len(tokens):
            last_result = True
            exp = parse_expression()
            if peek().text == ";":
                consume(";")
                last_result = False
            if peek().type == "end":
                break
            expressions.append(exp)

        if last_result:
            res = exp
        else:
            expressions.append(exp)

        loc = expressions[0].location if expressions else res.location
        return ast.Block(expressions=expressions, result=res, location=loc)

    def parse_function_def() -> ast.FunDef:
        consume("fun")
        ident = parse_identifier()
        args = []
        consume("(")
        while peek().text != ")":
            var_ident = parse_identifier()
            consume(":")
            var_type = parse_identifier()
            args.append(ast.FunDefArg(name=var_ident.name, type=var_type))

            if peek().text == ",":
                consume(",")
                if peek().text == ")":
                    raise Exception(
                        f"Parsing error at {peek().loc.line}:{peek().loc.column}: expected an argument"
                    )
        consume(")")
        consume(":")
        type = parse_identifier()
        body = parse_expression()
        return ast.FunDef(ident.location, ident.name, args, type, body)

    def parse_top_module() -> ast.Module:
        functions = []
        while peek().text == "fun":
            fun = parse_function_def()
            functions.append(fun)
        top_expr = parse_top_level()
        return ast.Module(functions, top_expr)

    result = parse_top_module()

    if pos != len(tokens):
        remaining = tokens[pos:]
        raise Exception(
            f"Parsing error at {remaining[0].loc.line}:{remaining[0].loc.column}"
        )

    return result
