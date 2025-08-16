"""External Toolsets Support

This module provides the infrastructure for external toolsets that can be
dynamically loaded into Pantheon without modifying the core system.

Architecture:
- base.py: ExternalToolSet base class and @tool decorator  
- loader.py: Dynamic loading system for external toolsets
- README.md: Complete usage documentation and design patterns

External toolsets are stored in the ext_toolsets/ directory and follow
the universal bio toolset design patterns.
"""

from .base import ExternalToolSet, tool
from .loader import ExternalToolsetLoader

__all__ = ['ExternalToolSet', 'tool', 'ExternalToolsetLoader']
__version__ = "2.0.0"
__author__ = "Pantheon External Tools Team"