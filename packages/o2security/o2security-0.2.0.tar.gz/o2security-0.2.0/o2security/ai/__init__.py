"""
O₂Security AI Module
====================

This module provides a secure client for interacting with Large Language Models (LLMs).

It leverages the O₂Security core to securely manage API keys and other configurations.
Conversation history is encrypted and stored locally in a SQLite database.

Usage:
    >>> from o2security.ai import O2AI
    >>>
    >>> # Initialize the client for your specific project
    >>> ai_client = O2AI(project_name='my-chatbot')
    >>>
    >>> # Set a system prompt if needed
    >>> ai_client.set_system_prompt("You are a pirate chatbot who says 'Arrr!' a lot.")
    >>>
    >>> # Chat with the model
    >>> response = ai_client.chat("What is the treasure of the seven seas?")
    >>> print(response)
    Arrr! The treasure be the friends we make along the way, matey! Arrr!

"""

# This makes the O2AI class directly accessible from the 'o2security.ai' package.
from .client import O2AI

# You can also define what gets imported when a user does 'from o2security.ai import *'
__all__ = ['O2AI']
