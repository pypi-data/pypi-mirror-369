
from loguru import logger

from rich.console import Console
from rich.text import Text
import sys


class CustomLogger:
    """Custom logger using Rich Console for clean, formatted output"""
    
    def __init__(self):
        self.console = Console()
        self._enabled = True
    
    def info(self, message: str,rich=None, **kwargs):
        """Log info message with rich formatting"""
        if message=="":
            message=rich
        else:
            message=message
        if self._enabled:
            self.console.print(message, **kwargs)
        else:
            print(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with rich formatting"""
        if self._enabled:
            self.console.print(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with rich formatting"""
        if self._enabled:
            self.console.print(f"[red]{message}[/red]", **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message with rich formatting"""
        if self._enabled:
            self.console.print(f"[green]{message}[/green]", **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with rich formatting"""
        if self._enabled:
            self.console.print(f"[dim]{message}[/dim]", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with rich formatting"""
        if self._enabled:
            self.console.print(f"[bold red]{message}[/bold red]", **kwargs)
    
    def disable(self, module_name: str = None):
        """Disable logging (compatibility with loguru)"""
        if module_name:
            # For specific module disabling, we could implement more sophisticated logic
            pass
        else:
            self._enabled = False
    
    def enable(self):
        """Enable logging"""
        self._enabled = True
    
    def configure(self, **kwargs):
        """Configure logger (compatibility with loguru)"""
        # This is for compatibility - we use Rich Console directly
        pass
    
    def remove(self, handler_id=None):
        """Remove handler (compatibility with loguru)"""
        # This is for compatibility - we use Rich Console directly
        pass
    
    def add(self, sink, **kwargs):
        """Add handler (compatibility with loguru)"""
        # This is for compatibility - we use Rich Console directly
        pass


# Create the logger instance
logger = CustomLogger()

#from loguru import logger

__all__ = ["logger"]