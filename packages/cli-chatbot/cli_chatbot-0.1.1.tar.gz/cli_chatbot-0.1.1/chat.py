from fastmcp import Client
import asyncio
import litellm
import json
import warnings

# Ignore warnings
warnings.filterwarnings("ignore")

class ChatCli:
    def __init__(self, name:str, transport: str):
        self.name = name
        self.client = Client(transport)
        self.llm_model = "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0"
        self.history = []
        self.tools = []
        self.llm_config = {}

    async def list_tools(self):
        tools = await self.client.list_tools()
        for tool in tools:
            _tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema or {"type": "object", "properties": {}}
                }
            }
            self.tools.append(_tool)
        return self.tools

    async def close(self):
        await self.client.close()

    async def llm_response(self, messages: list[dict], use_tool=False):
        response = await litellm.acompletion(
            model=self.llm_model,
            messages=messages,
            max_tokens=1000,
            tools=self.tools if use_tool and self.tools else None
        )
        return response["choices"][0]["message"]

    async def query(self, query: str):
        self.history.append({"role": "user", "content": query})
        while True:
            content = await self.llm_response(self.history, use_tool=True)
            if content.get("content"):
                self.history.append({
                    "role": "assistant",
                    "content": content["content"]
                })
            # If there are tool calls, process them sequentially
            if content.get("tool_calls"):
                for tool_call in content["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]
                    tool_args_dict = json.loads(tool_args)
                    tool_call_text = f"[Calling tool {tool_name} with args {tool_args_dict}]"
                    print(tool_call_text)
                    try:
                        result = await self.client.call_tool(tool_name, tool_args_dict)
                        tool_return_text = f"[Tool {tool_name} returned: {result.content}]"
                    except Exception as e:
                        tool_return_text = f"[Tool {tool_name} failed: {str(e)}]"

                    print(tool_return_text)
                    # Add tool result to history for next LLM response
                    self.history.append({
                        "role": "user",
                        "content": tool_call_text + "\n" + tool_return_text
                    })
                # Continue the loop to check for more tool calls in the next LLM response
                continue
            else:
                break
        return self.history[-1]["content"]

    async def chat(self):
        async with self.client:
            await self.list_tools()
            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                response = await self.query(user_input)
                print(f"Bot: {response}")


if __name__ == "__main__":
    chat_cli = ChatCli("BOT", "presigned_url.py")
    response = asyncio.run(chat_cli.chat())
