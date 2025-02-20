from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    pass


@dataclass(frozen=True)
class BasicType(Type):
    name: str


@dataclass(frozen=True)
class FunType(Type):
    params_type: list[Type]
    return_type: Type


Int = BasicType("Int")
Bool = BasicType("Bool")
Unit = BasicType("Unit")
