#!/usr/bin/env python3
import re
from typing import List
# import asyncio
# from playwright.async_api import async_playwright

# async def run():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # Launch browser
#         page1 = await browser.new_page()
#         page2 = await browser.new_page()
#         await asyncio.gather(
#             page1.goto("https://google.com"),    # Load page2 in parallel
#             page2.goto("https://facebook.com")
#         )
#         # page2.click()
#         await page2.fill('input[name="email"]', 'your_email@example.com')
#         await page2.fill('input[type="password"]', 'your_email@example.com')
#         # await browser.close()

# asyncio.run(run())


class Lexer:

    def __init__(self, token_spec: List[str]):
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


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.ast = None

    def peek(self, offset=0):
        return self.tokens[self.index+offset] if self.index+offset < len(self.tokens) else None

    def expect(self, expected_type):
        token = self.consume()
        if token and token[0] != expected_type:
            raise SyntaxError(
                f'Invalid syntax expected {expected_type} got {token[0]}')
        return token

    def match(self, expected_type,offset=0):
        return self.peek(offset) and self.peek(offset)[0] == expected_type

    def consume(self):
        if self.index >= len(self.tokens):
            return None
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse_navigation(self):
        self.expect("OPEN")
        url_token = self.expect('INPUT')
        return {
            "type": "Navigate",
            "url": url_token[1]
        }

    def parse_block(self):
        actions = []
        while not self.match('R_BRACE'):
            actions.append(self.parse_statement())
        return actions

    def parse_assignment(self):
        self.expect('AS')
        value = self.peek(-2)[1]
        variable = self.expect('IDENTIFIER')[1]
        return {
            "type": "Assignment",
            "value": value,
            "variable": variable
        }

    def parse_element_interaction(self):
        self.expect('ON')
        selector = self.expect("INPUT")[1]
        assignment = None
        if self.match("AS"):
            assignment = self.parse_statement()
        self.expect('L_BRACE')
        actions = self.parse_block()
        self.expect('R_BRACE')
        return {
            "type": "ElementInteraction",
            "assignment": assignment,
            "selector": selector,
            "wait": True,
            "actions": actions
        }

    def parse_arguments(self):
        result = {}
        if self.match('INPUT'):
            result["type"] = 'Literal'
            result["value"] = self.consume()[1]
        elif self.match('IDENTIFIER'):
            result["type"] = 'variable'
            result["name"] = self.consume()[1]

        return result

    def parse_fill(self):
        self.expect('FILL')
        left = self.parse_arguments()
        self.expect('WITH')
        right = self.parse_arguments()
        return {
            "type": "Fill",
            "selector": left,
            "input": right
        }

    def parse_read(self):
        self.expect('READ')
        selector = self.parse_arguments()
        assignment = None
        if self.match('AS', 1):
            assignment = self.parse_assignment()
        return {
            "type": 'Read',
            "assignment": assignment,
            "selector": selector,
        }

    def parse_statement(self):
        token = self.peek()
        if token[1] == "OPEN":
            return self.parse_navigation()
        elif token[1] == "ON":
            return self.parse_element_interaction()
        elif token[1] == "FILL":
            return self.parse_fill()
        elif token[1] == 'AS':
            return self.parse_assignment()
        elif token[1] == 'READ':
            return self.parse_read()
        else:
            raise SyntaxError(f'unknown Action {token[1]}')

    def parse(self):
        body = []
        while self.peek():
            node = self.parse_statement()
            body.append(node)
        self.ast = {"type": "Program", "body": body}
        return self.ast


token_spec = [
    # ("ACTION", r'\b[A-Z]+\b'),
    ("COMMENTS", r'#[^\n]*'),
    ("FILL", r'\bFILL\b'),
    ("ON", r'ON'),
    ("OPEN", r'OPEN'),
    ("READ", r'READ'),
    ("WITH", r'\bWITH\b'),
    ("AS", r'AS'),
    ("IF", r'IF'),
    ("HAS", r'HAS'),
    ("IS", r'IS'),
    ("EXISTS", r'EXISTS'),
    ("LOG", r'LOG'),
    ("CLICK", r'CLICK'),
    ("WHILE", r'WHILE'),
    ("L_BRACE", r'{'),
    ("R_BRACE", r'}'),
    ("INPUT", r'"([^"]*)"'),
    ("IDENTIFIER", r'\b[a-z][a-zA-Z_]*\b'),
    ("WHITESPACE", r'\s+'),

]
lexer = Lexer(token_spec)
lexer.parse("./start.mypl")
tokens = lexer.get_tokens()
print(tokens)
Parser = Parser(tokens)
ast = Parser.parse()
print(ast)
