from core.module.module import Module


def get_example_fibonacci_args() -> Module:
    name = "calculate_fibonacci"
    description = "calculate fibonacci"
    code = """
def fibonacci(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b

    return b
print(fibonacci(n))
        """
    tags = ["fibonacci", "math"]
    args = {
        "n": {
            "type": "int",
            "description": "the number of fibonacci"
        }
    }

    return Module(name=name, description=description, code=code, args=args, tags=tags)


example_fibonacci_args = get_example_fibonacci_args()
