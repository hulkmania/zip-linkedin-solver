# Queens Game Solver
# Module for solving LinkedIn Queens puzzles with colored regions and modified rules

__version__ = "1.0.0"
__author__ = "AI Assistant"

# Import main components for easy access
from . import board
from . import queen
from . import solver
from . import dom_reader
from . import bot

__all__ = ['board', 'queen', 'solver', 'dom_reader', 'bot']