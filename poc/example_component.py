from action_to_model_agent.agent import PythonREPLArgs

example_fabinacci_sqrt_component_args: PythonREPLArgs = PythonREPLArgs(
    name="calculate_fibonacci_and_add_sqrt",
    description="This function calculates the nth Fibonacci number, adds the square root of a given number to it, and rounds the result to a specified number of decimal places.",
    args={'fibonacci_index': 'int', 'sqrt_number': 'int', 'decimal_places': 'int'},
    code="""
def calculate_fibonacci_and_add_sqrt(fibonacci_index, sqrt_number, decimal_places):
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

    fib_n = fibonacci(fibonacci_index)
    result = fib_n + sqrt_number**0.5
    return round(result, decimal_places)

# 所有对形参的赋值语句都应该被忽略，假设所有实参已经被正确赋值。
# fibonacci_index = 10
# sqrt_number = 6
# decimal_places = 2
print(calculate_fibonacci_and_add_sqrt(fibonacci_index, sqrt_number, decimal_places))
"""
)