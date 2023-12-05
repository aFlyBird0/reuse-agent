import sys
from io import StringIO

from langchain_experimental.utilities import PythonREPL

f = """
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

if __name__ == '__main__':
    args = {
        "fibonacci_index": 10,
        "sqrt_number": 6,
        "round_decimal": 2,
    }
    # exec(f, args)

    args2 = {
        "fib_index": 10,
        "sqrt_number": 6,
        "decimal_places": 2,
    }
    try:
        exec(f2, args2)
    except Exception as e:
        print(e)
    # print(PythonREPL(_globals=globals(), _locals=args2).run(f2))

    from cot_component import my_exec

    # print(my_exec(globals=args2, locals=args2, code=f2))