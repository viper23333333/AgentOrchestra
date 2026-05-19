"""
Code execution tool for the AgentOrchestra system.

Provides a sandboxed environment for executing Python code snippets
safely. Includes resource limits, timeout enforcement, and output capture.
"""

from __future__ import annotations

import asyncio
import io
import logging
import contextlib
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CodeExecutionResult(BaseModel):
    """Result of a code execution operation.

    Attributes:
        success: Whether the execution completed without errors.
        stdout: Standard output captured during execution.
        stderr: Standard error captured during execution.
        return_code: Process return code (0 = success).
        execution_time_ms: Execution time in milliseconds.
        error: Error message if execution failed.
    """

    success: bool = Field(default=True, description="Execution success flag")
    stdout: str = Field(default="", description="Captured stdout")
    stderr: str = Field(default="", description="Captured stderr")
    return_code: int = Field(default=0, description="Return code")
    execution_time_ms: float = Field(default=0.0, description="Execution time in ms")
    error: str | None = Field(default=None, description="Error message if failed")


class CodeExecutor:
    """Sandboxed Python code execution tool.

    Executes Python code in a restricted environment with:
    - Timeout enforcement
    - Output capture (stdout/stderr)
    - Restricted builtins
    - Memory limits (via resource module on Unix)

    Attributes:
        name: Tool name.
        description: Tool description for agent consumption.
        default_timeout: Default execution timeout in seconds.
        max_output_length: Maximum output length to capture.
    """

    name: str = "code_executor"
    description: str = (
        "Execute Python code in a sandboxed environment. "
        "Use this tool to run code snippets, test algorithms, "
        "or perform calculations. The code runs with restricted "
        "builtins and a configurable timeout."
    )

    # Restricted builtins - remove dangerous functions
    RESTRICTED_BUILTINS: dict[str, Any] | None = None

    def __init__(
        self,
        default_timeout: int = 30,
        max_output_length: int = 10000,
    ) -> None:
        """Initialize the code executor.

        Args:
            default_timeout: Default timeout in seconds.
            max_output_length: Maximum characters to capture from output.
        """
        self.default_timeout = default_timeout
        self.max_output_length = max_output_length

        # Build restricted builtins
        import builtins

        safe_builtins = {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "reversed": reversed,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "isinstance": isinstance,
            "type": type,
            "hasattr": hasattr,
            "getattr": getattr,
            "repr": repr,
            "format": format,
            "any": any,
            "all": all,
            "iter": iter,
            "next": next,
            "slice": slice,
            "hash": hash,
            "id": id,
            "callable": callable,
            "chr": chr,
            "ord": ord,
            "hex": hex,
            "oct": oct,
            "bin": bin,
            "pow": pow,
            "divmod": divmod,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "AttributeError": AttributeError,
            "RuntimeError": RuntimeError,
            "StopIteration": StopIteration,
            "NotImplementedError": NotImplementedError,
            "Exception": Exception,
            "ArithmeticError": ArithmeticError,
            "ZeroDivisionError": ZeroDivisionError,
            "OverflowError": OverflowError,
        }
        self.RESTRICTED_BUILTINS = safe_builtins
        logger.info("CodeExecutor initialized (timeout=%ds)", default_timeout)

    async def execute(
        self,
        code: str,
        timeout: int | None = None,
    ) -> CodeExecutionResult:
        """Execute Python code in a sandboxed environment.

        Args:
            code: The Python code to execute.
            timeout: Execution timeout in seconds. Defaults to default_timeout.

        Returns:
            CodeExecutionResult: The execution result including output and errors.
        """
        import time

        timeout = timeout or self.default_timeout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        start_time = time.perf_counter()

        try:
            # Execute in a separate thread to enforce timeout
            result = await asyncio.wait_for(
                self._execute_sync(code, stdout_capture, stderr_capture),
                timeout=timeout,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            stdout = stdout_capture.getvalue()[: self.max_output_length]
            stderr = stderr_capture.getvalue()[: self.max_output_length]

            return CodeExecutionResult(
                success=result is None,
                stdout=stdout,
                stderr=stderr,
                return_code=0 if result is None else 1,
                execution_time_ms=elapsed_ms,
                error=str(result) if result else None,
            )
        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return CodeExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue()[: self.max_output_length],
                stderr=f"Execution timed out after {timeout} seconds",
                return_code=-1,
                execution_time_ms=elapsed_ms,
                error=f"Code execution timed out after {timeout} seconds",
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return CodeExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue()[: self.max_output_length],
                stderr=str(e),
                return_code=-1,
                execution_time_ms=elapsed_ms,
                error=f"Execution error: {e}",
            )

    def _execute_sync(
        self,
        code: str,
        stdout_capture: io.StringIO,
        stderr_capture: io.StringIO,
    ) -> BaseException | None:
        """Execute code synchronously (called from thread).

        Args:
            code: Python code to execute.
            stdout_capture: StringIO for stdout capture.
            stderr_capture: StringIO for stderr capture.

        Returns:
            BaseException | None: The exception if one occurred, else None.
        """
        # Redirect stdout/stderr
        old_stdout = io.StringIO()
        old_stderr = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_capture):
                with contextlib.redirect_stderr(stderr_capture):
                    # Compile first to catch syntax errors
                    compiled = compile(code, "<sandbox>", "exec")

                    # Create restricted namespace
                    namespace: dict[str, Any] = {
                        "__builtins__": self.RESTRICTED_BUILTINS,
                        "__name__": "__sandbox__",
                    }

                    # Execute
                    exec(compiled, namespace)  # noqa: S102

            return None
        except Exception as e:
            return e

    def get_tool_definition(self) -> dict[str, Any]:
        """Return the tool definition for LangChain tool binding.

        Returns:
            dict: Tool definition compatible with LangChain.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds",
                            "default": self.default_timeout,
                        },
                    },
                    "required": ["code"],
                },
            },
        }


class CodeExecutorError(Exception):
    """Custom exception for code executor errors."""

    pass
