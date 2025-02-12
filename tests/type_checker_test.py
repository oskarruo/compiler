import pytest
import re
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck, SymTab
from compiler.types import Bool, Int, Unit, FunType

def test_type_checker_binary_op() -> None:
    assert typecheck(parse(tokenize("1 + 2"))) == Int
    assert typecheck(parse(tokenize("1 - 2"))) == Int
    assert typecheck(parse(tokenize("1 * 2"))) == Int
    assert typecheck(parse(tokenize("1 / 2"))) == Int
    assert typecheck(parse(tokenize("1 % 2"))) == Int

    with pytest.raises(Exception, match=re.escape("Invalid types for operator +: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize('true + 2')))
    
    with pytest.raises(Exception, match=re.escape("Invalid types for operator -: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize('true - 2')))

    return None

def test_type_checker_binary_comp() -> None:
    assert typecheck(parse(tokenize("1 < 2"))) == Bool
    assert typecheck(parse(tokenize("1 <= 2"))) == Bool
    assert typecheck(parse(tokenize("1 > 2"))) == Bool
    assert typecheck(parse(tokenize("1 >= 2"))) == Bool
    assert typecheck(parse(tokenize("1 == 2"))) == Bool
    assert typecheck(parse(tokenize("1 != 2"))) == Bool
    
    with pytest.raises(Exception, match=re.escape("Invalid types for operator <: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize('true < 2')))

    with pytest.raises(Exception, match=re.escape("Invalid types for operator ==: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize('true == 2')))
    
    return None

def test_type_checker_binary_logical() -> None:
    assert typecheck(parse(tokenize("true and false"))) == Bool
    assert typecheck(parse(tokenize("true or false"))) == Bool

    with pytest.raises(Exception, match=re.escape("Invalid types for operator and: BasicType(name='Int'), BasicType(name='Bool')")):
        typecheck(parse(tokenize('1 and false')))

    with pytest.raises(Exception, match=re.escape("Invalid types for operator or: BasicType(name='Int'), BasicType(name='Bool')")):
        typecheck(parse(tokenize('1 or false')))

    return None

def test_type_checker_unary_op() -> None:
    assert typecheck(parse(tokenize("-x")), symtab=SymTab({'x': Int}, SymTab({}, None))) == Int
    assert typecheck(parse(tokenize("not true"))) == Bool

    with pytest.raises(Exception, match=re.escape("Invalid type for operator not: BasicType(name='Int')")):
        typecheck(parse(tokenize("not 1")))

    return None

def test_type_checker_if_expression() -> None:
    assert typecheck(parse(tokenize("if true then 1 else 2"))) == Int
    assert typecheck(parse(tokenize("if true then 1"))) == Unit

    with pytest.raises(Exception, match=re.escape("Invalid types for then and else: BasicType(name='Int'), BasicType(name='Bool')")):
        typecheck(parse(tokenize("if true then 1 else true")))
    
    assert typecheck(parse(tokenize("if true then true else false"))) == Bool
    assert typecheck(parse(tokenize("if true then false else true"))) == Bool
    assert typecheck(parse(tokenize("if true then false"))) == Unit

    with pytest.raises(Exception, match=re.escape("Invalid type for condition: BasicType(name='Int')")):
        typecheck(parse(tokenize("if 1 then 1 else 2")))

    with pytest.raises(Exception, match=re.escape("Invalid types for then and else: BasicType(name='Int'), BasicType(name='Bool')")):
        typecheck(parse(tokenize("if true then 1 else true")))

    return None

def test_type_checker_block() -> None:
    assert typecheck(parse(tokenize("{ 1; 2 }"))) == Int
    assert typecheck(parse(tokenize("{ 1; }"))) == Unit
    assert typecheck(parse(tokenize("{ }"))) == Unit

    return None

def test_type_checker_function() -> None:
    assert typecheck(parse(tokenize("print_int(1)"))) == Unit
    assert typecheck(parse(tokenize("print_bool(true)"))) == Unit
    assert typecheck(parse(tokenize("read_int()"))) == Int

    with pytest.raises(Exception, match=re.escape("Invalid type for argument: BasicType(name='Bool')")):
        typecheck(parse(tokenize("print_int(true)")))
    
    return None

def test_type_checker_while() -> None:
    assert typecheck(parse(tokenize("while true do 1"))) == Unit

    with pytest.raises(Exception, match=re.escape("Invalid type for condition: BasicType(name='Int')")):
        typecheck(parse(tokenize("while 1 do 1")))

    return None

def test_type_checker_variable_declaration() -> None:
    assert typecheck(parse(tokenize("var x: Int = 1"))) == Unit
    assert typecheck(parse(tokenize("var x = 1"))) == Unit

    with pytest.raises(Exception, match=re.escape("Unknown type annotation: float")):
        typecheck(parse(tokenize("var x: float = 1")))
    
    with pytest.raises(Exception, match=re.escape("Invalid types for variable x: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize("var x: Int = true")))

    return None

def test_type_checker_variable_assignment() -> None:
    assert typecheck(parse(tokenize("var x = 1; x = 2"))) == Int

    with pytest.raises(Exception, match=re.escape("Unknown variable: x")):
        typecheck(parse(tokenize("x = 2")))

    with pytest.raises(Exception, match=re.escape("Invalid types for assignement: BasicType(name='Bool'), BasicType(name='Int')")):
        typecheck(parse(tokenize("var x = 1; x = true")))

    return None

def test_type_checker_node_type_assignement() -> None:
    node = parse(tokenize("42"))
    typecheck(node)
    assert node.type == Int