# Browser-Use MCP Console 测试指南

## 版本 0.1.1 测试流程

### 1. 快速测试（推荐）

在 PowerShell 中运行：

```powershell
# 进入项目目录
cd D:\supie\202507\browser_use_mcp

# 安装到当前 Python 环境
pip install -e .

# 运行快速测试
python quick_test.py
```

**预期结果**：
- ✅ 服务器能正常启动
- ✅ 没有窗口弹出（test.png 不再出现）
- ✅ 显示 "服务器启动成功"

### 2. 完整测试（需要虚拟环境）

#### Windows PowerShell:

```powershell
# 运行设置脚本
.\test_setup.ps1

# 在虚拟环境中测试
python test_mcp_client.py
```

#### 手动步骤:

```powershell
# 1. 创建虚拟环境
python -m venv test_env

# 2. 激活虚拟环境
.\test_env\Scripts\Activate.ps1

# 3. 安装依赖
pip install mcp
pip install -e .

# 4. 设置 API key（用于测试）
$env:OPENAI_API_KEY = "test-key-123"

# 5. 运行测试客户端
python test_mcp_client.py
```

### 3. MCP Inspector 测试

使用官方 MCP Inspector 工具：

```bash
# 安装 Inspector
npm install -g @modelcontextprotocol/inspector

# 测试服务器
mcp-inspector browser-use-mcp-console
```

### 4. Claude Desktop 集成测试

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "browser-use": {
      "command": "uvx",
      "args": ["browser-use-mcp-console"],
      "env": {
        "OPENAI_API_KEY": "your-actual-key"
      }
    }
  }
}
```

## 验证要点

### ✅ 版本 0.1.1 应该修复的问题：

1. **窗口弹出问题**
   - 运行 `browser-use-mcp-console` 不应该打开任何窗口
   - 不应该生成 `test.png` 文件
   - 原因：已将 `playwright show-trace` 改为 `playwright --version`

2. **Playwright 检测**
   - 如果未安装 Playwright，应该显示警告信息
   - 不会因为 Playwright 未安装而崩溃

3. **正常功能**
   - 能正常接收和处理 MCP 请求
   - 能执行浏览器自动化任务
   - Console 工具能正常工作

## 常见问题

### 1. "找不到 browser-use-mcp-console 命令"

```bash
# 确保已安装
pip install -e .

# 或从 PyPI 安装
pip install browser-use-mcp-console==0.1.1
```

### 2. "Playwright 未安装"

```bash
# 安装 Playwright 和 Chromium
playwright install chromium --with-deps
```

### 3. "API key 错误"

设置真实的 API key：
```powershell
$env:OPENAI_API_KEY = "your-real-api-key"
# 或
$env:ANTHROPIC_API_KEY = "your-real-api-key"
```

## 发布前检查清单

- [ ] 运行 `quick_test.py` 无窗口弹出
- [ ] 版本号已更新为 0.1.1
- [ ] `playwright show-trace` 已改为 `playwright --version`
- [ ] README 已更新
- [ ] 在干净环境中测试安装

## 发布命令

```bash
# 构建
python -m build

# 检查
twine check dist/*

# 上传到 PyPI
twine upload dist/*
```