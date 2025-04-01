#!/usr/bin/env python3
import sys
from Lexer.lexer import Lexer


class Parser:
    def __init__(self):
        self.lexer = Lexer()
        self.tokens = None
        self.index = 0
        self.ast = None

    def peek(self, offset=0):
        return self.tokens[self.index+offset] if self.index+offset < len(self.tokens) else None

    def expect(self, expected_type):
        token = self.consume()
        if not token:
            raise SyntaxError(
                f'Invalid syntax missing {expected_type}')

        if token and token[0] != expected_type:
            raise SyntaxError(
                f'Invalid syntax expected {expected_type} got {token[0]}:"{token[1]}"')
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
        url= self.parse_literal()
        return {
            "type": "NavigateExpression",
            "url": url
        }

    def parse_block(self):
        actions = []
        self.expect('L_BRACE')
        while not self.match('R_BRACE') and self.peek() is not None:
            actions.append(self.parse_statement())
        self.expect('R_BRACE')
        return actions

    def parse_assignment(self):
        self.expect('SET')
        variable = self.expect('IDENTIFIER')[1]
        self.expect('WITH')
        value = None
        if self.match('READ'):
            value = self.parse_read()
        else:
            # handle varibale or literal
            value = self.parse_expression()

        return {
            'type': "AssignmentExpression",
            'target': {"type": 'Identifier', "name": variable},
            'value': value,
        }

    def parse_element_interaction(self):
        self.expect('ON')
        locator = self.parse_expression()
        actions = self.parse_block()
        return {
            "type": "ElementInteraction",
            "target": locator,
            "wait": True,
            "actions": actions
        }

    def parse_primary(self):
        result = {}
        if self.match('STRING_LITERAL'):
            result["type"] = 'Literal'
            result["value"] = self.consume()[1].strip("\"")
        elif self.match('IDENTIFIER'):
            result["type"] = 'Identifier'
            result["name"] = self.consume()[1]
        elif self.match("INTEGER_LITERAL"):
            result["type"] = 'Literal'
            result["value"] = int(self.consume()[1])
        else:
            raise SyntaxError(f"expected indentifiers,integer literals or string literals but got {self.peek()}")

        return result

    def parse_fill(self):
        self.expect('FILL')
        left = self.parse_expression()
        self.expect('WITH')
        right = self.parse_expression()
        return {
            "type": "FillExpression",
            "target": left,
            "value": right
        }

    def parse_read(self):
        self.expect('READ')
        locator = self.parse_locator()
        return {
            "type": 'ReadExpression',
            "target": locator
        }
    def parse_try_catch(self):
        self.expect('TRY')
        try_block = self.parse_block()
        self.expect('CATCH')
        catch_block = self.parse_block()
        return {
            "type":"TryCatchExpression",
            "try":try_block,
            "catch":catch_block
        }
    def parse_click(self):
        self.expect('CLICK')
        locator = self.parse_expression()
        return {
            "type": 'ClickExpression',
            "target": locator
        }
    def parse_literal(self):
        literal = self.expect('STRING_LITERAL')[1].strip("\"")
        return {
            "type":"Literal",
            "value":literal
        }

    def parse_identifier(self):
        name = self.expect('IDENTIFIER')[1]
        return {
            "type":"Identifier",
            "name":name
        }
    def parse_locator(self):
        value = self.expect('STRING_LITERAL')[1].strip("\"")
        return {
            "type":"Locator",
            "value":value
        }
    def parse_log(self):
        self.expect('LOG')
        value = None
        if self.match('STRING_LITERAL'):
            value = self.parse_literal()
        elif self.match('IDENTIFIER') :
            value = self.parse_identifier()
        else:
            value = self.parse_statement()

        return {
            "type": 'LogExpression',
            "value": value,
        }

    def parse_logical_expression(self):
        left = self.parse_expression()
        operator = self.expect("LOGICAL_OPERATOR")[1]
        right = self.parse_expression()
        return {
            "type": 'BinaryExpression',
            "operator": operator,
            "left": left,
            "right": right,
        }

    def parse_conditional(self):
        self.expect("IF")
        self.expect("L_PAREN")
        conditional = self.parse_logical_expression()
        self.expect("R_PAREN")
        then_block = self.parse_block()
        else_block = None
        if self.match("ELSE"):
            self.consume()
            else_block = self.parse_block()

        return {
            "type": "ConditionalExpression",
            "conditional": conditional,
            "then": then_block,
            "else": else_block
        }

    def parse_while_loop(self):
        self.expect('WHILE')
        condition = self.parse_logical_expression()
        block = self.parse_block()
        return {
            "type":"WhileLoopExpression",
            "conditional":condition,
            "block":block
        }
    def parse_wait(self):
        self.expect('WAIT')
        duration = self.parse_expression()
        return {
            "type":"WaitExpression",
            "duration":duration
        }

    def parse_expression(self):
        left = self.parse_primary()
        if not self.match("ARITHMETIC_OPERATOR"):
            return left
        operator = self.consume()[1]
        right = self.parse_expression()
        return {
            "type": "BinaryExpression",
            "operator": operator,
            "left": left,
            "right": right,
        }

    def parse_statement(self):
        token = self.peek()
        if token[0] == "OPEN":
            return self.parse_navigation()
        elif token[0] == "ON":
            return self.parse_element_interaction()
        elif token[0] == "FILL":
            return self.parse_fill()
        elif token[0] == 'SET':
            return self.parse_assignment()
        elif token[0] == 'READ':
            return self.parse_read()
        elif token[0] == 'CLICK':
            return self.parse_click()
        elif token[0] == 'LOG':
            return self.parse_log()
        elif token[0] == 'IF':
            return self.parse_conditional()
        elif token[0] == 'TRY':
            return self.parse_try_catch()
        elif token[0] == 'WHILE':
            return self.parse_while_loop()
        elif token[0] == 'WAIT':
            return self.parse_wait()
        elif token[0] in ["INTEGER_LITERAL", "STRING_LITERAL", "IDENTIFIER"]:
            return self.parse_expression()
        else:
            raise SyntaxError(f'unknown Action {token}')

    def parse(self, filePath: str):
        body = []
        self.tokens = self.lexer.parse(filePath)
        while self.peek():
            node = self.parse_statement()
            body.append(node)
        self.ast = {"type": "Program", "body": body}
        return self.ast


if __name__ == "__main__":
    file_path =  sys.argv[1:][0]
    Parser = Parser()
    ast = Parser.parse(file_path)
    print('\n')
    print(file_path)
    print("----------------------")
    print(f"ast:{ast}")
    print("----------------------")
