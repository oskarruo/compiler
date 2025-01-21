from compiler import ast
from compiler.tokenizer import Token, L

def parse(tokens: list[Token]) -> ast.Expression:
    if len(tokens) == 0:
        raise Exception(f'Parsing error: empty input tokens')

    depth = 0
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                loc=tokens[-1].loc,
                type="end",
                text=""
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'Parsing error at {token.loc.line}:{token.loc.column} expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'Parsing error at {token.loc.line}:{token.loc.column} expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token

    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected an integer literal')
        token = consume()
        return ast.Literal(value=int(token.text), location=token.loc)

    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected an identifier')
        token = consume()
        return ast.Identifier(name=token.text, location=token.loc)

    def parse_boolean() -> ast.Literal:
        if peek().type != 'boolean':
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected a boolean')
        token = consume()
        return ast.Literal(value=bool(token.text), location=token.loc)

    def parse_expression() -> ast.Expression:
        nonlocal depth
        depth += 1
        left = parse_or()

        while peek().text in ['=']:
            consume('=')
            right = parse_expression()
            left = ast.Assignement(
                left=left,
                right=right,
                location=left.location
            )
        if peek().type == "end" or peek().text in [')', 'then', 'else', ',', ';', '}', 'do']:
            depth -= 1
            return left
        else:
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}')

    def parse_or() -> ast.Expression:
        left = parse_and()

        while peek().text in ['or']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_and()
            left = ast.BinaryLogical(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left
        
    def parse_and() -> ast.Expression:
        left = parse_bool_opers_eq_neq()

        while peek().text in ['and']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_bool_opers_eq_neq()
            left = ast.BinaryLogical(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left

    def parse_bool_opers_eq_neq() -> ast.Expression:
        left = parse_bool_opers()

        while peek().text in ['==', '!=']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_bool_opers()
            left = ast.BinaryComp(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left

    def parse_bool_opers() -> ast.Expression:
        left = parse_pm()

        while peek().text in ['<', '<=', '>', '>=']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_pm()
            left = ast.BinaryComp(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left

    def parse_pm() -> ast.Expression:
        left = parse_term()

        while peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = ast.BinaryOp(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left

    def parse_term() -> ast.Expression:
        left = parse_unary()

        while peek().text in ['*', '/', '%']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_unary()
            left = ast.BinaryOp(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )
        return left
    
    def parse_unary() -> ast.Expression:
        while peek().text in ['-', 'not']:
            operator_token = consume()
            operator = operator_token.text
            operand = parse_unary()
            return ast.UnaryOp(
                op=operator,
                operand=operand,
                location=operand.location
            )
        return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'var':
            return parse_variable()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().text == 'while':
            return parse_while()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            ident = parse_identifier()
            if peek().text == '(':
                return parse_function(ident=ident)
            return ident
        elif peek().type == 'boolean':
            return parse_boolean()
        elif peek().text == '{':
            return parse_block()
        else:
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}')

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expression = parse_expression()
        consume(')')
        return expression
    
    def parse_variable() -> ast.Expression:
        if depth > 1:
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}')
        consume('var')
        ident = parse_identifier()
        type = None
        if peek().text == ':':
            consume(':')
            type = parse_identifier()
        consume('=')
        value = parse_expression()
        return ast.Variable(ident=ident, type=type, value=value, location=ident.location)

    def parse_if_expression() -> ast.Expression:
        consume('if')
        condition = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None
        return ast.IfExpression(condition=condition, then_clause=then_clause, else_clause=else_clause, location=condition.location)

    def parse_function(ident: ast.Identifier) -> ast.Expression:
        args = []
        consume('(')
        while peek().text != ')':
            args.append(parse_expression())
            if peek().text == ',':
                consume(',')
                if peek().text == ')':
                    raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected an argument')
        consume(')')
        return ast.Function(name=ident.name, arguments=args, location=ident.location)
    
    def parse_block() -> ast.Block:
        nonlocal depth
        old_depth = depth
        depth = 0

        expressions = []
        consume('{')
        res: ast.Expression = ast.Literal(value=None, location=L())
        while peek().text != '}':
            exp = parse_expression()
            if peek().text == ';':
                consume(';')
                expressions.append(exp)
            else:
                res = exp
        consume('}')

        loc = expressions[0].location if expressions else peek().loc

        depth = old_depth
        return ast.Block(expressions=expressions, result=res, location=loc)
    
    def parse_while() -> ast.While:
        consume('while')
        condition = parse_expression()
        consume('do')
        do_clause = parse_block()
        return ast.While(condition=condition, do_clause=do_clause, location=condition.location)
    
    def parse_top_level() -> ast.Expression:
        block = False
        expressions = []
        res: ast.Expression = ast.Literal(value=None, location=L())
        while pos < len(tokens):
            exp = parse_expression()
            if peek().text == ';':
                block = True
                consume(';')
                expressions.append(exp)
            else:
                res = exp

        loc = expressions[0].location if expressions else peek().loc

        if block:
            return ast.Block(expressions=expressions, result=res, location=loc)
        return res

    result = parse_top_level()

    if pos != len(tokens):
        remaining = tokens[pos:]
        raise Exception(f'Parsing error at {remaining[0].loc.line}:{remaining[0].loc.column}')

    return result
