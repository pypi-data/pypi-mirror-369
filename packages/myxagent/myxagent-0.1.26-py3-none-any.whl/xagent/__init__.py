"""
xAgent - Multi-Modal AI Agent System

A powerful multi-modal AI Agent system with modern architecture.
"""

from .core import Session, Agent
from .interfaces import HTTPAgentServer, CLIAgent
from .schemas import Message
from .db import MessageStorageBase, MessageStorageRedis, MessageStorageLocal
from .utils import function_tool
from .tools import web_search, draw_image
from .multi import Swarm, Workflow
from .__version__ import __version__

__all__ = [
    # Core components
    "Session",
    "Agent", 

    # interfaces
    "HTTPAgentServer",
    "CLIAgent",
    
    # Data models
    "Message",

    # Database
    "MessageStorageBase",
    "MessageStorageRedis",
    "MessageStorageLocal",
    
    # Utilities
    "function_tool",

    # Built-in tools
    "web_search",
    "draw_image",

    # Multi-agent
    "Swarm",
    "Workflow",
    
    # Meta
    "__version__"
]
