from compiler.tokenizer import tokenize
from compiler.tokenizer import Token
from compiler.tokenizer import Location
from compiler.tokenizer import L

def test_tokenizer_basics() -> None:
    assert tokenize('aaa 123 bbb') == [
    Token(loc=L(), type="identifier", text="aaa"),
    Token(loc=L(), type="int_literal", text="123"),
    Token(loc=L(), type="identifier", text="bbb"),
    ]
    return None

def test_tokenizer_location() -> None:
    assert tokenize('aaa \n123 \n  bbb  ccc') == [
    Token(loc=Location(1, 1), type="identifier", text="aaa"),
    Token(loc=Location(2, 1), type="int_literal", text="123"),
    Token(loc=Location(3, 3), type="identifier", text="bbb"),
    Token(loc=Location(3, 8), type="identifier", text="ccc"),
    ]
    return None

def test_tokenizer_comments() -> None:
    assert tokenize('aaa //hello\nbbb #hi\n//haha\nccc') == [
    Token(loc=L(), type="identifier", text="aaa"),
    Token(loc=L(), type="identifier", text="bbb"),
    Token(loc=L(), type="identifier", text="ccc"),
    ]
    return None

def test_tokenizer_operators() -> None:
    assert tokenize('123 + 456 \n1+1=3\na=1\na==2\na>=1\na != 1') == [
    Token(loc=L(), type="int_literal", text="123"),
    Token(loc=L(), type="identifier", text="+"),
    Token(loc=L(), type="int_literal", text="456"),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="identifier", text="+"),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="identifier", text="="),
    Token(loc=L(), type="int_literal", text="3"),
    Token(loc=L(), type="identifier", text="a"),
    Token(loc=L(), type="identifier", text="="),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="identifier", text="a"),
    Token(loc=L(), type="identifier", text="=="),
    Token(loc=L(), type="int_literal", text="2"),
    Token(loc=L(), type="identifier", text="a"),
    Token(loc=L(), type="identifier", text=">="),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="identifier", text="a"),
    Token(loc=L(), type="identifier", text="!="),
    Token(loc=L(), type="int_literal", text="1"),
    ]
    return None

def test_tokenizer_punctuation() -> None:
    assert tokenize('if 1+2=3 {\nprint_int(123)\na,b=1}') == [
    Token(loc=L(), type="identifier", text="if"),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="identifier", text="+"),
    Token(loc=L(), type="int_literal", text="2"),
    Token(loc=L(), type="identifier", text="="),
    Token(loc=L(), type="int_literal", text="3"),
    Token(loc=L(), type="punctuation", text="{"),
    Token(loc=L(), type="identifier", text="print_int"),
    Token(loc=L(), type="punctuation", text="("),
    Token(loc=L(), type="int_literal", text="123"),
    Token(loc=L(), type="punctuation", text=")"),
    Token(loc=L(), type="identifier", text="a"),
    Token(loc=L(), type="punctuation", text=","),
    Token(loc=L(), type="identifier", text="b"),
    Token(loc=L(), type="identifier", text="="),
    Token(loc=L(), type="int_literal", text="1"),
    Token(loc=L(), type="punctuation", text="}")
    ]
    return None