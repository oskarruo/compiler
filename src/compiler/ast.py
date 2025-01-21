from dataclasses import dataclass

@dataclass
class Expression:
    pass

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
    type: Identifier | None
    value: Expression
