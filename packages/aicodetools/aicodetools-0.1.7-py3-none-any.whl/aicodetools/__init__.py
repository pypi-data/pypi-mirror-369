"""
aicodetools: A powerful framework for providing tools to AI agents.

This package provides CodeInstance, a class that wraps deployment environments
(Docker/local) and offers various code tools to AI agents including file operations,
bash sessions, search capabilities, and more.

Usage:
    from aicodetools import CodeInstance
    
    # Create instance with Docker environment
    config = {'docker': {'image': 'python:3.12'}}
    instance = CodeInstance('docker', config, auto_start=True)
    
    # Get tools for your agent
    tools = instance.get_tools(include=['read_file', 'write_file', 'run_command'])
    
    # Use tools with your AI agent
    agent = Agent(tools=tools, ...)
"""

from .instance import CodeInstance

__version__ = "0.1.3"
__author__ = "balajidinesh"

__all__ = ["CodeInstance"]