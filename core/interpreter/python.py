from langchain.utilities.python import PythonREPL
from .base import BaseInterpreter


class PythonInterpreter(BaseInterpreter):
    name = "python"
    description = "Executes python code on the user's machine and returns the output"

    def __init__(self):
        self.namespace = {}

    def run(self, code: str, **kwargs):
        # merge namespace with kwargs
        self.namespace.update(kwargs)
        return PythonREPL(_globals=self.namespace, _locals=None).run(code)

    def setup(self, code: str):
        self.run(code)
