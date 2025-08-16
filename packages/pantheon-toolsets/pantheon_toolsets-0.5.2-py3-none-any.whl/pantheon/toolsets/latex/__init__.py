import subprocess

from ..utils.toolset import ToolSet, tool


class LatexToolSet(ToolSet):
    @tool(job_type="thread")
    async def compile_latex(self, tex_file: str) -> str:
        """
        Compile a LaTeX file and return the output.
        """
        try:
            result = subprocess.run(
                ["pdflatex", tex_file],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error compiling LaTeX file: {e}"


__all__ = ["LatexToolSet"]