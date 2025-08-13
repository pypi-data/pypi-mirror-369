"""
Bolt Agent Toolkit

Standalone Python toolkit integration for Bolt APIs
"""

from .api import BoltAPI
from .configuration import Configuration, Context, is_tool_allowed
from .tools import tools

__version__ = "0.1.0"
__author__ = "Bolt Financial Inc."
