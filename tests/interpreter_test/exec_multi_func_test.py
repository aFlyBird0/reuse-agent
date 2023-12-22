import sys
from io import StringIO

from langchain_experimental.utilities import PythonREPL
from core.interpreter.python import PythonInterpreter

f1 = """
def fibonacci(n): 
    if n <= 0: 
        return 0 
    elif n == 1: 
        return 1 
    else: 
        return fibonacci(n-1) + fibonacci(n-2) 

import math 

def calculate_fibonacci_and_add_sqrt(fibonacci_index, sqrt_number, round_decimal):
    fib_n = fibonacci(fibonacci_index) 
    result = fib_n + math.sqrt(sqrt_number) 
    return round(result, round_decimal)

# 所有对形参的赋值语句都应该被忽略，假设所有实参已经被正确赋值。
# fibonacci_index = 10
# sqrt_number = 6
# round_decimal = 2
print(calculate_fibonacci_and_add_sqrt(fibonacci_index, sqrt_number, round_decimal))
"""

args1 = {
    "fibonacci_index": 10,
    "sqrt_number": 6,
    "round_decimal": 2,
}

f2 = """
import math

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n+1):
            a, b = b, a + b
        return b

def calculate_result(fib_index, sqrt_number, decimal_places):
    fib_n = fibonacci(fib_index)
    sqrt_num = math.sqrt(sqrt_number)
    result = round(fib_n + sqrt_num, decimal_places)
    return result

# 所有对形参的赋值语句都应该被忽略，假设所有实参已经被正确赋值。
# fib_index = 10
# sqrt_number = 6
# decimal_places = 2
print(calculate_result(fib_index, sqrt_number, decimal_places))
"""

args2 = {
    "fib_index": 10,
    "sqrt_number": 6,
    "decimal_places": 2,
}

f3 = """
import math

def calculate_fibonacci_and_add_sqrt(n, number):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return round(b + math.sqrt(number), 2)

# 实参初始化/赋值语句应该被忽略，假设所有实参已经被正确赋值。
# result = round(fibonacci(10) + math.sqrt(6), 2)
result = calculate_fibonacci_and_add_sqrt(10, 6)
print(result)
"""

args3 = {
    "n": 10,
    "number": 6,
}

f4 = """
import math

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def calculate_fibonacci_and_add(n, number_to_add):
    fib_num = fibonacci(n)
    result = fib_num + number_to_add
    return result
    
# 实参初始化/赋值语句应该被忽略，假设所有实参已经被正确赋值。
print(calculate_fibonacci_and_add(n, math.sqrt(num_to_add)))
"""

args4 = {
    "n": 10,
    "num_to_add": 6,
}

if __name__ == '__main__':

    f, args = f4, args4
    # try:
    #     exec(f, args)
    # except Exception as e:
    #     print(e)

    # print(PythonREPL(_globals=args, _locals=args).run(f))

    # from core.action_to_module.toolgen import my_exec

    # print(my_exec(code=f, args=args))
    # print(exec(f, args))

    def my_exec2(code, kwargs):
        return PythonREPL(_globals=kwargs, _locals=None).run(code)

    # print(my_exec2(code=f, kwargs=args))

    print(PythonInterpreter().run(f, **args))

    # f, args = f4, args4
    # print(my_exec2(code=f, kwargs=args))