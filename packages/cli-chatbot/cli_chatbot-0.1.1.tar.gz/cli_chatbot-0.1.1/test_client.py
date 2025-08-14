import asyncio
from client import MCPClient

async def test_client():
    try:
        print("Testing MCP Client with fixed tool schemas...")
        async with MCPClient("presigned_url.py") as client:
            print("Connected successfully!")
            
            # Test a simple query
            response = await client.process_query("hello")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_client())
