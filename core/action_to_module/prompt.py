SYSTEM_PROMPT_CN_TEMPLATE = """
您将获得一个Python代码片段。您的任务是重构代码，使其更加通用，将函数内部的硬编码变量转换为函数参数。此外，您应该为函数提供简洁的英文名称，创建详细的函数描述，并详细指定函数参数的名称和类型。

将提供的当前任务日志和原始主任务视为您的参考。其中，前者是AI助手在编写Python代码时的思考过程，后者更像是AI助手的最终目标，但和您的任务关系不大，仅作为背景信息。

-------您的任务：----------

重构给定的Python代码以实现更好的通用性，代码应该是由若干个Python函数定义，加上若干个函数调用，最后print()函数输出的结果。
为重构后的代码提供简洁的英文名称。
撰写全面的代码描述。
详细指定运行这整段代码时，传入的参数名称和类型。（如果函数形参与传入的形参名称不同，以实际传入的形参名称为准。）

------附加信息：----------
1. 你应该尽可能关注当前任务日志，以保证重构的代码更加通用。如有必要，可以参考原始主任务。
2. 你重构后的代码，应该是由若干个Python函数定义，加上若干个函数调用，最后print()函数输出的结果。
3. 在调用函数输出结果时，请不传入实际参数，而是使用形式参数名进行调用。请注意忽略任何在代码中对形参进行赋值的语句，假设所有实参已经被正确赋值。此外，请确保形式参数的数据类型与您在函数定义中指定的类型相匹配。
4. 如果函数形参和调用时的实参名不一致，你可以将其修改为一致的名称。
5. 注意函数的顺序，确保函数在调用之前已经定义；并且不要定义递归函数，也不要在函数内部定义函数。
------示例：-------------

Python Code:
```python
{example_origin_code}
```

当前任务日志(撰写Python代码思考过程): {example_task_log}

原始主任务: {example_origin_main_task}

你应该返回一个完整的Json和重构后的代码块，不要有其他任何多余的东西(比如解释）

其中Json包含以下字段：
* name: 函数名称
* description: 函数描述
* args: 函数参数列表，其中包含参数名称和类型
* tags: 若干个标签，用于描述函数的功能/用途/特性/分类等等
* dependencies: 需要安装的python包，如果为空，则显示为一个空列表[]
后面空一行，然后是重构后的Python代码块。

完整回复例子如下：

```json
{example_args_extracted_json}
```

```python
{example_refactored_code}
```

------附加信息：----------
{example_additional_info}
"""

USER_PROMPT_CN_TEMPLATE = """
Python Code:
```python
{code}
```

当前任务日志(撰写Python代码思考过程): {task_log}

原始主任务: {origin_main_task}
"""