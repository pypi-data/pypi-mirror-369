#!/usr/bin/env python3
"""
Entry point for running cmdlm.cli as a module.

This allows commands like:
    python -m cmdlm.cli
    python -m cmdlm.cli chat --tools all
"""

from .main import cli

if __name__ == "__main__":
    cli()
