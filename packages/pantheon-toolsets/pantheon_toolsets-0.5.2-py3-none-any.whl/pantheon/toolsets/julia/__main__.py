from .julia_interpreter import JuliaInterpreterToolSet
from ..utils.toolset import toolset_cli


toolset_cli(JuliaInterpreterToolSet, "julia-interpreter")