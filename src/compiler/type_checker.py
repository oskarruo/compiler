from compiler import ast
from compiler.types import Int, Bool, Unit, Type, FunType

functions = {
        '+': FunType(params_type=[Int, Int], return_type=Int),
        '-': FunType(params_type=[Int, Int], return_type=Int),
        '<': FunType(params_type=[Int, Int], return_type=Bool),
        '>': FunType(params_type=[Int, Int], return_type=Bool),
        '<=': FunType(params_type=[Int, Int], return_type=Bool),
        '>=': FunType(params_type=[Int, Int], return_type=Bool),
        '*': FunType(params_type=[Int, Int], return_type=Int),
        '/': FunType(params_type=[Int, Int], return_type=Int),
        '%': FunType(params_type=[Int, Int], return_type=Int),
        'unary_-': FunType(params_type=[Int], return_type=Int),
        'unary_not': FunType(params_type=[Bool], return_type=Bool),
        'and': FunType(params_type=[Bool, Bool], return_type=Bool),
        'or': FunType(params_type=[Bool, Bool], return_type=Bool),
        'print_int': FunType(params_type=[Int], return_type=Unit),
        'print_bool': FunType(params_type=[Bool], return_type=Unit),
        'read_int': FunType(params_type=[], return_type=Int)
    }

types = {
    'Int': Int,
    'Bool': Bool,
    'Unit': Unit
}

def typecheck(node: ast.Expression, symtab: dict[str, Type] | None = None) -> Type:
    if symtab is None:
        symtab = {}

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
            if node.name in types:
                node.type = types[node.name]
            elif node.name in symtab:
                node.type = symtab[node.name]
            else:
                raise Exception(f"Unknown identifier: {node.name}")
        
        case ast.Variable():
            name = node.ident.name
            a: Type = typecheck(node=node.value, symtab=symtab)

            if node.type_declaration:
                if node.type_declaration.name in types:
                    b: Type = types[node.type_declaration.name]  
                else:
                    raise Exception(f"Unknown type annotation: {node.type_declaration.name}")

                if a != b:
                    raise Exception(f"Invalid types for variable {name}: {a}, {b}")

            symtab[name] = a
            node.type = Int

        case ast.Assignement():
            if not isinstance(node.left, ast.Identifier):
                raise Exception(f"Left side of assignement must be an identifier")

            name = node.left.name
            c: Type = typecheck(node=node.right, symtab=symtab)

            if name in symtab:
                d = symtab[name]
                if c != d:
                    raise Exception(f"Invalid types for assignement: {c}, {d}")
            else:
                raise Exception(f"Unknown variable: {name}")
            
            node.type = Unit

        case ast.BinaryOp():
            func = functions[node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            e: Type = typecheck(node=node.left, symtab=symtab)
            f: Type = typecheck(node=node.right, symtab=symtab)
            if (e, f) == (func.params_type[0], func.params_type[1]):
                node.type = func.return_type
            else:
                raise Exception(f"Invalid types for operator {node.op}: {e}, {f}")

        case ast.BinaryComp():
            if node.op == '==' or node.op == '!=':
                g: Type = typecheck(node=node.left, symtab=symtab)
                h: Type = typecheck(node=node.right, symtab=symtab)
                if g == h:
                    node.type = Bool
                else:
                    raise Exception(f"Invalid types for operator {node.op}: {g}, {h}")
            else:
                func = functions[node.op]
                if func is None:
                    raise Exception(f"Unknown operator: {node.op}")
                i: Type = typecheck(node=node.left, symtab=symtab)
                j: Type = typecheck(node=node.right, symtab=symtab)
                if (i, j) == (func.params_type[0], func.params_type[1]):
                    node.type = func.return_type
                else:
                    raise Exception(f"Invalid types for operator {node.op}: {i}, {j}")

        case ast.BinaryLogical():
            func = functions[node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            k: Type = typecheck(node=node.left, symtab=symtab)
            l: Type = typecheck(node=node.right, symtab=symtab)
            if (k, l) == (func.params_type[0], func.params_type[1]):
                node.type = func.return_type
            else:
                raise Exception(f"Invalid types for operator {node.op}: {k}, {l}")
            
        case ast.IfExpression():
            condition = typecheck(node=node.condition, symtab=symtab)
            if condition != Bool:
                raise Exception(f"Invalid type for condition: {condition}")
            then_clause = typecheck(node=node.then_clause, symtab=symtab)
            
            if node.else_clause is None:
                node.type = Unit
            else:
                else_clause = typecheck(node=node.else_clause, symtab=symtab)

                if then_clause == else_clause:
                    node.type = then_clause
                else:
                    raise Exception(f"Invalid types for then and else: {then_clause}, {else_clause}")
        
        case ast.UnaryOp():
            func = functions['unary_' + node.op]
            if func is None:
                raise Exception(f"Unknown operator: {node.op}")
            m: Type = typecheck(node=node.operand, symtab=symtab)
            if m == func.params_type[0]:
                node.type = func.return_type
            else:
                raise Exception(f"Invalid type for operator {node.op}: {m}")
        
        case ast.Block():
            for expression in node.expressions:
                typecheck(node=expression, symtab=symtab)
            node.type = typecheck(node=node.result, symtab=symtab)
        
        case ast.Function():
            func = functions[node.name]
            if func is None:
                raise Exception(f"Unknown function: {node.name}")
            for arg in node.arguments:
                n: Type = typecheck(node=arg, symtab=symtab)
                if n != func.params_type[0]:
                    raise Exception(f"Invalid type for argument: {n}")
            node.type = func.return_type
        
        case ast.While():
            condition = typecheck(node.condition, symtab=symtab)
            if condition != Bool:
                raise Exception(f"Invalid type for condition: {condition}")
            typecheck(node=node.do_clause, symtab=symtab)
            node.type = Unit
        
        case _:
            raise Exception(f"Unknown node type: {node}")

    return node.type