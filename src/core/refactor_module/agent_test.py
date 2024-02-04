import json
import logging
from typing import List

from langchain_core.messages import HumanMessage
from pydantic.json import pydantic_encoder

from core.action_to_module.prompt import USER_PROMPT_CN_TEMPLATE
from core.module.module_store import default_module_store
from core.refactor_module.agent import create_refactor_agent, refactor_or_combine
from llm.openai import OpenAIConfig


def test_refactor_or_combine(module_names: List[str], request: str):
    store = default_module_store

    modules_in_store = [store.list_by_name(name)[0] for name in module_names]

    for m in modules_in_store:
        print(f"待重构/合并模块名:{m.name}, 描述：{m.description}, 参数：{m.params}")
        print(f"代码：{m.code}")
        print("--------------------------------")

    modules = [m.to_dict() for m in modules_in_store]

    refactored_module = refactor_or_combine(modules=modules, request=request)

    print(f"重构/合并后新模块名:{refactored_module.name}, 描述：{refactored_module.description}, 参数：{refactored_module.params}")
    print(f"代码: {refactored_module.code}")


def test_combine():
    modules = ["list_files", "read_file_content"]
    request = "我希望先列出文件列表，然后读取前n个文件的内容"
    test_refactor_or_combine(module_names=modules, request=request)


def test_refactor():
    modules = ["list_files"]
    request = "我希望能指定，只列出前n个文件"
    test_refactor_or_combine(module_names=modules, request=request)

def test_refactor2():
    modules = ["calculate_fibonacci"]
    request = "我希望能输出从1到n的斐波那契数列"
    test_refactor_or_combine(module_names=modules, request=request)

def test_refactor3():
    modules = ["find_next_prime"]
    request = "我希望能同时找到前一个和后一个素数"
    test_refactor_or_combine(module_names=modules, request=request)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # test_refactor()
    # test_combine()
    # test_refactor2()
    from config import settings
    test_refactor3()