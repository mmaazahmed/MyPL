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
            if group != "WHITESPACE":
                self.tokens.append((group, value))

    def get_tokens(self):
        return self.tokens


token_spec = [
    ("KEYWORD", r'\b[A-Z]+\b'),
    ("PUNCTUATION",r':'),
    ("ACTION", r'[A-Z][a-z]*'),
    ("INPUT",r'"([^"]*)"'),
    ("NUMBER", r'\d+'),
    ("VARIABLE", r'[a-z][a-zA-Z]*'),
    ("WHITESPACE", r'\s+'),
]
lexer = Lexer(token_spec)
lexer.parse("./test.mypl")
print(lexer.get_tokens())
# class Interpreter:
#    def __init__(self):
#        self.program=[]
