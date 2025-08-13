"""
VAIL Model Registry package initialization.
"""

from vail.cli import main as cli_main
from vail.registry import interactive_browse

__all__ = [
    "cli_main",
    "interactive_browse",
]
