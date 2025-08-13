"""Main module for cursor_credits."""

# Re-export the main functions from cli for backward compatibility
from .cli import run_check, main

__all__ = ["run_check", "main"]
