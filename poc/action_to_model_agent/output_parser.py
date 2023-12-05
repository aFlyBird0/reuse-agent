import json
import logging
import re

# 写一个函数，把输出中的json和python代码提取出来
example_dict = {
    "name": "is_prime",
    "description": "Check if a number is prime.",
    "args": {
        "number": "int"
    }
}

example_json = json.dumps(example_dict, indent=4)
example_python_code = """
def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            return False
    return True

# number_to_check = 100

if is_prime(number_to_check):
    print(f"{number_to_check} is prime")
else:
    print(f"{number_to_check} is not prime")
"""

example = f"""
```json
{example_json}
```
```python
{example_python_code}
```
"""


# def split_json_and_code(text) -> (dict, str):
#     """
#     分隔json和python代码
#     :param text: LLM的输出
#     :return: json, python_code
#     """
#     pattern = r'```python(.*?)```'
#     match = re.search(pattern, text, re.DOTALL)
#     json_part = text.split('```')[0].strip()
#     try:
#         json_data = json.loads(json_part)
#     except json.decoder.JSONDecodeError:
#         logging.error("json decode error")
#         logging.info(f"text: {text}")
#         logging.info(f"json_part: {json_part}")
#         return None, None
#     python_code = match.group(1).strip()
#
#     return json_data, python_code

def split_json_and_code(text) -> (dict, str):
    json_pattern = r'```json(.*?)```'
    python_pattern = r'```python(.*?)```'

    json_match = re.search(json_pattern, text, re.DOTALL)
    python_match = re.search(python_pattern, text, re.DOTALL)

    json_block = json.loads(json_match.group(1).strip()) if json_match else None
    python_block = python_match.group(1).strip() if python_match else None

    return json_block, python_block

if __name__ == "__main__":
    dict_gotten, code_gotten = split_json_and_code(example)
    # print(dict_gotten, "\n", code_gotten)
    assert dict_gotten == example_dict
