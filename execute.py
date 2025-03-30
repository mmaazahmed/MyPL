from parser import Parser
class Interpreter:
    def __init__(self,filePath:str):
        self.parser = Parser(filePath)
        self.ast =self.parser.parse()
        self.variables={}
        # print(self.ast)
    # def handle_playwright_command(self,node):
    #     pass

    def handle_assignment_expression(self, node):
        target_name = node["target"]["name"]
        if node["value"]["type"] == 'Identifier':
            self.variables[target_name] = self.get_variable_value(node["value"]["name"])
        elif node["value"]["type"] == 'Literal':
            self.variables[target_name] = node["value"]["value"]
        elif node["value"]["type"] == 'ReadExpression':
            self.variables[target_name] = self.handle_read_expression(node["value"])
        else:
            raise RuntimeError(f'Unsupported assignment type: {node["value"]["type"]}')

    # def handle_read_expression(self,node):
    #     target = node["target"]
    #     if target["value"] ==
    def get_variable_value(self,variable):
        if variable not in self.variables:
            raise RuntimeError(
                f'variable {node["value"]["name"]} hasnt been defined yet')
        return self.variables[variable]

    def handle_log_expression(self, node):
        value = node["value"]
        if value["type"] == 'Literal':
            print(value["value"])
        else:
            variable = node["value"]["name"]
            print(self.get_variable_value(variable))

    def execute(self, node):
        # print(node)
        type = node["type"]
        if type == 'ElementInteraction':
            self.handle_element_interaction(node)
        elif type == "FillExpression":
            self.handle_fill_expression(node)
        elif type == "AssignmentExpression":
            self.handle_assignment_expression(node)
        elif type == "ClickExpression":
            self.handle_click_expression(node)
        elif type == "NavigateExpression":
            self.handle_navigate_expression(node)
        elif type == "LogExpression":
            self.handle_log_expression(node)
        elif type == "ReadExpression":
            self.handle_read_expression(node)

    def run(self):
        for node in self.ast["body"]:
            # print(node)
            self.execute(node)
        # print(self.ast)

i = Interpreter('./code.mypl')
i.run()
# {
#   "type": "Program",
#   "body": [
#     {
#       "type": "ElementInteraction",
#       "target": {
#         "type": "Locator",
#         "value": "#login-form"
#       },
#       "wait": true,
#       "actions": [
#         {
#           "type": "FillExpression",
#           "target": {
#             "type": "Literal",
#             "value": "#username"
#           },
#           "value": {
#             "type": "Literal",
#             "value": "test_user"
#           }
#         },
#         {
#           "type": "FillExpression",
#           "target": {
#             "type": "Literal",
#             "value": "#password"
#           },
#           "value": {
#             "type": "Identifier",
#             "name": "password_variable"
#           }
#         },
#         {
#           "type": "ClickExpression",
#           "target": {
#             "type": "Locator",
#             "value": "#submit"
#           }
#         }
#       ]
#     }
#   ]
# }
