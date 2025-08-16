import asyncio
from ..shell._shell import AsyncCommandLineInterpreter


class AsyncJuliaInterpreter(AsyncCommandLineInterpreter):
    """Julia interpreter toolset.
    For running Julia code in an interpreter.

    Args:
        julia_executable: The path to the Julia executable.
        julia_args: The arguments to pass to the Julia executable.
        marker: The marker to use to detect the end of the command.
    """

    def __init__(
            self,
            julia_executable: str = "julia",
            julia_args: list[str] | None = None,
            marker: str = "__COMMAND_FINISHED__",
            ):
        super().__init__(
            executable=julia_executable,
            args=julia_args or [],
            marker=marker,
        )
    
    async def start(self) -> str:
        """Starts the Julia interpreter process.
        
        Julia doesn't output any initial banner or prompt when started,
        so we override the parent's start method to handle this.
        
        Returns:
            A string indicating Julia has started (empty for Julia).
        """
        self.process = await asyncio.create_subprocess_exec(
            self.executable, *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=self.env,
        )
        # Julia doesn't produce initial output, so just return empty string
        await asyncio.sleep(0.2)  # Give Julia a moment to fully start
        return ""

    async def run_command(self, command, timeout=10):
        """
        Send a command to the Julia interpreter and wait until the unique marker is detected.

        The marker is injected via a `println` command and then filtered out from the output.
        Handles both single-line and multi-line Julia code.

        Parameters:
            command (str): The Julia command to execute (can be single or multiline).
            timeout (int, optional): Maximum time in seconds to wait for the marker.

        Returns:
            tuple: (output, finished) where output is the command output and finished indicates if marker was found.
        """
        if self.process.returncode is not None:
            raise Exception("Julia interpreter process has terminated.")
        
        # Ensure command ends with newline
        if not command.endswith('\n'):
            command = command + '\n'
        
        # Send the command as-is
        # Julia handles multiline code naturally
        self.process.stdin.write(command.encode('utf-8'))
        await self.process.stdin.drain()
        
        # Send marker after command completes
        self.process.stdin.write(f'println("{self.marker}")\n'.encode('utf-8'))
        await self.process.stdin.drain()
        
        return await self.read_until_marker(timeout=timeout)

    async def close(self):
        """
        Gracefully close the Julia interpreter.
        """
        if self.process.returncode is None:
            # Send Julia's quit command.
            self.process.stdin.write(b"exit()\n")
            await self.process.stdin.drain()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()

    def stop_on_line(self, line: str, marker: str):
        if (marker in line) and (not line.startswith("julia> ")):
            return True
        return False

    def filter_out_line(self, line: str, marker: str):
        return False

# Example usage demonstrating both single-line and multi-line commands
async def main():
    j = AsyncJuliaInterpreter(julia_executable="julia")
    await j.start()
    print("Julia interpreter started")
    
    try:
        # Single-line command
        print("\n1. Simple calculation:")
        output, _ = await j.run_command("2 + 3", timeout=10)
        print(f"   Result: {output.strip()}")
        
        # Multi-line function definition
        print("\n2. Multi-line function:")
        code = """function fibonacci(n)
    if n <= 1
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
fibonacci(10)"""
        output, _ = await j.run_command(code, timeout=10)
        print(f"   Result: {output.strip()}")
        
        # For loop
        print("\n3. For loop:")
        code = """for i in 1:3
    println("Number: $i")
end"""
        output, _ = await j.run_command(code, timeout=10)
        print(f"   Result:\n{output}")
        
    finally:
        await j.close()
        print("Julia interpreter closed")


if __name__ == "__main__":
    asyncio.run(main())