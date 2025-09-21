"""Test Python file for AB Code Reviewer."""

import os
from typing import List


def hello_world(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def process_items(items: List[str]) -> List[str]:
    """Process a list of items."""
    return [item.upper() for item in items if item]


if __name__ == "__main__":
    print(hello_world())
    print(process_items(["hello", "world"]))
