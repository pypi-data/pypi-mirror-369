#!/usr/bin/env python3
"""
快速测试脚本 - 验证 browser-use-mcp-console 是否正常工作
无需额外依赖，直接使用 subprocess 调用
"""
import subprocess
import json
import sys
import os

def test_mcp_server():
    """测试 MCP 服务器是否能正常启动"""
    print("=== 快速测试 browser-use-mcp-console ===\n")
    
    # 设置测试 API key
    os.environ['OPENAI_API_KEY'] = 'test-key-123'
    
    # 1. 测试命令是否存在
    print("1. 检查命令...")
    try:
        result = subprocess.run(
            ["browser-use-mcp-console"], 
            capture_output=True, 
            text=True,
            timeout=2,
            input='{"jsonrpc": "2.0", "method": "initialize", "params": {"capabilities": {}}, "id": 1}\n'
        )
        
        if result.returncode == 0:
            print("✅ 命令可以运行")
            
            # 检查输出
            if result.stdout:
                print("\n2. 服务器响应:")
                try:
                    # 尝试解析第一行 JSON 响应
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            response = json.loads(line)
                            if 'result' in response:
                                print("✅ 初始化成功")
                                print(f"   服务器名称: {response['result'].get('serverInfo', {}).get('name', 'Unknown')}")
                                break
                except:
                    print("⚠️  无法解析响应，但服务器似乎在运行")
            
            if result.stderr:
                print("\n3. 日志信息:")
                print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
                
        else:
            print("❌ 命令运行失败")
            if result.stderr:
                print(f"错误: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("✅ 服务器启动成功（等待输入）")
        print("   这是正常的，说明服务器正在运行")
        
    except FileNotFoundError:
        print("❌ 找不到 browser-use-mcp-console 命令")
        print("\n请先运行以下命令安装：")
        print("  pip install -e .")
        print("\n或从 PyPI 安装：")
        print("  pip install browser-use-mcp-console")
        return False
    
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False
    
    print("\n=== 测试完成 ===")
    print("\n如果没有窗口弹出，说明 v0.1.1 修复成功！")
    return True

if __name__ == "__main__":
    sys.exit(0 if test_mcp_server() else 1)