import asyncio
import json
import os
import sys

async def main():
    """
    A local test client for the mcp-novelaigen server.
    This script starts the server as a subprocess and communicates with it over stdio,
    mimicking how the AstrBot environment would call the tool.
    """
    # --- Configuration ---
    # The API Key is now hardcoded for this local test to avoid environment issues.
    API_KEY = "pst-dhBc7AUK5nA4a4UT1o9cc6xVY6bHTdswfVzyHP2hgHY2HqdVqjX7IgtuwEqJYmfa"
    
    # Determine the path to the Python executable in the virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        # Fallback for non-Windows environments
        venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")

    # The command to run the MCP server using the virtual environment's Python
    # We run it as a module to ensure imports work correctly.
    # The "-v" flag makes Python print every module it imports.
    server_command = [venv_python, "-v", "-m", "mcp_novelaigen.server"]
    
    print(f"Starting server with command: {' '.join(server_command)}")

    # Create a copy of the current environment and add the API key and Proxy
    server_env = os.environ.copy()
    server_env["NOVELAI_API_KEY"] = API_KEY
    server_env["PROXY_SERVER"] = "http://127.0.0.1:7897"

    # Start the server as a subprocess
    process = await asyncio.create_subprocess_exec(
        *server_command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        # The CWD must be the project root where pyproject.toml is located
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=server_env  # Pass the modified environment to the subprocess
    )

    print(f"Server started with PID: {process.pid}")

    # Helper to read messages from server's stdout with a timeout
    async def read_message(timeout=60.0):
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=timeout)
            if not line:
                return None
            return json.loads(line.decode('utf-8'))
        except asyncio.TimeoutError:
            print(f"Error: Timed out after {timeout} seconds waiting for a message from the server.", file=sys.stderr)
            return None
        except (asyncio.IncompleteReadError, json.JSONDecodeError) as e:
            print(f"Error reading/decoding message from server: {e}", file=sys.stderr)
            return None

    # 1. Wait for the server's `initialize` response (optional but good practice)
    print("Waiting for server to initialize...")
    init_response = await read_message(timeout=15.0)  # Shorter timeout for initialization
    print(f"Received Initialize Response: {json.dumps(init_response, indent=2)}")
    if not init_response or 'result' not in init_response:
        print("Failed to get a valid initialization response from the server.", file=sys.stderr)
        process.terminate()
        await process.wait()
        return

    # 2. Send a `list_tools` request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "list_tools",
        "params": {}
    }
    print(f"\nSending List Tools Request: {json.dumps(list_tools_request, indent=2)}")
    process.stdin.write(json.dumps(list_tools_request).encode('utf-8') + b'\n')
    await process.stdin.drain()
    
    list_tools_response = await read_message()
    print(f"Received List Tools Response: {json.dumps(list_tools_response, indent=2)}")


    # 3. Send a `call_tool` request
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "call_tool",
        "params": {
            "name": "NovelAIGen",
            "arguments": {
                "prompt": "1girl, best quality, amazing quality, very aesthetic, absurdres",
                "resolution": "832x1216",
                "negative_prompt": "lowres, bad anatomy, bad hands, text, error"
            }
        }
    }
    print(f"\nSending Call Tool Request: {json.dumps(call_tool_request, indent=2)}")
    process.stdin.write(json.dumps(call_tool_request).encode('utf-8') + b'\n')
    await process.stdin.drain()

    # 4. Read the result
    call_tool_response = await read_message()
    print("\n--- Received Call Tool Response ---")
    if call_tool_response:
        # Pretty print the JSON response
        print(json.dumps(call_tool_response, indent=2, ensure_ascii=False))
        
        # Check if the result contains image data and give a summary
        if 'result' in call_tool_response and isinstance(call_tool_response['result'], list):
            for item in call_tool_response['result']:
                if item.get('type') == 'image' and item.get('data'):
                    print("\n[SUCCESS] The response contains image data!")
                elif item.get('type') == 'text':
                     print(f"\n[INFO] The response contains a text message: {item.get('text')}")

    else:
        print("[FAILURE] Did not receive a valid response for the tool call.", file=sys.stderr)

    # 5. Clean up
    print("\n--- Test Finished ---")
    if process.returncode is None:
        print("Terminating server process...")
        process.terminate()
    
    # Drain stderr to see any errors from the server
    stderr_output = await process.stderr.read()
    if stderr_output:
        print("\n--- Server Stderr Output ---", file=sys.stderr)
        print(stderr_output.decode('utf-8', errors='ignore'), file=sys.stderr)
        
    await process.wait()
    print(f"Server process exited with code: {process.returncode}")


if __name__ == "__main__":
    asyncio.run(main())