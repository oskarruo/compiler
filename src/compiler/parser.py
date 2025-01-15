from compiler import ast
from compiler.tokenizer import Token

def parse(tokens: list[Token]) -> ast.Expression:
    if len(tokens) == 0:
        raise Exception(f'Parsing error: empty input tokens')

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
        return ast.Literal(int(token.text))
    
    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected an identifier')
        token = consume()
        return ast.Identifier(token.text)
    
    def parse_boolean() -> ast.Literal:
        if peek().type != 'boolean':
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}: expected a boolean')
        token = consume()
        return ast.Literal(bool(token.text))
    
    def parse_expression() -> ast.Expression:
        left = parse_term()

        while peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        if peek().type == "end" or peek().text in [')', 'then', 'else', ',']:
            return left
        else:
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}')
    
    def parse_term() -> ast.Expression:
        left = parse_factor()

        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expression = parse_expression()
        consume(')')
        return expression
    
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
        return ast.IfExpression(condition, then_clause, else_clause)
    
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
        return ast.Function(name=ident.name, arguments=args)

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            ident = parse_identifier()
            if peek().text == '(':
                return parse_function(ident=ident)
            return ident
        elif peek().type == 'boolean':
            return parse_boolean()
        else:
            raise Exception(f'Parsing error at {peek().loc.line}:{peek().loc.column}')
    
    result = parse_expression()

    if pos != len(tokens):
        remaining = tokens[pos:]
        raise Exception(f'Parsing error at {remaining[0].loc.line}:{remaining[0].loc.column}')

    return result
