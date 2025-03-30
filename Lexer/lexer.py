
import re
from typing import List

class Lexer:

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
        ("LOG", r'\bLOG\b'),
        ("CLICK", r'CLICK'),
        ("WHILE", r'WHILE'),
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
