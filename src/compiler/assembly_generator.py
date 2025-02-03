from compiler import ir
from dataclasses import dataclass, fields
from compiler.intrinsics import all_intrinsics, IntrinsicArgs

def generate_assembly(instructions: list[ir.Instruction]) -> str:
    assembly_code_lines = []
    def emit(line: str) -> None: assembly_code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))

    emit(".global main")
    emit(".type main, @function")
    emit(".extern print_int")

    emit('.section .text')
    emit('main:')
    emit('pushq %rbp')
    emit('movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')

    for isn in instructions:
        match isn:
            case ir.Label():
                emit(f'.{isn.name}:')
            case ir.LoadIntConst():
                if -2**31 <= isn.value < 2**31:
                    emit(f'movq ${isn.value}, {locals.get_ref(isn.dest)}')
                else:
                    emit(f'movabsq ${isn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(isn.dest)}')
            case ir.LoadBoolConst():
                emit(f'movq ${int(isn.value)}, {locals.get_ref(isn.dest)}')
            case ir.Copy():
                emit(f'movq {locals.get_ref(isn.src)}, %rax')
                emit(f'movq %rax, {locals.get_ref(isn.dest)}')
            case ir.Jump():
                emit(f'jmp .{isn.label.name}')
            case ir.CondJump():
                emit(f'cmpq $0, {locals.get_ref(isn.cond)}')
                emit(f'jne .{isn.then_label.name}')
                emit(f'jmp .{isn.else_label.name}')
            case ir.Call():
                if (intrinsic := all_intrinsics.get(isn.fun.name)) is not None:
                    args = IntrinsicArgs(
                        arg_refs = [locals.get_ref(arg) for arg in isn.args],
                        result_register = '%rax',
                        emit = emit,
                    )
                    intrinsic(args)
                    emit(f'movq %rax, {locals.get_ref(isn.dest)}')
                else:
                    match isn.fun.name:
                        case "print_int":
                            if len(isn.args) != 1:
                                raise Exception(f"Expected 1 argument for print_int, got {len(isn.args)}")
                            emit(f'movq {locals.get_ref(isn.args[0])}, %rdi')
                            emit('callq print_int')
                            emit(f'movq %rax, {locals.get_ref(isn.dest)}')
                        case "print_bool":
                            if len(isn.args) != 1:
                                raise Exception(f"Expected 1 argument for print_int, got {len(isn.args)}")
                            emit(f'movq {locals.get_ref(isn.args[0])}, %rdi')
                            emit('callq print_bool')
                            emit(f'movq %rax, {locals.get_ref(isn.dest)}')
                        case "read_int":
                            emit('callq read_int')
                            emit(f'movq %rax, {locals.get_ref(isn.dest)}')
                        case _:
                            raise Exception(f"Unknown function: {isn.fun.name}")
            case _:
                raise Exception(f"Unknown instruction: {type(isn)}")

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    emit('')

    return "\n".join(assembly_code_lines)


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list

class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 8
        for v in variables:
            if v not in self._var_to_location:
                self._var_to_location[v] = f'-{self._stack_used}(%rbp)'
                self._stack_used += 8

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used
