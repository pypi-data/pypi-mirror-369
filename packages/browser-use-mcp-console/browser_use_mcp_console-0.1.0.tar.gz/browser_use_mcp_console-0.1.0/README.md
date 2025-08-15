# Browser-Use MCP Server

A Model Context Protocol (MCP) server that provides browser automation capabilities using [browser-use](https://github.com/browser-use/browser-use) with console debugging tools.

## Features

- 🌐 Browser automation through MCP
- 🛠️ Console debugging capabilities for web applications
- ⚡ Parallel task execution support
- 🔒 Isolated browser sessions
- 📊 Real-time console log viewing

## Installation

### Prerequisites

First, install Chromium browser (required by browser-use):

```bash
playwright install chromium --with-deps --no-shell
```

### Using uvx (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure with Claude (选择一个 API key)
claude mcp add browser-use \
  --env OPENAI_API_KEY=your-api-key-here \
  -- uvx browser-use-mcp-console

# 或使用 OpenRouter
claude mcp add browser-use \
  --env OPENROUTER_API_KEY=your-api-key-here \
  -- uvx browser-use-mcp-console

# 或使用 Anthropic
claude mcp add browser-use \
  --env ANTHROPIC_API_KEY=your-api-key-here \
  -- uvx browser-use-mcp-console
```

### Using pip

```bash
pip install browser-use-mcp-console

# Configure with Claude (选择一个 API key)
claude mcp add browser-use \
  --env OPENAI_API_KEY=your-api-key-here \
  -- browser-use-mcp-console
```

### 获取 API Key

选择其中一个提供商：
- [OpenAI](https://platform.openai.com/api-keys) - 获取 OPENAI_API_KEY
- [Anthropic](https://console.anthropic.com/account/keys) - 获取 ANTHROPIC_API_KEY  
- [OpenRouter](https://openrouter.ai) - 获取 OPENROUTER_API_KEY（支持多种模型）

## Usage

Once configured, the MCP server provides the `run_browser_tasks` tool that can:

- Execute single or multiple browser automation tasks
- Run tasks in parallel for better performance
- Enable console debugging for web application development

### Example

```
Run browser automation task:
- Task: "Go to example.com and take a screenshot"
- Model: google/gemini-2.5-pro
- Headless: false
- Enable console: true
```

## Configuration

The server supports the following parameters:

- `tasks`: List of tasks to execute
- `model`: LLM model to use (default varies by provider:
  - OpenAI: "gpt-4o-mini"
  - Anthropic: "claude-3-5-sonnet-20241022"
  - OpenRouter: "google/gemini-2.5-pro")
- `headless`: Whether to run browsers in headless mode (default: false)
- `max_steps`: Maximum steps per task (default: 100)
- `enable_console`: Enable console viewing capabilities (default: false)

## Requirements

- Python 3.11+
- browser-use >= 0.5.6

## Development

To contribute or modify:

```bash
# Clone the repository
git clone https://github.com/yourusername/browser-use-mcp-console
cd browser-use-mcp-console

# Install in development mode
pip install -e .
```

## License

MIT License