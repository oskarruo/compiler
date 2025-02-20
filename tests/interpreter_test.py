import pytest
from unittest.mock import patch
from compiler.interpreter import interpret
from compiler.tokenizer import tokenize
from compiler.parser import parse

def test_interpreter_binary_op() -> None:
    assert interpret(node=parse(tokenize("2 + 3"))) == 5
    assert interpret(node=parse(tokenize("2 - 3"))) == -1
    assert interpret(node=parse(tokenize("2 * 3"))) == 6
    assert interpret(node=parse(tokenize("4 / 2"))) == 2
    assert interpret(node=parse(tokenize("3 % 2"))) == 1
    return None

def test_interpreter_binary_comp() -> None:
    assert interpret(node=parse(tokenize("2 < 3"))) == True
    assert interpret(node=parse(tokenize("2 > 3"))) == False
    assert interpret(node=parse(tokenize("2 <= 3"))) == True
    assert interpret(node=parse(tokenize("2 >= 3"))) == False
    assert interpret(node=parse(tokenize("2 == 3"))) == False
    assert interpret(node=parse(tokenize("2 != 3"))) == True
    return None

def test_interpreter_binary_logical() -> None:
    assert interpret(node=parse(tokenize("true and false"))) == False
    assert interpret(node=parse(tokenize("true or false"))) == True
    return None

def test_interpreter_unary_op() -> None:
    assert interpret(node=parse(tokenize("var x = 2; -x"))) == -2
    assert interpret(node=parse(tokenize("not true"))) == False
    return None

def test_interpreter_functions() -> None:
    with patch('builtins.print') as mock_print:
        res = interpret(node=parse(tokenize("print_int(5)")))
        mock_print.assert_called_with(5)
        assert res == None
    with patch('builtins.print') as mock_print:
        res = interpret(node=parse(tokenize("print_bool(true)")))
        mock_print.assert_called_with(True)
        assert res == None
    with patch('builtins.input', return_value='69'):
        result = interpret(node=parse(tokenize("read_int()")))
        assert result == 69
    return None

def test_interpreter_short_circuiting() -> None:
    assert interpret(node=parse(tokenize("var e = false; true or { e = true; true }; e"))) == False
    return None

def test_interpreter_block() -> None:
    assert interpret(node=parse(tokenize("{ 2 + 3; 3 + 4 }"))) == 7
    return None

def interpreter_test_block_with_variable() -> None:
    assert interpret(node=parse(tokenize("{ var x = 2 + 3; x + 4 }"))) == 9
    return None

def test_interpreter_block_with_unknown_variable_fails() -> None:
    with pytest.raises(Exception, match=r'Unknown variable: x'):
        interpret(parse(tokenize('{ { var x = 2; }; x + 4 }')))
    return None

def test_interpreter_block_with_variable_shadowing() -> None:
    assert interpret(node=parse(tokenize("{ var x = 2; { var x = 3; x }; x }"))) == 2
    return None

def test_interpreter_assignment() -> None:
    assert interpret(node=parse(tokenize("var x = 2; x = 3; x"))) == 3
    return None

def test_interpreter_while() -> None:
    assert interpret(node=parse(tokenize("var x = 0; while x < 3 do { x = x + 1 }; x"))) == 3
    return None

def test_interpreter_break() -> None:
    assert interpret(node=parse(tokenize("var x = 0; while true do { x = x + 1; if x == 3 then break }; x"))) == 3
    return None

def test_interpreter_continue() -> None:
    assert interpret(node=parse(tokenize("var x = 0; while x < 3 do { x = x + 2; if x == 2 then continue; x = x + 1;} x"))) == 5
    return None

def test_interpreter_function_def() -> None:
    assert interpret(node=parse(tokenize('fun square(x: Int): Int { return x * x; } square(2)'))) == 4
    assert interpret(node=parse(tokenize('fun add(x: Int, y: Int): Unit { x + y } add(2, 3)'))) == None
    return None
