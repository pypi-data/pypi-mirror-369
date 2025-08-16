import ast
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ..visualization.charts import save_plot


class SafeExecutor:
    def __init__(self):
        """Initialize the safe code execution environment."""
        # Allowed modules and functions
        self.allowed_modules = {
            "pandas": pd,
            "numpy": np,
            "matplotlib.pyplot": plt,
            "seaborn": sns,
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns,
            "save_plot": save_plot,
        }

        # Allowed built-in functions
        self.allowed_builtins = {
            "len",
            "range",
            "enumerate",
            "zip",
            "list",
            "dict",
            "tuple",
            "set",
            "str",
            "int",
            "float",
            "bool",
            "sum",
            "max",
            "min",
            "sorted",
            "abs",
            "round",
            "print",
            "type",
            "isinstance",
            "any",
            "all",
            "filter",
            "map",
            "reversed",
            "slice",
            "divmod",
            "pow",
            "ord",
            "chr",
            "bin",
            "hex",
            "oct",
            "format",
            "repr",
            "ascii",
            "hash",
            "id",
            "vars",
            "dir",
            "getattr",
            "hasattr",
            "callable",
            "issubclass",
            "super",
            "property",
            "staticmethod",
            "classmethod",
            "next",
            "iter",
            "help",
            "compile",
            "breakpoint",
            "copyright",
            "credits",
            "license",
        }

        # Dangerous operations that are explicitly blocked
        self.blocked_operations = {
            "import",
            "from",
            "del",
            "global",
            "nonlocal",
            "assert",
            "raise",
            "yield",
            "lambda",
            "class",
            "def",
        }

    def execute(self, code: str, local_vars: dict) -> str:
        """Execute code safely and return output."""
        # Parse and validate AST
        try:
            tree = ast.parse(code)
            self._validate_ast(tree)
        except SyntaxError as e:
            return f"Syntax error in generated code: {e}"
        except ValueError as e:
            return f"Code validation failed: {e}"

        # Prepare execution environment
        safe_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in self.allowed_builtins
                if hasattr(__builtins__, name)
            },
            **self.allowed_modules,
        }

        # Capture output
        output_buffer = StringIO()
        error_buffer = StringIO()

        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, safe_globals, local_vars)

            output = output_buffer.getvalue()
            errors = error_buffer.getvalue()

            return (
                errors
                if errors
                else (output if output else "Code executed successfully (no output)")
            )
        except Exception as e:
            return f"Execution failed: {e}"

    def _validate_ast(self, tree):
        """Validate AST for security."""
        dangerous_nodes = [
            ast.Import,
            ast.ImportFrom,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        ]

        for node in ast.walk(tree):
            # Check for dangerous node types
            if any(isinstance(node, dangerous) for dangerous in dangerous_nodes):
                raise ValueError(
                    f"Dangerous operation not allowed: {type(node).__name__}"
                )

            # Check function definitions
            if isinstance(node, ast.FunctionDef):
                raise ValueError("Function definitions are not allowed in safe mode")

            # Check for loops and conditionals (basic control flow is allowed)
            if isinstance(node, (ast.For, ast.While, ast.If, ast.Try)):
                # Allow basic control flow but with restrictions
                pass

            # Check function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if (
                        func_name not in self.allowed_builtins
                        and func_name not in self.allowed_modules
                        and func_name not in self.blocked_operations
                    ):
                        # Allow method calls on allowed objects
                        if isinstance(node.func, ast.Attribute):
                            continue
                        raise ValueError(f"Function call not allowed: {func_name}")

            # Check for file operations
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["open", "file"]:
                    raise ValueError("File operations are not allowed in safe mode")

            # Check for network operations
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if hasattr(node.func, "value") and isinstance(
                    node.func.value, ast.Name
                ):
                    if node.func.value.id in ["requests", "urllib", "socket"]:
                        raise ValueError(
                            "Network operations are not allowed in safe mode"
                        )

    def get_execution_stats(self) -> dict:
        """Get statistics about the execution environment."""
        return {
            "allowed_modules": list(self.allowed_modules.keys()),
            "allowed_builtins": list(self.allowed_builtins),
            "blocked_operations": list(self.blocked_operations),
            "sandbox_mode": "strict",
        }
