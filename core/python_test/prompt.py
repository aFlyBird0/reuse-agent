SYSTEM_PROMPT_CN = """你是一个强大的代码测试员，你拥有在本地运行代码的能力，下面是代码运行工具的使用说明：
{tool_description}

我将给你一份示例代码，并且给你代码的描述和参数要求。请你按照代码参数要求，生成测试参数，并生成预期控制台输出（如果没有控制台没有输出就留空）。

你的回复也应该是一个json代码块，不要有其他多余内容，整体格式如下：

```json
{response_schema_example}
```

"""

USER_PROMPT_CN = """
下面是代码：

```python
{code}
```

下面是代码的描述和参数要求：
```json
{code_args}
```
"""

# example_code = """
# def add(a, b):
#     return a + b
# print(add(a, b))
# """

from core.action_to_module import example
example_code = example.example_refactored_code
example_args_schema_dict = example.example_args_extracted_json
example_response_schema = """
{
    "args": {
        "arg1": "value1",
        "arg2": "value2"
    },
    "stdout": "expected stdout"
}
"""

from core.interpreter.python_tool import PythonTool
def get_tool_description(tool: PythonTool)->str:
    # args_schema = re.sub("}", "}}", re.sub("{", "{{", str(tool.args)))
    args_schema = str(tool.args)
    return (f"Tool Name: {tool.name}\n"
            f"Tool Description:{tool.description}\n"
            # f"Tool Args: {args_schema}\n"
    )

example_tool_description = get_tool_description(PythonTool())