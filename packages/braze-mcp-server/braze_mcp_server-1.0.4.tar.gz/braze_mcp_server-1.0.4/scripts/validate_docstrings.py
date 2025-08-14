#!/usr/bin/env python3
"""
Pre-commit hook script to validate MCP tool docstrings.

This script validates that all MCP tool functions follow the required
docstring conventions as documented in docs/DOCSTRING_CONVENTIONS.md
"""

import sys
import importlib.util
from pathlib import Path


def load_module_from_path(file_path: str):
    """Dynamically load a Python module from file path."""
    import os
    import sys
    
    # Add src directory to Python path for imports to work
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Use a unique module name based on file path
    module_name = f"validation_module_{hash(file_path) % 1000000}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"⚠️  Could not load module {file_path}: {e}")
        return None


def validate_tool_functions(file_path: str) -> list[str]:
    """Validate all MCP tool functions in a file."""
    try:
        # Import validation function
        from braze_mcp.registry_builder import validate_docstring
    except ImportError:
        print(f"⚠️  Could not import validation function for {file_path}")
        return []
    
    module = load_module_from_path(file_path)
    if not module:
        return [f"Could not load module: {file_path}"]
    
    issues = []
    
    # Check all functions that look like MCP tools
    for name in dir(module):
        obj = getattr(module, name)
        if (callable(obj) and 
            name.startswith('get_') and 
            not name.startswith('_') and
            hasattr(obj, '__module__') and 
            obj.__module__ and 
            'braze_mcp.tools' in obj.__module__):
            is_valid, validation_issues = validate_docstring(obj)
            if not is_valid:
                issues.append(f"❌ {file_path}::{name}")
                for issue in validation_issues:
                    issues.append(f"   - {issue}")
    
    return issues


def main():
    """Main validation logic."""
    all_issues = []
    
    # Process each file passed to the script
    for file_path in sys.argv[1:]:
        if ('braze_mcp/tools/' in file_path and 
            file_path.endswith('.py') and 
            not file_path.endswith('__init__.py')):
            file_issues = validate_tool_functions(file_path)
            all_issues.extend(file_issues)
    
    if all_issues:
        print("📋 MCP Tool Docstring Validation Issues:")
        for issue in all_issues:
            print(issue)
        print("\n📖 See docs/DOCSTRING_CONVENTIONS.md for guidance")
        sys.exit(1)
    else:
        print("✅ All MCP tool docstrings are valid")


if __name__ == "__main__":
    main() 