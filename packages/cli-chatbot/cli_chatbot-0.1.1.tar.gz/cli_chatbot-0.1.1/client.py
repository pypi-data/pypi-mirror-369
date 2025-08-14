import asyncio
from dotenv import load_dotenv
from fastmcp import Client as FastMCPClient
import litellm
import json

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.client: FastMCPClient = None

    async def __aenter__(self):
        self.client = await FastMCPClient(self.server_script_path).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc, tb)

    async def list_tools(self):
        tools = await self.client.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        return tools


    async def process_query(self, query: str) -> str:
        """Process a query using Claude (via litellm) and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            tools = await self.client.list_tools()
            response = litellm.completion(
                model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
                messages=messages,
                max_tokens=1000,
                tools=tools
                )
        except Exception as e:
            print(f"Error during tool processing: {e}")
            # Fallback to no tools
            print("Falling back to API call without tools")
            response = litellm.completion(
                model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
                messages=messages,
                max_tokens=1000
            )
        # Initial Claude API call using litellm
        final_text = []

        # litellm returns response['choices'][0]['message']
        content = response["choices"][0]["message"]
        if content.get("tool_calls"):
            for tool_call in content["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                # tool_args is a JSON string, parse it
                tool_args_dict = json.loads(tool_args)
                result = await self.client.call_tool(tool_name, tool_args_dict)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args_dict}]")
                # Continue conversation with tool results
                messages.append({
                    "role": "assistant",
                    "content": content.get("content", "")
                })
                messages.append({
                    "role": "user",
                    "content": result.text
                })
                # Get next response from Claude
                response = litellm.completion(
                    model="claude-3-5-sonnet-20241022",
                    messages=messages,
                    max_tokens=1000
                )
                next_content = response["choices"][0]["message"]
                final_text.append(next_content.get("content", ""))
        else:
            final_text.append(content.get("content", ""))

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")


async def main():
    print("MCP Client Startup")
    print("==================")
    
    # Use default server script for testing
    server_script = "presigned_url.py"
    
    # Ask user for server script path
    user_input = input(f"\nEnter the path to your MCP server script (default: {server_script}): ").strip()
    if user_input:
        server_script = user_input
    
    # Check if file exists
    import os
    if not os.path.exists(server_script):
        print(f"File '{server_script}' not found. Please check the path.")
        return
    
    print(f"\nConnecting to MCP server: {server_script}")
    
    try:
        async with MCPClient(server_script) as client:
            await client.list_tools()
            await client.chat_loop()
    except Exception as e:
        print(f"\nFailed to connect to MCP server: {str(e)}")
        print("Please check that the server script is correct and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
