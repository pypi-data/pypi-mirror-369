import uuid
import os
import base64

from ._julia import AsyncJuliaInterpreter
from ..utils.toolset import ToolSet, tool
from ..utils.log import logger


class JuliaInterpreterToolSet(ToolSet):
    """Julia interpreter toolset.
    For running Julia code in an interpreter.

    Args:
        julia_executable: The path to the Julia executable.
        julia_args: The arguments to pass to the Julia executable.
        init_code: The code to run to initialize the Julia environment.
        workdir: The working directory to use for the Julia interpreter.
    """
    def __init__(
            self,
            name: str,
            worker_params: dict | None = None,
            julia_executable: str = "julia",
            julia_args: list[str] | None = None,
            init_code: str | None = None,
            workdir: str | None = None,
            **kwargs,
            ):
        super().__init__(name, worker_params, **kwargs)
        self.interpreters = {}
        self.clientid_to_interpreterid = {}
        self.julia_executable = julia_executable
        self.julia_args = julia_args
        self.init_code = init_code
        self.workdir = workdir

    @tool
    async def run_julia_code(
            self,
            code: str,
            timeout: int = 100,
            context_variables: dict | None = None,
            ):
        """Run Julia code in a new interpreter and return the output with enhanced functionality.
        Automatically handles figures, provides sample data functions, and includes package support.
        If you use this function, don't need to use `new_interpreter` and `delete_interpreter`.

        Args:
            code: The Julia code to run.
            timeout: The timeout for the code to run.
        
        Returns:
            A dictionary with result, stdout, stderr, and optionally figure information.
        """
        # Reset figure path
        reset_code = "GLOBAL_FIG_PATH = nothing"
        
        # Show Julia execution status
        #logger.info("Starting Julia execution...")
        
        initial_output = ""

        if context_variables is None:
            context_variables = {}
        client_id = context_variables.get("client_id")
        if client_id is None:
            client_id = "default"
            logger.warning("No client_id provided, using default")
        p_id = self.clientid_to_interpreterid.get(client_id)
        if (p_id is None) or (p_id not in self.interpreters):
            res = await self.new_interpreter()
            p_id = res["interpreter_id"]
            initial_output = res["initial_output"]
            self.clientid_to_interpreterid[client_id] = p_id

        # Reset figure path and run the actual code
        await self.run_code_in_interpreter(reset_code, p_id, timeout=timeout)
        output = await self.run_code_in_interpreter(code, p_id, timeout=timeout)
        
        # Check for generated figures
        fig_check_output = await self.run_code_in_interpreter("GLOBAL_FIG_PATH", p_id, timeout=10)
        
        # Format result similar to Python toolset
        full_output = output
        if initial_output:
            full_output = initial_output + "\n" + output
            
        result = {
            "result": None,  # Julia doesn't return specific variables like Python
            "stdout": full_output,
            "stderr": "",  # Julia stderr is usually mixed with stdout
            "code_executed": code  # Add the executed code for display
        }
            
        # Handle figure output (Julia uses similar pattern to save figures)
        fig_path_line = None
        for line in fig_check_output.split('\n'):
            # Julia output format might be different, check for path
            if '.png' in line or '.jpg' in line or '.svg' in line:
                # Extract path from Julia output
                line = line.strip()
                if line != "nothing" and line != "Nothing":
                    fig_path_line = line.strip('"')
                    break
                
        if fig_path_line and fig_path_line != "nothing" and os.path.exists(fig_path_line):
            result["fig_storage_path"] = fig_path_line
            logger.info(f"✅ Figure saved: {fig_path_line}")
            try:
                with open(fig_path_line, "rb") as f:
                    base64_img = base64.b64encode(f.read()).decode("utf-8")
                # Determine image type
                if fig_path_line.endswith('.svg'):
                    base64_uri = f"data:image/svg+xml;base64,{base64_img}"
                elif fig_path_line.endswith('.jpg') or fig_path_line.endswith('.jpeg'):
                    base64_uri = f"data:image/jpeg;base64,{base64_img}"
                else:
                    base64_uri = f"data:image/png;base64,{base64_img}"
                result["base64_uri"] = [base64_uri]
                result["hidden_to_model"] = ["base64_uri"]
            except Exception as e:
                logger.warning(f"⚠️ Warning: Failed to read figure file: {e}")
                logger.warning(f"Failed to read figure file {fig_path_line}: {e}")
        
        # Show execution completion
        if "ERROR" in full_output or "Error" in full_output or "error" in full_output.lower():
            logger.error("❌ Julia execution completed with errors")
        else:
            logger.info("")
        
        return result

    @tool
    async def new_interpreter(self) -> dict:
        """Create a new Julia interpreter and return its id and the initial output.
        You can use `run_code_in_interpreter` to run code in the interpreter,
        by providing the interpreter id."""
        # Show Julia interpreter creation status
        logger.info("Creating new Julia interpreter...")
        
        interpreter = AsyncJuliaInterpreter(
            self.julia_executable,
            self.julia_args,
        )
        interpreter.id = str(uuid.uuid4())
        self.interpreters[interpreter.id] = interpreter
        initial_output = await interpreter.start()
        
        # Set working directory if specified
        if self.workdir is not None:
            await self.run_code_in_interpreter(f'cd("{self.workdir}")', interpreter.id)
            
        # Run initialization code
        if self.init_code is not None:
            logger.info("Setting up Julia environment...")
            init_output, _ = await interpreter.run_command(self.init_code, timeout=120)
            initial_output += "\n" + init_output
            logger.info("✅ Julia environment ready")
        
        # Set up figure saving function for Julia (simplified version)
        figure_setup_code = """
# Set up global figure path variable
global GLOBAL_FIG_PATH = nothing

# Helper function to save figures (will only work if Plots is loaded)
function save_figure(filename::String="figure.png")
    global GLOBAL_FIG_PATH
    GLOBAL_FIG_PATH = abspath(filename)
    println("Figure path set to: ", GLOBAL_FIG_PATH)
    return GLOBAL_FIG_PATH
end
"""
        try:
            await interpreter.run_command(figure_setup_code, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to set up figure saving: {e}")

        return {
            "interpreter_id": interpreter.id,
            "initial_output": initial_output,
        }

    @tool
    async def delete_interpreter(self, interpreter_id: str):
        """Delete a Julia interpreter.

        Args:
            interpreter_id: The id of the interpreter to delete.
        """
        interpreter = self.interpreters.get(interpreter_id)
        if interpreter is not None:
            await interpreter.close()
            del self.interpreters[interpreter_id]

    @tool
    async def run_code_in_interpreter(
            self,
            code: str,
            interpreter_id: str,
            timeout: int = 100,
            ) -> str:
        """Run Julia code in an interpreter and return the output.

        Args:
            code: The Julia code to run.
            interpreter_id: The id of the interpreter to run the code in.
            timeout: The timeout for the code to run.
        """
        interpreter = self.interpreters.get(interpreter_id)
        if interpreter is None:
            raise ValueError(f"Interpreter {interpreter_id} not found")
        output, finished = await interpreter.run_command(code, timeout=timeout)
        if not finished:
            output += "\n[Warning] The execution of the command was interrupted because of the timeout. "
            output += "You can try to run get_interpreter_output to get the remaining output of the interpreter."
        return output

    @tool
    async def get_interpreter_output(self, interpreter_id: str, timeout: int = 10) -> str:
        """Get the output of a Julia interpreter. Don't use this function unless you need to get the remaining output of an interrupted command.

        Args:
            interpreter_id: The id of the interpreter to get the output from.
            timeout: The timeout for the output to be returned.
        """
        interpreter = self.interpreters.get(interpreter_id)
        if interpreter is None:
            raise ValueError(f"Interpreter {interpreter_id} not found")
        output, finished = await interpreter.read_until_marker(timeout=timeout)
        if not finished:
            output += "\n[Warning] The execution of the command was interrupted because of the timeout. "
            output += "You can try to run get_interpreter_output to get the remaining output of the interpreter."
        return output

    async def run_setup(self):
        """Setup the toolset before running it."""
        logger.warning(
            "This ToolSet is not secure, it can be used to execute arbitrary code."
            " Please be careful when using it."
            " Highly recommend using it in a controlled environment like a docker container."
        )