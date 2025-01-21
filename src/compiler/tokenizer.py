import re
from dataclasses import dataclass
from typing import Literal, Union, Optional

class L:
    def __init__(self) -> None:
        self.pos: Optional[int] = None
        self.line: Optional[int] = None
        self.column: Optional[int] = None

    def __eq__(self, arg: object) -> bool:
        return isinstance(arg, (Location, L))

@dataclass(frozen=True)
class Location:
    pos: int
    line: int
    column: int

@dataclass(frozen=True)
class Token:
    loc: Union[Location, L]
    type: Literal["int_literal", "identifier", "punctuation", "boolean", "end"]
    text: str

    def __eq__(self, arg: object) -> bool:
        if not isinstance(arg, Token):
            return False
        return (
            self.type == arg.type
            and self.text == arg.text
            and (self.loc == arg.loc or isinstance(self.loc, L) or isinstance(arg.loc, L))
        )

def tokenize(source_code: str) -> list[Token]:
    boolean_re = re.compile(r'true|false')
    ident_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    int_re = re.compile(r'[0-9]+')
    newline_re = re.compile(r'\n')
    comments_re = re.compile(r'//.*|#.*')
    oper_re = re.compile(r'<=|>=|==|!=|>|<|=|/|-|\*|\+|\%')
    punct_re = re.compile(r'[(){},;:]')
    whitespace_re = re.compile(r'[^\S\n]+')

    pos = 0
    line = 1
    column = 1
    tokens: list[Token] = []

    while pos < len(source_code):
        match = boolean_re.match(source_code, pos)
        if match:
            tokens.append(Token(
                loc = Location(pos=pos, line=line, column=column),
                type="boolean",
                text=source_code[pos:match.end()]
            ))
            column += match.end() - pos
            pos = match.end()
            continue

        match = ident_re.match(source_code, pos)
        if match:
            tokens.append(Token(
                loc = Location(pos=pos, line=line, column=column),
                type="identifier",
                text=source_code[pos:match.end()]
            ))
            column += match.end() - pos
            pos = match.end()
            continue
        
        match = int_re.match(source_code, pos)
        if match:
            tokens.append(Token(
                loc = Location(pos=pos, line=line, column=column),
                type="int_literal",
                text=source_code[pos:match.end()]
            ))
            column += match.end() - pos
            pos = match.end()
            continue

        match = newline_re.match(source_code, pos)
        if match:
            line += 1
            column = 1
            pos = match.end()
            continue

        match = comments_re.match(source_code, pos)
        if match:
            column += match.end() - pos
            pos = match.end()
            continue

        match = oper_re.match(source_code, pos)
        if match:
            tokens.append(Token(
                loc = Location(pos=pos, line=line, column=column),
                type="identifier",
                text=source_code[pos:match.end()]
            ))
            column += match.end() - pos
            pos = match.end()
            continue
        
        match = punct_re.match(source_code, pos)
        if match:
            tokens.append(Token(
                loc = Location(pos=pos, line=line, column=column),
                type="punctuation",
                text=source_code[pos:match.end()]
            ))
            column += match.end() - pos
            pos = match.end()
            continue

        match = whitespace_re.match(source_code, pos)
        if match:
            column += match.end() - pos
            pos = match.end()
            continue

        raise Exception(f'Tokenization failure near {line}:{column} - {source_code[pos:(pos + 10)]}...')

    return tokens