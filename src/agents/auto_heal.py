#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Auto Healing Agent
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from .validate_docs import validate
from .generate_docs import generate


def heal(project_path: str) -> None:
    """
    Auto-heal detected issues in the project.
    
    Args:
        project_path: Path to the project directory
    """
    project_dir = Path(project_path)
    
    print(f"Starting auto-heal for {project_path}")
    
    # First, validate to identify issues
    errors = validate(project_path, fast=False)
    
    if not errors:
        print("No issues detected, project is healthy")
        return
    
    print(f"Found {len(errors)} issues to heal:")
    for error in errors:
        print(f"  - {error}")
    
    # Attempt to heal each issue
    healed_count = 0
    for error in errors:
        if _heal_issue(project_dir, error):
            healed_count += 1
    
    print(f"Successfully healed {healed_count}/{len(errors)} issues")
    
    # Re-validate after healing
    remaining_errors = validate(project_path, fast=False)
    if remaining_errors:
        print(f"Remaining issues after healing:")
        for error in remaining_errors:
            print(f"  - {error}")
    else:
        print("All issues successfully healed")


def _heal_issue(project_dir: Path, error: str) -> bool:
    """
    Attempt to heal a specific issue.
    
    Args:
        project_dir: Project directory path
        error: Error description
        
    Returns:
        True if issue was healed successfully
    """
    try:
        if "Missing required file:" in error:
            return _heal_missing_file(project_dir, error)
        elif "Missing docs directory" in error:
            return _heal_missing_docs(project_dir)
        elif "Missing documentation file:" in error:
            return _heal_missing_doc_file(project_dir, error)
        elif "Empty documentation file:" in error:
            return _heal_empty_doc_file(project_dir, error)
        elif "Missing goldminer.lock file" in error:
            return _heal_missing_lock_file(project_dir)
        else:
            print(f"Cannot auto-heal: {error}")
            return False
            
    except Exception as e:
        print(f"Failed to heal '{error}': {e}")
        return False


def _heal_missing_file(project_dir: Path, error: str) -> bool:
    """Heal missing required files"""
    file_name = error.split(": ")[-1]
    
    if file_name == "Makefile":
        _create_default_makefile(project_dir)
        return True
    elif file_name == "requirements.txt":
        _create_default_requirements(project_dir)
        return True
    elif file_name == "ai-plugin.json":
        _create_default_plugin_config(project_dir)
        return True
    elif file_name == "goldminer.toml":
        _create_default_goldminer_config(project_dir)
        return True
    
    return False


def _heal_missing_docs(project_dir: Path) -> bool:
    """Create missing docs directory and regenerate docs"""
    docs_dir = project_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    generate(str(project_dir))
    return True


def _heal_missing_doc_file(project_dir: Path, error: str) -> bool:
    """Regenerate missing documentation file"""
    generate(str(project_dir))
    return True


def _heal_empty_doc_file(project_dir: Path, error: str) -> bool:
    """Regenerate empty documentation file"""
    generate(str(project_dir))
    return True


def _heal_missing_lock_file(project_dir: Path) -> bool:
    """Create missing lock file"""
    lock_content = """# VIBECODER-SECURE MCP Lock File
# Auto-generated - do not edit manually
version = "1.0.0"
lockfile_version = 1
created = "2025-06-12T00:00:00Z"

[integrity]
merkle_root = ""
last_validated = ""
"""
    with open(project_dir / "goldminer.lock", "w") as f:
        f.write(lock_content)
    return True


def _create_default_makefile(project_dir: Path) -> None:
    """Create default Makefile"""
    makefile_content = """SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)

.PHONY: init generate validate heal lock sign audit backup clean rebuild

init:
\t@vibecoder-secure-mcp init $(PROJECT_DIR)

generate:
\t@vibecoder-secure-mcp generate $(PROJECT_DIR)

validate:
\t@vibecoder-secure-mcp validate $(PROJECT_DIR)

heal:
\t@vibecoder-secure-mcp heal $(PROJECT_DIR)

lock:
\t@vibecoder-secure-mcp lock --update $(PROJECT_DIR)

sign:
\t@vibecoder-secure-mcp sign --key $(GPG_KEY) $(PROJECT_DIR)

audit:
\t@vibecoder-secure-mcp audit $(PROJECT_DIR) > audit.log

backup:
\t@vibecoder-secure-mcp backup $(PROJECT_DIR)

clean:
\t@rm -rf docs .goldminer goldminer.lock goldminer.toml ai-plugin.json src

rebuild: clean init generate validate lock sign audit backup
\t@echo "Rebuild complete."
"""
    with open(project_dir / "Makefile", "w") as f:
        f.write(makefile_content)


def _create_default_requirements(project_dir: Path) -> None:
    """Create default requirements.txt"""
    requirements = """vibecoder-secure-mcp
fastapi
uvicorn
pyyaml
cryptography
mistune
openai
langchain
redis
gitpython
python-gitlab
"""
    with open(project_dir / "requirements.txt", "w") as f:
        f.write(requirements)


def _create_default_plugin_config(project_dir: Path) -> None:
    """Create default ai-plugin.json"""
    plugin_config = """{
  "schema_version":"v1",
  "name_for_human":"VIBECODER-SECURE MCP",
  "name_for_model":"vibecoder_secure_mcp",
  "description_for_human":"Veilige docs-pipeline met integriteit & audit",
  "description_for_model":"Gebruik alleen de endpoints generate, validate, heal, lock en sign; raak niets anders aan.",
  "auth":{"type":"none"},
  "api":{"url":"https://your-domain.com/openapi.json"}
}"""
    with open(project_dir / "ai-plugin.json", "w") as f:
        f.write(plugin_config)


def _create_default_goldminer_config(project_dir: Path) -> None:
    """Create default goldminer.toml"""
    goldminer_config = """[project]
name = "VIBECODER-SECURE MCP"
version = "1.0.0"

[dependencies]
vibecoder-secure-mcp = "latest"

[security]
enable_integrity_checks = true
require_code_signing = true
"""
    with open(project_dir / "goldminer.toml", "w") as f:
        f.write(goldminer_config)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        heal(sys.argv[1])
    else:
        print("Usage: python auto_heal.py <project_path>")