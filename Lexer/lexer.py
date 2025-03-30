
import re
from typing import List

token_spec = [
    # ("ACTION", r'\b[A-Z]+\b'),
    ("COMMENTS", r'#[^\n]*'),
    ("FILL", r'\bFILL\b'),
    ("ON", r'ON'),
    ("OPEN", r'OPEN'),
    ("READ", r'READ'),
    ("WITH", r'\bWITH\b'),
    ("SET", r'\bSET\b'),
    ("IF", r'IF'),
    ("HAS", r'HAS'),
    ("IS", r'IS'),
    ("EXISTS", r'EXISTS'),
    ("LOG", r'LOG'),
    ("CLICK", r'CLICK'),
    ("WHILE", r'WHILE'),
    ("L_BRACE", r'{'),
    ("R_BRACE", r'}'),
    ("STRING_LITERAL", r'"([^"]*)"'),
    ("IDENTIFIER", r'\b[a-z][a-zA-Z0-9_]*\b'),
    ("WHITESPACE", r'\s+'),

]
class Lexer:

    def __init__(self):
        self.tokens = []
        self.token_spec = token_spec

    def parse(self, filePath):
        with open(filePath, "r") as file:
            file_contents = file.read()
        self.lexer(file_contents)

    def lexer(self, contents: List[str]):
        pattern = "|".join(
            f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        for match in re.finditer(pattern, contents):
            group = match.lastgroup
            value = match.group()
            if group == 'COMMENTS':
                continue
            if group != "WHITESPACE":
                self.tokens.append((group, value))

    def get_tokens(self):
        return self.tokens

