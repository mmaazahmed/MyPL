from parser import Parser
import sys
import asyncio
from playwright.async_api import async_playwright, Error,TimeoutError

class Interpreter:
    def __init__(self):
        self.parser = Parser()
        self.variables = {}
        self.playwright = None
        self.browser = None
        self.page = None
        self.ast =None

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
        elif type == 'Locator':
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
        locator = await self.get_node_value(node["target"])
        return await self.page.locator(locator).first.text_content()

    async def handle_element_interaction(self,node):
        locator = await self.get_node_value(node["target"])
        actions = node["actions"]
        await self.page.locator(locator).wait_for(state='visible')
        for action in actions:
            await self.execute(action)

    async def handle_try_catch_expression(self, node):
        try_block = node["try"]
        catch_block = node["catch"]
        try:
            for try_action in try_block:
                await self.execute(try_action)
        except (RuntimeError, Error, TimeoutError):
            for catch_action in catch_block:
                await self.execute(catch_action)
        except Exception as e:
            print(f"unexpected interpreter error: {e}")
            raise

    async def handle_condition(self, node):
        operator = node["operator"]
        left_value = await self.get_node_value(node["left"])
        right_value = await self.get_node_value(node["right"])
        result = None
        if operator in ["==", "IS"]:
            result = left_value == right_value

        if operator == "HAS" and isinstance(left_value, (str, list)):
            result = right_value in left_value
        if operator =='<':
            return left_value < right_value
        if operator =='<=':
            return left_value <= right_value

        if result is None:
            raise RuntimeError(f"invalid conditional")
        return result

    async def handle_conditional_expression(self, node):
        result = await self.handle_condition(node["conditional"])
        if result:
            for action in node["then"]:
                await self.execute(action)
        else:
            for action in node["else"]:
                await self.execute(action)

    async def handle_fill_expression(self, node):
        target = await self.get_node_value(node["target"])
        value = await self.get_node_value(node["value"])
        await self.page.locator(target).fill(value)

    async def handle_click_expression(self,node):
        target = await self.get_node_value(node["target"])
        await self.page.locator(target).click()

    async def handle_while_expression(self,node):
        while await self.handle_condition(node["conditional"]):
            for statement in node["block"]:
                await self.execute(statement)

    async def handle_wait_expression(self,node):
        duration = await self.get_node_value(node["duration"])
        await asyncio.sleep(duration)

    async def handle_binary_expression(self,node):
        operator = node["operator"]
        left = await self.get_node_value(node["left"])
        right = await self.get_node_value(node["right"])
        if operator =='+':
            return left + right
        if operator =='-':
            return left - right
        raise RuntimeError(f"unsupported operator {operator}")

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
        elif type == "TryCatchExpression":
            return await self.handle_try_catch_expression(node)
        elif type == "WhileLoopExpression":
            return await self.handle_while_expression(node)
        elif type == "WaitExpression":
            return await self.handle_wait_expression(node)
        elif type == "BinaryExpression":
            return await self.handle_binary_expression(node)
        else:
            raise RuntimeError(
                f'unsupported {type}')

    async def close_browser(self):
        await self.browser.close()
        await self.playwright.stop()

    async def run(self,file_path:str):
        try:
            self.ast = self.parser.parse(file_path)
            for node in self.ast["body"]:
                await self.execute(node)
            print(f"Done executing script {file_path}")
        except Exception as e:
            print(type(e))
            print(f"Error during execution: file:{file_path} {e}")
            print("------------------------------------")
            print("AST\n",self.ast)
            print("------------------------------------")
            print("Tokens\n",self.parser.tokens)
        finally:
            await self.close_browser()


async def main(file_path:str,flag):
    i = Interpreter()
    await i.initialize(False)
    await i.run(file_path)
    if (flag in ["--debug","-d"]):
        print("------------------------------------")
        print("AST\n",i.ast)
        print("------------------------------------")
        print("Tokens\n",i.parser.tokens)

if __name__ == "__main__":
    file_path =  sys.argv[1]
    flag =None
    if len(sys.argv)>=3:
        flag =  sys.argv[2]

    print(f"starting interpreter {file_path}")
    try:
        asyncio.run(main(file_path,flag))
    except Exception as e:
        print(f"Error occurred while starting up interpreter  {file_path}: {e}")
