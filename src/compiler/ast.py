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
