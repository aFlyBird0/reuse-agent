from typing import Any, Union
from pydantic import BaseModel, Field

class TestParams(BaseModel):
    args: dict[str, Any] = Field(description="arguments input", default_factory=dict)
    stdout: str = Field(description="expected stdout", default="")


class TestInput(BaseModel):
    """
    full args when running a test
    """
    name: str = Field(description="The name of the code")
    description: str = Field(description="The description of the code")
    code: str = Field(description="The code to execute")
    dependencies: list[str] = Field(description="dependencies to install with pip", default_factory=list)
    args_schema: dict[str, str] = Field(description="arguments schema", default_factory=dict)
    args_input: dict[str, Any] = Field(description="arguments input", default_factory=dict)
    expected_output: Any = Field(description="expected output", default=None)


class TestOutput(BaseModel):
    input: TestInput = Field(description="The test input snapshot")
    stdout: Union[str, None] = Field(description="The stdout of the test")
    stderr: Union[str, None] = Field(description="The stderr of the test")
    success: bool = Field(description="Whether the test is success(no error and output is expected)", default=False)
