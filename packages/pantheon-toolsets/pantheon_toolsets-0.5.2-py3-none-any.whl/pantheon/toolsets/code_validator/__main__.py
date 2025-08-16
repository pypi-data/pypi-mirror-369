"""Code Validator ToolSet CLI entry point"""

from ..utils.toolset import toolset_cli
from .core import CodeValidatorToolSet

if __name__ == "__main__":
    toolset_cli(CodeValidatorToolSet, "code_validator")