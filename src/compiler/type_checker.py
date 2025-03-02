from __future__ import annotations
from compiler import ast
from compiler.types import Int, Bool, Unit, Type, FunType
from compiler.symtab import SymTab

functions = {
    "+": FunType(params_type=[Int, Int], return_type=Int),
    "-": FunType(params_type=[Int, Int], return_type=Int),
    "<": FunType(params_type=[Int, Int], return_type=Bool),
    ">": FunType(params_type=[Int, Int], return_type=Bool),
    "<=": FunType(params_type=[Int, Int], return_type=Bool),
    ">=": FunType(params_type=[Int, Int], return_type=Bool),
    "*": FunType(params_type=[Int, Int], return_type=Int),
    "/": FunType(params_type=[Int, Int], return_type=Int),
    "%": FunType(params_type=[Int, Int], return_type=Int),
    "unary_-": FunType(params_type=[Int], return_type=Int),
    "unary_not": FunType(params_type=[Bool], return_type=Bool),
    "and": FunType(params_type=[Bool, Bool], return_type=Bool),
    "or": FunType(params_type=[Bool, Bool], return_type=Bool),
    "print_int": FunType(params_type=[Int], return_type=Unit),
    "print_bool": FunType(params_type=[Bool], return_type=Unit),
    "read_int": FunType(params_type=[], return_type=Int),
}

types = {"Int": Int, "Bool": Bool, "Unit": Unit}


def typecheck(
    node: ast.Expression | ast.Module, symtab: SymTab | None = None, funct: str = "main"
) -> Type:
    if symtab is None:
        symtab = SymTab(locals={}, parent=SymTab(locals={}, parent=None))

    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                node.type = Bool
            elif isinstance(node.value, int):
                node.type = Int
            elif node.value is None:
                node.type = Unit
            else:
                raise Exception(f"Unknown literal type: {node.value}")

        case ast.Identifier():
            v = False
            if node.name in types:
                node.type = types[node.name]
                v = True
            else:
                current_scope = symtab
                while current_scope.parent:
                    if node.name in current_scope.locals:
                        node.type = current_scope.locals[node.name]
                        v = True
                        break
                    current_scope = current_scope.parent

            if not v:
                raise Exception(f"Unknown identifier: {node.name}")

        case ast.Variable():
            name = node.ident.name
            a: Type = typecheck(node=node.value, symtab=symtab, funct=funct)

            if node.type_declaration:
                if node.type_declaration.name in types:
                    b: Type = types[node.type_declaration.name]
                else:
                    raise Exception(
                        f"Unknown type annotation: {node.type_declaration.name}"
                    )

                if a != b:
                    raise Exception(f"Invalid types for variable {name}: {a}, {b}")

            symtab.locals[name] = a
            node.type = Unit

        case ast.Assignement():
            if not isinstance(node.left, ast.Identifier):
                raise Exception("Left side of assignement must be an identifier")

            name = node.left.name
            c: Type = typecheck(node=node.right, symtab=symtab, funct=funct)

            v = False
            current_scope = symtab
            while current_scope.parent:
                if name in current_scope.locals:
                    d = current_scope.locals[name]
                    if c != d:
                        raise Exception(f"Invalid types for assignement: {c}, {d}")
                    v = True
                    break
                current_scope = current_scope.parent

            if v is False:
                raise Exception(f"Unknown variable: {name}")

            node.type = d

        case ast.BinaryOp():
            func = functions[node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            e: Type = typecheck(node=node.left, symtab=symtab, funct=funct)
            f: Type = typecheck(node=node.right, symtab=symtab, funct=funct)
            if (e, f) == (func.params_type[0], func.params_type[1]):
                node.type = func.return_type
            else:
                raise Exception(f"Invalid types for operator {node.op}: {e}, {f}")

        case ast.BinaryComp():
            if node.op == "==" or node.op == "!=":
                g: Type = typecheck(node=node.left, symtab=symtab, funct=funct)
                h: Type = typecheck(node=node.right, symtab=symtab, funct=funct)
                if g == h:
                    node.type = Bool
                else:
                    raise Exception(f"Invalid types for operator {node.op}: {g}, {h}")
            else:
                func = functions[node.op]
                if func is None:
                    raise Exception(f"Unknown operator: {node.op}")
                i: Type = typecheck(node=node.left, symtab=symtab, funct=funct)
                j: Type = typecheck(node=node.right, symtab=symtab, funct=funct)
                if (i, j) == (func.params_type[0], func.params_type[1]):
                    node.type = func.return_type
                else:
                    raise Exception(f"Invalid types for operator {node.op}: {i}, {j}")

        case ast.BinaryLogical():
            func = functions[node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            k: Type = typecheck(node=node.left, symtab=symtab, funct=funct)
            ll: Type = typecheck(node=node.right, symtab=symtab, funct=funct)
            if (k, ll) == (func.params_type[0], func.params_type[1]):
                node.type = func.return_type
            else:
                raise Exception(f"Invalid types for operator {node.op}: {k}, {ll}")

        case ast.IfExpression():
            condition = typecheck(node=node.condition, symtab=symtab, funct=funct)
            if condition != Bool:
                raise Exception(f"Invalid type for condition: {condition}")
            then_clause = typecheck(node=node.then_clause, symtab=symtab, funct=funct)

            if node.else_clause is None:
                node.type = Unit
            else:
                else_clause = typecheck(
                    node=node.else_clause, symtab=symtab, funct=funct
                )

                if then_clause == else_clause:
                    node.type = then_clause
                else:
                    raise Exception(
                        f"Invalid types for then and else: {then_clause}, {else_clause}"
                    )

        case ast.UnaryOp():
            func = functions["unary_" + node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            m: Type = typecheck(node=node.operand, symtab=symtab, funct=funct)
            if m == func.params_type[0]:
                node.type = func.return_type
            else:
                raise Exception(f"Invalid type for operator {node.op}: {m}")

        case ast.Block():
            new_symtab = SymTab(locals={}, parent=symtab)
            for expression in node.expressions:
                typecheck(node=expression, symtab=new_symtab, funct=funct)
            node.type = typecheck(node=node.result, symtab=new_symtab, funct=funct)

        case ast.Function():
            func = functions[node.name]
            if func is None:
                raise Exception(f"Unknown function: {node.name}")
            for arg in node.arguments:
                n: Type = typecheck(node=arg, symtab=symtab, funct=funct)
                if n != func.params_type[0]:
                    raise Exception(f"Invalid type for argument: {n}")
            node.type = func.return_type

        case ast.While():
            condition = typecheck(node=node.condition, symtab=symtab, funct=funct)
            if condition != Bool:
                raise Exception(f"Invalid type for condition: {condition}")
            typecheck(node=node.do_clause, symtab=symtab, funct=funct)
            node.type = Unit

        case ast.Break():
            node.type = Unit

        case ast.Continue():
            node.type = Unit

        case ast.ReturnExpression():
            o: Type = typecheck(node=node.value, symtab=symtab, funct=funct)
            if o != functions[funct].return_type:
                raise Exception(f"Invalid return type: {o}")
            node.type = o

        case ast.Module():
            for fun in node.funs:
                functions[fun.name] = FunType(
                    params_type=[types[arg.type.name] for arg in fun.params],
                    return_type=types[fun.return_type.name],
                )

            for fun in node.funs:
                typecheck_fundef(node=fun)

            p: Type = typecheck(node=node.body, symtab=symtab, funct=funct)
            node.type = p

        case _:
            raise Exception(f"Unknown node type: {node}")

    return node.type


def typecheck_fundef(node: ast.FunDef) -> None:
    symtab = SymTab(locals={}, parent=SymTab(locals={}, parent=None))
    for arg in node.params:
        symtab.locals[arg.name] = types[arg.type.name]
    typecheck(node=node.body, symtab=symtab, funct=node.name)
    return None
