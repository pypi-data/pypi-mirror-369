"""
Base gridworld environment package.

This subpackage defines the core GridWorld environment along with its corresponding renderer. 
Separating the environment logic from the renderer allows the core environment code to remain free of
any Pygame dependencies.
"""

from .env import *
