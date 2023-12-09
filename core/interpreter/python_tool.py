from typing import Any, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import loggers.logs
from .python import PythonInterpreter

logger = loggers.logs.setup_logger()

class PythonInput(BaseModel):
    code: str = Field(description="The code to execute")
    dependencies: list[str] = Field(description="dependencies to install with pip", default=[])


class PythonTool(StructuredTool):
    name: str = "python"
    description: str = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "With this tool you can do anything by writing python code(including operate user's machine). "
        "If the code import packages which is not built-in, please specify the dependencies in tool_input."
        # "If you want to see the output of a value, you should print it out "
        "Never use (!) when running commands."
        "Remember to print out the result or success info"
        "with `print(...)`."
    )
    args_schema: Type[BaseModel] = PythonInput

    def _run(
            self,
            code: str,
            dependencies: list[str],
            run_manager: Optional[CallbackManagerForToolRun] = None,
            **kwargs: Any,
    ) -> Any:
        """Use the tool."""
        logger.info(f"run python code: {code}")
        install_dep_result = PythonInterpreter().install_dependencies(dependencies)
        stderr = install_dep_result.get("stderr", "")
        logger.info(f"install dependencies result: {install_dep_result}")
        if stderr != "":
            return stderr
        logger.info(f"install dependencies success, dependencies: {dependencies}")
        return PythonInterpreter().run(code)
