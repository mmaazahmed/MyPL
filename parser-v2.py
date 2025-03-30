#!/usr/bin/env python3
from Lexer.lexer import Lexer


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

    def match(self, expected_type, offset=0):
        return self.peek(offset) and self.peek(offset)[0] == expected_type

    def consume(self):
        if self.index >= len(self.tokens):
            return None
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse_navigation(self):
        self.expect("OPEN")
        url_token = self.expect('STRING_LITERAL')
        return {
            "type": "Navigate",
            "url": {"type": 'Literal', "value": url_token[1]}
        }

    def parse_block(self):
        actions = []
        while not self.match('R_BRACE'):
            actions.append(self.parse_statement())
        return actions

    def parse_assignment(self):
        self.expect('SET')
        variable = self.expect('IDENTIFIER')[1]
        self.expect('WITH')
        value = None
        if self.match('READ'):
            # handle dom read
            value = self.parse_read()
        else:
            # handle varibale or literal
            value = self.parse_arguments()

        return {
            'type': "Assignment",
            'target': {"type": 'Identifier', "name": variable},
            'value': value,
        }

    def parse_element_interaction(self):
        self.expect('ON')
        locator = self.expect("STRING_LITERAL")[1].strip("\'")
        self.expect('L_BRACE')
        actions = self.parse_block()
        self.expect('R_BRACE')
        return {
            "type": "ElementInteraction",
            "target": {"type": 'Locator', "value": locator},
            "wait": True,
            "actions": actions
        }

    def parse_arguments(self):
        result = {}
        if self.match('STRING_LITERAL'):
            result["type"] = 'Literal'
            result["value"] = self.consume()[1]
        elif self.match('IDENTIFIER'):
            result["type"] = 'Identifier'
            result["name"] = self.consume()[1]

        return result

    def parse_fill(self):
        self.expect('FILL')
        left = self.parse_arguments()
        self.expect('WITH')
        right = self.parse_arguments()
        return {
            "type": "FillExpression",
            "target": left,
            "value": right
        }

    def parse_read(self):
        self.expect('READ')
        locator = self.expect('STRING_LITERAL')[1].strip("\'")
        return {
            "type": 'ReadExpression',
            "target": {"type": 'Locator', "value": locator},
        }

    def parse_click(self):
        self.expect('CLICK')
        locator = self.expect('STRING_LITERAL')[1].strip("\'")
        return {
            "type": 'ClickExpression',
            "target": {"type": 'Locator', "value": locator},
        }

    def parse_statement(self):
        token = self.peek()
        if token[1] == "OPEN":
            return self.parse_navigation()
        elif token[1] == "ON":
            return self.parse_element_interaction()
        elif token[1] == "FILL":
            return self.parse_fill()
        elif token[1] == 'SET':
            return self.parse_assignment()
        elif token[1] == 'READ':
            return self.parse_read()
        elif token[1] == 'CLICK':
            return self.parse_click()
        else:
            raise SyntaxError(f'unknown Action {token[1]}')

    def parse(self):
        body = []
        while self.peek():
            node = self.parse_statement()
            body.append(node)
        self.ast = {"type": "Program", "body": body}
        return self.ast


lexer = Lexer()
lexer.parse("./code.mypl")
tokens = lexer.get_tokens()
# print(tokens)
Parser = Parser(tokens)
ast = Parser.parse()
Parser.print_ast()
print(ast)
