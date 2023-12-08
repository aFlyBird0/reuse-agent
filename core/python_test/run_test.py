import logging
from typing import Any, Union
from pydantic import BaseModel, Field

from loggers.logs import setup_logger
from core.interpreter.python import PythonInterpreter
from core.action_to_module.module_define import PythonModule
from core.python_test.agent import get_python_test_args
from core.python_test.model import TestInput, TestOutput, TestParams

logger = setup_logger()


class PythonTestRunner:
    def __init__(self, test_input: TestInput):
        self.test_input = test_input
        self.test_output = TestOutput(input=test_input, output=None, stdout=None, stderr=None, success=False)
        self.interpreter = PythonInterpreter()

    def run(self):
        install_res = self.interpreter.install_dependencies(self.test_input.dependencies)
        install_stderr = install_res.get("stderr", "")
        if install_stderr != "":
            self.test_output.stderr = install_stderr
            return self.test_output

        # todo: 把 .run() 改造成 json 式的返回
        run_res = self.interpreter.run(self.test_input.code, **self.test_input.args_input).strip()
        self.test_output.stdout = run_res
        if run_res != self.test_input.expected_output:
            return self.test_output
        else:
            self.test_output.success = True
            return self.test_output


def test_exist_module(module: PythonModule) -> TestOutput:
    test_params: TestParams = get_python_test_args(code=module.code, args_schema=module.args)
    test_input = TestInput(
        name=module.name,
        description=module.description,
        code=module.code,
        dependencies=module.dependencies,
        args_schema=module.args,
        args_input=test_params.args,
        expected_output=test_params.stdout
    )
    runner: PythonTestRunner = PythonTestRunner(test_input)
    test_res: TestOutput = runner.run()

    return test_res


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from core.action_to_module.module_define import example_fibonacci

    module = example_fibonacci()

    test_res = test_exist_module(module)

    logger.info(f"test_res.input: {test_res.input}")
    logger.info(f"test_res.stdout: {test_res.stdout}")
    logger.info(f"test_res.stderr: {test_res.stderr}")
    logger.info(f"test_res.success: {test_res.success}")
