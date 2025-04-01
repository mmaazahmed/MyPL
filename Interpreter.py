from parser import Parser
import sys
import asyncio
from playwright.async_api import async_playwright


class Interpreter:
    def __init__(self, filePath: str):
        self.parser = Parser()
        self.ast = self.parser.parse(filePath)
        self.variables = {}
        self.playwright = None
        self.browser = None
        self.page = None
        print(self.ast)

    async def initialize(self, isHeadless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=isHeadless)
        self.page = await self.browser.new_page()

    async def handle_assignment_expression(self, node):
        target_name = node["target"]["name"]
        value_node =node["value"]

        value = await self.get_node_value(value_node)

        if value is None:
            raise RuntimeError(
                f'Unsupported assignment type: {node["value"]["type"]}')
        self.variables[target_name] = value

    async def get_node_value(self, node):
        type =  node["type"]
        if type =='Identifier':
            variable = node["name"]
            if variable not in self.variables:
                raise RuntimeError(f'variable {variable} hasnt been defined yet')
            return self.variables[variable]
        elif type == 'Literal':
            return node["value"]

        return await self.execute(node)


    async def handle_log_expression(self, node):
        value = node["value"]
        if value["type"] == 'Literal':
            print(value["value"])
        else:
            print(await self.get_node_value(value))

    async def handle_navigate_expression(self,node):
        url = node["url"]
        if url["type"]=='Literal':
            await self.page.goto(url["value"])

    async def handle_read_expression(self,node):
        locator = node["target"]["value"]
        return await self.page.locator(locator).text_content()

    async def handle_element_interaction(self,node):
        locator = node["target"]["value"]
        actions = node["actions"]
        await self.page.locator(locator).wait_for(state='visible')
        for action in actions:
            await self.execute(action)

    async def handle_conditional_expression(self,node):
        conditional = node["conditional"]
        operator = conditional["operator"]
        left_value = await self.get_node_value(conditional["left"])
        right_value = await self.get_node_value(conditional["right"])
        result=None
        if operator  in ["==", "IS"]:
            result= left_value == right_value

        if operator == "HAS":
            result= right_value in left_value

        if result is None:
            raise RuntimeError(f"invalid conditional")

        if result:
            for action in node["then"]:
                await self.execute(action)
        else:
            for action in node["else"]:
                await self.execute(action)

    async def execute(self, node):

        type = node["type"]
        if type == 'ElementInteraction':
            return await self.handle_element_interaction(node)
        elif type == "FillExpression":
            return await self.handle_fill_expression(node)
        elif type == "AssignmentExpression":
            return await self.handle_assignment_expression(node)
        elif type == "ClickExpression":
            return await self.handle_click_expression(node)
        elif type == "NavigateExpression":
            return await self.handle_navigate_expression(node)
        elif type == "LogExpression":
            return await self.handle_log_expression(node)
        elif type == "ReadExpression":
            return await self.handle_read_expression(node)
        elif type == "ConditionalExpression":
            return await self.handle_conditional_expression(node)
        else:
            raise RuntimeError(
                f'unsupported {type}')

    async def close_browser(self):
        await self.browser.close()
        await self.playwright.stop()

    async def run(self):
        try:
            for node in self.ast["body"]:
                await self.execute(node)
        except Exception as e:
            print(f"Error during execution: {e}")
        finally:
            await self.close_browser()


async def main(file_path:str):
    i = Interpreter(file_path)
    await i.initialize(False)
    await i.run()

if __name__ == "__main__":
    file_path =  sys.argv[1:][0]
    print(f"Running script {file_path}")
    asyncio.run(main(file_path))
    print(f"Done executing script {file_path}")
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
