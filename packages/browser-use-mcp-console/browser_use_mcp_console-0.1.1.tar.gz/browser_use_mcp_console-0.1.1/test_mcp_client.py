#!/usr/bin/env python3
"""
MCP Client Test Script
用于测试 browser-use-mcp-console 服务器
"""
import json
import subprocess
import sys
from pathlib import Path

def send_request(process, request):
    """发送 JSON-RPC 请求到 MCP 服务器"""
    request_str = json.dumps(request) + '\n'
    process.stdin.write(request_str.encode())
    process.stdin.flush()
    
    # 读取响应
    response_line = process.stdout.readline()
    if response_line:
        return json.loads(response_line)
    return None

def test_mcp_server():
    """测试 MCP 服务器功能"""
    print("Starting MCP server test...")
    
    # 启动 MCP 服务器
    cmd = [sys.executable, "-m", "browser_use_mcp.server"]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    try:
        # 1. 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        }
        
        print("Sending initialize request...")
        response = send_request(process, init_request)
        print(f"Initialize response: {response}")
        
        # 2. 列出可用工具
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("\nListing available tools...")
        response = send_request(process, list_tools_request)
        if response and 'result' in response:
            tools = response['result'].get('tools', [])
            print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # 3. 测试调用工具（不实际执行）
        call_tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "run_browser_tasks",
                "arguments": {
                    "tasks": ["Test task"],
                    "headless": True,
                    "max_steps": 1
                }
            },
            "id": 3
        }
        
        print("\nTesting tool call (this will fail without API key)...")
        response = send_request(process, call_tool_request)
        print(f"Tool call response: {response}")
        
    finally:
        # 关闭服务器
        process.terminate()
        process.wait()
        print("\nTest completed!")

if __name__ == "__main__":
    # 设置测试环境变量
    import os
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    test_mcp_server()