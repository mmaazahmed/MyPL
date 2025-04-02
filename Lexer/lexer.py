import sys
import re
from typing import List

class Lexer:

    token_spec = [
        ("COMMENTS", r'#[^\n]*'),
        ("FILL", r'\bFILL\b'),
        ("TRY", r'\bTRY\b'),
        ("CATCH", r'\bCATCH\b'),
        ("INTEGER_LITERAL", r'\b\d+\b'),
        ("LOGICAL_OPERATOR", r'==|AND|OR|>|<|<=|>=|\bHAS\b|\bIS\b'),
        ("ARITHMETIC_OPERATOR", r'\+|\-|\*|\/'),
        ("ON", r'ON'),
        ("WAIT",r'\bWAIT\b'),
        ("OPEN", r'\bOPEN\b'),
        ("READ", r'\bREAD\b'),
        ("WITH", r'\bWITH\b'),
        ("SET", r'\bSET\b'),
        ("IF", r'IF'),
        ("ELSE", r'ELSE'),
        ("LOG", r'\bLOG\b'),
        ("CLICK", r'\bCLICK\b'),
        ("WHILE", r'\bWHILE\b'),
        ("L_PAREN",r'\('),
        ("R_PAREN",r'\)'),
        ("L_BRACE", r'{'),
        ("R_BRACE", r'}'),
        ("STRING_LITERAL", r'"([^"]*)"'),
        ("IDENTIFIER", r'\b[a-z][a-zA-Z0-9_]*\b'),
        ("WHITESPACE", r'\s+'),

    ]
    def __init__(self):
        self.pattern = "|".join(
            f'(?P<{name}>{pattern})' for name, pattern in self.token_spec)
    def parse(self, filePath):
        with open(filePath, "r") as file:
            file_contents = file.read()
        return self.tokenize(file_contents)

    def tokenize(self, contents: List[str]):
        tokens = []
        for match in re.finditer(self.pattern, contents):
            group = match.lastgroup
            value = match.group()
            if group == 'COMMENTS':
                continue
            if group != "WHITESPACE":
                tokens.append((group, value))
        return tokens

if __name__ == "__main__":
    file_path =  sys.argv[1:][0]
    lexer = Lexer()
    tokens = lexer.parse(file_path)
    print('\n')
    print(file_path)
    print("----------------------")
    print(f"tokens:{tokens}")
    print("----------------------")
