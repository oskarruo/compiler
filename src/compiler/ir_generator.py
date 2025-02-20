from __future__ import annotations
from dataclasses import dataclass
from compiler import ast, ir
from compiler.types import Bool, Int, Type, Unit
from compiler.type_checker import functions

@dataclass
class SymTab:
    locals: dict
    parent: SymTab | None

def generate_ir(root_node: ast.Module) -> dict[str, list[ir.Instruction]]:
    root_types = {ir.IRVar(name): typ for name, typ in functions.items()}
    
    var_types: dict[ir.IRVar, Type] = dict(root_types)

    var_unit = ir.IRVar('unit')
    var_types[var_unit] = Unit

    next_var_num = 1
    next_label_num = 1

    def new_var(t: Type) -> ir.IRVar:
        nonlocal next_var_num
        var = ir.IRVar(f'x{next_var_num}')
        var_types[var] = t
        next_var_num += 1
        return var
    
    def new_label() -> ir.Label:
        nonlocal next_label_num
        label = ir.Label(location=None, name=f'L{next_label_num}')
        next_label_num += 1
        return label
    
    instructions: list[ir.Instruction] = []

    funcs: dict[str, list[ir.Instruction]] = {}
    
    def visit(st: SymTab, expr: ast.Expression, start_label: ir.Label | None = None, end_label: ir.Label | None = None) -> ir.IRVar:
        loc = expr.location

        match expr:
            case ast.Literal():
                match expr.value:
                    case bool():
                        var = new_var(Bool)
                        instructions.append(ir.LoadBoolConst(location=loc, value=expr.value, dest=var))
                    case int():
                        var = new_var(Int)
                        instructions.append(ir.LoadIntConst(location=loc, value=expr.value, dest=var))
                    case None:
                        var = new_var(Unit)
                    case _:
                        raise Exception(f'Invalid literal: {type(expr.value)}')
                
                return var

            case ast.Identifier():
                current_scope = st
                while current_scope.parent:
                    if expr.name in current_scope.locals:
                        return current_scope.locals[expr.name]
                    current_scope = current_scope.parent
                raise Exception(f'Unknown variable: {expr.name}')

            case ast.BinaryOp():
                var_op = root_symtab.locals[expr.op]
                var_left = visit(st, expr.left, start_label, end_label)
                var_right = visit(st, expr.right, start_label, end_label)
                var_result = new_var(expr.type)
                instructions.append(ir.Call(location=loc, fun=var_op, args=[var_left, var_right], dest=var_result))
                return var_result
            
            case ast.IfExpression():
                if expr.else_clause is None:
                    l_then = new_label()
                    l_end = new_label()

                    var_cond = visit(st, expr.condition, start_label, end_label)
                    instructions.append(ir.CondJump(location=loc, cond=var_cond, then_label=l_then, else_label=l_end))

                    instructions.append(ir.Label(location=loc, name=l_then.name))
                    visit(st, expr.then_clause, start_label, end_label)

                    instructions.append(ir.Label(location=loc, name=l_end.name))

                    return var_unit
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(st, expr.condition, start_label, end_label)
                    instructions.append(ir.CondJump(location=loc, cond=var_cond, then_label=l_then, else_label=l_else))

                    var_result = new_var(expr.type)

                    instructions.append(ir.Label(location=loc, name=l_then.name))
                    var_then = visit(st, expr.then_clause, start_label, end_label)
                    instructions.append(ir.Copy(location=loc, src=var_then, dest=var_result))
                    instructions.append(ir.Jump(location=loc, label=l_end))

                    instructions.append(ir.Label(location=loc, name=l_else.name))
                    var_else = visit(st, expr.else_clause, start_label, end_label)
                    instructions.append(ir.Copy(location=loc, src=var_else, dest=var_result))
                    instructions.append(ir.Label(location=loc, name=l_end.name))

                    return var_result
            
            case ast.BinaryComp():
                if expr.op in ['==', '!=']:
                    var_left = visit(st, expr.left, start_label, end_label)
                    var_right = visit(st, expr.right, start_label, end_label)
                    var_result = new_var(Bool)
                    instructions.append(ir.Call(location=loc, fun=ir.IRVar(expr.op), args=[var_left, var_right], dest=var_result))
                    return var_result

                var_op = root_symtab.locals[expr.op]
                var_left = visit(st, expr.left, start_label, end_label)
                var_right = visit(st, expr.right, start_label, end_label)
                var_result = new_var(Bool)
                instructions.append(ir.Call(location=loc, fun=var_op, args=[var_left, var_right], dest=var_result))
                return var_result
            
            case ast.BinaryLogical():
                l_right = new_label()
                l_skip = new_label()
                l_end = new_label()

                var_left = visit(st, expr.left, start_label, end_label)
                var_result = new_var(Bool)

                if expr.op == "and":
                    instructions.append(ir.CondJump(location=loc, cond=var_left, then_label=l_right, else_label=l_skip))

                    instructions.append(ir.Label(location=loc, name=l_right.name))
                    var_right = visit(st, expr.right, start_label, end_label)
                    instructions.append(ir.Copy(location=loc, src=var_right, dest=var_result))
                    instructions.append(ir.Jump(location=loc, label=l_end))

                    instructions.append(ir.Label(location=loc, name=l_skip.name))
                    instructions.append(ir.LoadBoolConst(location=loc, value=False, dest=var_result))
                    instructions.append(ir.Jump(location=loc, label=l_end))

                elif expr.op == "or":
                    instructions.append(ir.CondJump(location=loc, cond=var_left, then_label=l_skip, else_label=l_right))

                    instructions.append(ir.Label(location=loc, name=l_right.name))
                    var_right = visit(st, expr.right, start_label, end_label)
                    instructions.append(ir.Copy(location=loc, src=var_right, dest=var_result))
                    instructions.append(ir.Jump(location=loc, label=l_end))

                    instructions.append(ir.Label(location=loc, name=l_skip.name))
                    instructions.append(ir.LoadBoolConst(location=loc, value=True, dest=var_result))
                    instructions.append(ir.Jump(location=loc, label=l_end))

                instructions.append(ir.Label(location=loc, name=l_end.name))

                return var_result
            
            case ast.Function():
                fun = root_symtab.locals[expr.name]
                args = [visit(st, arg, start_label, end_label) for arg in expr.arguments]
                dest = new_var(expr.type)
                instructions.append(ir.Call(location=loc, fun=fun, args=args, dest=dest))

                return dest
            
            case ast.While():
                l_start = new_label()
                l_body = new_label()
                l_end = new_label()

                instructions.append(ir.Label(location=loc, name=l_start.name))
                var_cond = visit(st, expr.condition, start_label, end_label)
                instructions.append(ir.CondJump(location=loc, cond=var_cond, then_label=l_body, else_label=l_end))

                instructions.append(ir.Label(location=loc, name=l_body.name))
                visit(st, expr.do_clause, start_label=l_start, end_label=l_end)
                instructions.append(ir.Jump(location=loc, label=l_start))

                instructions.append(ir.Label(location=loc, name=l_end.name))

                return var_unit
            
            case ast.Variable():
                if expr.ident.name in st.locals:
                    raise Exception(f'Variable already defined in this scope: {expr.ident.name}')
                var = new_var(expr.value.type)
                value = visit(st, expr.value, start_label, end_label)
                instructions.append(ir.Copy(location=loc, src=value, dest=var))
                st.locals[expr.ident.name] = var
                return var_unit

            case ast.Block():
                new_st = SymTab(locals={}, parent=st)
                for expression in expr.expressions:
                    visit(new_st, expression, start_label, end_label)
                return visit(new_st, expr.result, start_label, end_label)
            
            case ast.Assignement():
                if isinstance(expr.left, ast.Identifier):
                    v = None
                    current_scope = st
                    while current_scope.parent:
                        if expr.left.name in current_scope.locals:
                            var = current_scope.locals[expr.left.name]
                            v = True
                            break
                        current_scope = current_scope.parent
                    if v is None:
                        raise Exception(f'Unknown variable: {expr.left.name}')
                    value = visit(st, expr.right, start_label, end_label)
                    instructions.append(ir.Copy(location=loc, src=value, dest=var))
                    return value
                else:
                    raise Exception(f'Left side of assignment must be an identifier')
            
            case ast.UnaryOp():
                var_op = root_symtab.locals['unary_' + expr.op]
                var_operand = visit(st, expr.operand, start_label, end_label)
                var_result = new_var(expr.type)
                instructions.append(ir.Call(location=loc, fun=var_op, args=[var_operand], dest=var_result))
                return var_result
            
            case ast.Break():
                if end_label is None:
                    raise Exception(f'Break outside of loop')
                instructions.append(ir.Jump(location=loc, label=end_label))
                return var_unit
            
            case ast.Continue():
                if start_label is None:
                    raise Exception(f'Continue outside of loop')
                instructions.append(ir.Jump(location=loc, label=start_label))
                return var_unit
            
            case ast.ReturnExpression():
                var_result = visit(st, expr.value, start_label, end_label)
                instructions.append(ir.Return(location=loc, value=var_result))
                return var_unit

            case _:
                raise Exception(f'Invalid expression: {type(expr)}')

    root_symtab = SymTab(locals={}, parent=None)
    for v in root_types.keys():
        root_symtab.locals[v.name] = v

    for fun in root_node.funs:
        args = []
        for arg in fun.params:
            args.append(arg.name)
        instructions.append(ir.Label(location=None, name='start'))
        fun_symtab = SymTab(locals={}, parent=root_symtab)
        for arg in fun.params:
            var = ir.IRVar(arg.name)
            var_types[var] = arg.type.type
            fun_symtab.locals[arg.name] = var
        visit(fun_symtab, fun.body)
        if instructions[-1].__class__ != ir.Return:
            instructions.append(ir.Return(location=None, value=var_unit))
        funcs[f'{fun.name}({str(args)})'] = instructions
        instructions = []

    instructions.append(ir.Label(location=None, name='start'))
    
    var_final_result = visit(SymTab(locals={}, parent=root_symtab), root_node.body)

    if var_types[var_final_result] == Int:
        instructions.append(ir.Call(location=None, fun=root_symtab.locals['print_int'], args=[var_final_result], dest=new_var(Unit)))
    elif var_types[var_final_result] == Bool:
        instructions.append(ir.Call(location=None, fun=root_symtab.locals['print_bool'], args=[var_final_result], dest=new_var(Unit)))

    funcs['main'] = instructions

    return funcs