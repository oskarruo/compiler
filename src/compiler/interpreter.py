from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from compiler import ast

Value = int | bool | Callable | None


class BreakExpection(Exception):
    pass


class ContinueExpection(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value: Value) -> None:
        self.value = value


@dataclass
class SymTab:
    locals: dict
    parent: SymTab | None


def top_level_symtab() -> SymTab:
    return SymTab(
        locals={
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a // b,
            "%": lambda a, b: a % b,
            "unary_-": lambda a: -a,
            "unary_not": lambda a: not a,
        },
        parent=None,
    )


def interpret(node: ast.Module | ast.Expression, tbl: SymTab | None = None) -> Value:
    table = tbl if tbl is not None else top_level_symtab()

    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node=node.left, tbl=table)
            b: Any = interpret(node=node.right, tbl=table)

            current_table = table
            while current_table.parent is not None:
                current_table = current_table.parent
            if node.op in current_table.locals:
                return current_table.locals[node.op](a, b)
            else:
                raise Exception(f"Unknown operator: {node.op}")

        case ast.BinaryComp():
            c: Any = interpret(node=node.left, tbl=table)
            d: Any = interpret(node=node.right, tbl=table)

            current_table = table
            while current_table.parent is not None:
                current_table = current_table.parent
            if node.op in current_table.locals:
                return current_table.locals[node.op](c, d)
            else:
                raise Exception(f"Unknown operator: {node.op}")

        case ast.BinaryLogical():
            e: Any = interpret(node=node.left, tbl=table)

            if node.op == "and":
                if not e:
                    return False
                f: Any = interpret(node=node.right, tbl=table)
                if f:
                    return True
                return False
            elif node.op == "or":
                if e:
                    return True
                g: Any = interpret(node=node.right, tbl=table)
                if g:
                    return True
                return False
            else:
                raise Exception(f"Unknown operator: {node.op}")

        case ast.UnaryOp():
            h: Any = interpret(node=node.operand, tbl=table)

            current_table = table
            while current_table.parent is not None:
                current_table = current_table.parent
            if "unary_" + node.op in current_table.locals:
                return current_table.locals["unary_" + node.op](h)
            else:
                raise Exception(f"Unknown operator: {node.op}")

        case ast.IfExpression():
            if node.else_clause is not None:
                if interpret(node=node.condition, tbl=table):
                    return interpret(node=node.then_clause, tbl=table)
                else:
                    return interpret(node=node.else_clause, tbl=table)
            else:
                if interpret(node=node.condition, tbl=table):
                    return interpret(node=node.then_clause, tbl=table)
                return None

        case ast.Function():
            match node.name:
                case "print_int":
                    arg_value = interpret(node=node.arguments[0], tbl=table)
                    print(arg_value)
                    return None
                case "print_bool":
                    arg_value = interpret(node=node.arguments[0], tbl=table)
                    print(arg_value)
                    return None
                case "read_int":
                    return int(input())
                case _:
                    current_scop: SymTab | None = table
                    while current_scop:
                        if node.name in current_scop.locals:
                            function = current_scop.locals[node.name]
                            new_table = SymTab(locals={}, parent=current_scop)
                            for arg, param in zip(node.arguments, function.params):
                                new_table.locals[param.name] = interpret(
                                    node=arg, tbl=table
                                )
                            try:
                                interpret(node=function.body, tbl=new_table)
                                return None
                            except ReturnException as e:
                                return e.value
                        current_scop = current_scop.parent
                    raise Exception(f"Unknown function: {node.name}")

        case ast.Identifier():
            current_scope: SymTab | None = table
            while current_scope:
                if node.name in current_scope.locals:
                    return current_scope.locals[node.name]
                current_scope = current_scope.parent
            raise Exception(f"Unknown variable: {node.name}")

        case ast.Variable():
            value = interpret(node=node.value, tbl=table)
            table.locals[node.ident.name] = value
            return value

        case ast.Block():
            new_table = SymTab(locals={}, parent=table)
            for expr in node.expressions:
                interpret(node=expr, tbl=new_table)
            return interpret(node.result, tbl=new_table)

        case ast.Assignement():
            if isinstance(node.left, ast.Identifier):
                value = interpret(node=node.right, tbl=table)
                current_sco: SymTab | None = table
                while current_sco:
                    if node.left.name in current_sco.locals:
                        current_sco.locals[node.left.name] = value
                        return value
                    current_sco = current_sco.parent
                raise Exception(f"Unknown variable: {node.left.name}")
            else:
                raise Exception("Left side of assignment must be an identifier")

        case ast.While():
            while interpret(node=node.condition, tbl=table):
                try:
                    interpret(node=node.do_clause, tbl=table)
                except ContinueExpection:
                    continue
                except BreakExpection:
                    break
            return None

        case ast.Break():
            raise BreakExpection()

        case ast.Continue():
            raise ContinueExpection()

        case ast.ReturnExpression():
            value = interpret(node=node.value, tbl=table)
            raise ReturnException(value)

        case ast.Module():
            for function in node.funs:
                table.locals[function.name] = function
            return interpret(node=node.body, tbl=table)

        case _:
            raise Exception(f"Unknown node type: {type(node)}")
