# mcp-run-python-code
Python interpreter, MCP server, no API key, free. Get results from running Python code.

## Overview

This MCP server provides tools for running Python code, installing packages, and executing Python files. 
It can be easily integrated with MCP clients, including Claude and other LLM applications supporting the MCP protocol.

## Features

- Execute Python code in a safe environment
- Install Python packages using pip
- Save Python code to files and run them
- Run existing Python files
- Return specific variable values from executed code
- Error handling and debugging support

## Installation

### From pip
You can install the MCP Run Python Code Server using `uv`:

```bash
uv pip install mcp-run-python-code
```

Or using pip:

```bash
pip install mcp-run-python-code
```

### From source
```bash
git clone https://github.com/shibing624/mcp-run-python-code.git
cd mcp-run-python-code
pip install -e .
```

## Usage
### Python Demo
```python
from run_python_code import RunPythonCode

tool = RunPythonCode(base_dir='/tmp/tmp_run_code/')

# 示例1：基本代码执行
result = tool.run_python_code("x = 10\ny = 20\nz = x * y", "z")
print(f"结果: {result}")  # 输出: 结果: 200

# 示例2：保存并运行文件
result = tool.save_to_file_and_run(
    file_name="calc.py",
    code="a = 5\nb = 15\nc = a + b",
    variable_to_return="c"
)
print(f"结果: {result}")  # 输出: 结果: 20

# 实例3：安装python包
result = tool.pip_install_package("requests")
print(f"结果: {result}")
```

![](https://github.com/shibing624/mcp-run-python-code/blob/main/docs/calc_demo.png)

### Running as a standalone MCP server

Run the server with the stdio transport:

```bash
uvx mcp-run-python-code
```

or

```bash
uv run mcp-run-python-code
```

or 

```bash
python -m mcp-run-python-code
```

Then, you can use the server with any MCP client that supports stdio transport.

### Integrating with Cursor

To add the weather MCP server to Cursor, add stdio MCP with command:

```bash
uvx mcp-run-python-code
```

### Tools available

- `run_python_code` - Execute Python code and optionally return a variable value
- `save_to_file_and_run` - Save Python code to a file and execute it
- `pip_install_package` - Install Python packages using pip
- `run_python_file` - Run an existing Python file and optionally return a variable value

## Examples

#### Example 1: Basic Code Execution
```python
from run_python_code import RunPythonCode
tool = RunPythonCode(base_dir='/tmp/tmp_run_code/')
# Execute simple calculations
code = "result = 2 ** 10"
value = tool.run_python_code(code, "result")
print(value)  # Output: 1024
```

#### Example 2: Run python File
```python
from run_python_code import RunPythonCode
tool = RunPythonCode(base_dir='/tmp/tmp_run_code/')
# Save code to a file and run it
script_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
"""
result = tool.save_to_file_and_run("fib.py", script_code, "result")
print(result)  # Output: 55
```

#### Example 3: Data Processing
```python
from run_python_code import RunPythonCode
tool = RunPythonCode(base_dir='/tmp/tmp_run_code/')
# JSON data processing
code = """
import json
data = {'name': '张三', 'age': 30}
json_str = json.dumps(data, ensure_ascii=False)
"""
result = tool.run_python_code(code, "json_str")
print(result)  # Output: {"name": "张三", "age": 30}
```


## Contact

- Issues and suggestions: [![GitHub issues](https://img.shields.io/github/issues/shibing624/mcp-run-python-code.svg)](https://github.com/shibing624/mcp-run-python-code/issues)
- Email: xuming624@qq.com
- WeChat: Add me (WeChat ID: xuming624) with the message: "Name-Company-NLP" to join our NLP discussion group.

<img src="https://github.com/shibing624/weather-forecast-server/blob/main/docs/wechat.jpeg" width="200" />


## License

This project is licensed under [The Apache License 2.0](/LICENSE) and can be used freely for commercial purposes. 
Please include a link to the `mcp-run-python-code` project and the license in your product description.
## Contribute

We welcome contributions to improve this project! Before submitting a pull request, please:

1. Add appropriate unit tests in the `tests` directory
2. Run `python -m pytest` to ensure all tests pass
3. Submit your PR with clear descriptions of the changes

## Acknowledgements

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 