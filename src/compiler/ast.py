from dataclasses import dataclass, field
from compiler.tokenizer import Location, L
from compiler.types import Type, Unit

@dataclass
class Expression:
    location: Location | L
    type: Type = field(kw_only=True, default=Unit)

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class IfExpression(Expression):
    condition: Expression
    then_clause: Expression
    else_clause: Expression | None

@dataclass
class Function(Expression):
    name: str
    arguments: list[Expression]

@dataclass
class BinaryComp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class BinaryLogical(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class Assignement(Expression):
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class Block(Expression):
    expressions: list[Expression]
    result: Expression

@dataclass
class While(Expression):
    condition: Expression
    do_clause: Expression

@dataclass
class Variable(Expression):
    ident: Identifier
    type_declaration: Identifier | None
    value: Expression

@dataclass
class Break(Expression):
    pass

@dataclass
class Continue(Expression):
    pass

@dataclass
class ReturnExpression(Expression):
    value: Expression

@dataclass
class FunDefArg:
    name: str
    type: Identifier

@dataclass
class FunDef:
    location: Location | L
    name: str
    params: list[FunDefArg]
    return_type: Identifier
    body: Expression

@dataclass
class Module:
    funs: list[FunDef]
    body: Expression
    type: Type = field(kw_only=True, default=Unit)
