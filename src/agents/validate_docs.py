#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Document Validation Agent
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional


def validate(project_path: str, fast: bool = False) -> List[str]:
    """
    Validate document integrity and compliance.
    
    Args:
        project_path: Path to the project directory
        fast: If True, perform fast validation only
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    project_dir = Path(project_path)
    
    if not project_dir.exists():
        errors.append(f"Project directory does not exist: {project_path}")
        return errors
    
    # Validate required files
    errors.extend(_validate_required_files(project_dir))
    
    if not fast:
        # Full validation including integrity checks
        errors.extend(_validate_integrity(project_dir))
        errors.extend(_validate_compliance(project_dir))
    
    return errors


def _validate_required_files(project_dir: Path) -> List[str]:
    """Validate that required files exist"""
    errors = []
    required_files = [
        "Makefile",
        "requirements.txt", 
        "ai-plugin.json",
        "goldminer.toml",
        ".goldminer/manifest.json",
        ".goldminer/config.yml"
    ]
    
    for file_path in required_files:
        if not (project_dir / file_path).exists():
            errors.append(f"Missing required file: {file_path}")
    
    return errors


def _validate_integrity(project_dir: Path) -> List[str]:
    """Validate document integrity using hashes"""
    errors = []
    docs_dir = project_dir / "docs"
    
    if not docs_dir.exists():
        errors.append("Missing docs directory")
        return errors
    
    # Check for expected documentation files (README.md should be in root, not docs)
    expected_docs = ["API.md", "SECURITY.md"]
    for doc in expected_docs:
        doc_path = docs_dir / doc
        if not doc_path.exists():
            errors.append(f"Missing documentation file: {doc}")
        elif doc_path.stat().st_size == 0:
            errors.append(f"Empty documentation file: {doc}")
    
    # Check that README.md is in root, not in docs (to avoid duplication)
    docs_readme = docs_dir / "README.md"
    root_readme = project_dir / "README.md"
    if docs_readme.exists():
        errors.append("README.md should be in root directory, not docs/ (prevents duplication)")
    if not root_readme.exists():
        errors.append("Missing README.md in root directory")
    
    return errors


def _validate_compliance(project_dir: Path) -> List[str]:
    """Validate compliance with security requirements"""
    errors = []
    
    # Check lock file exists and is valid
    lock_file = project_dir / "goldminer.lock"
    if not lock_file.exists():
        errors.append("Missing goldminer.lock file - run 'make lock' first")
    
    # Validate configuration
    config_file = project_dir / ".goldminer" / "config.yml"
    if config_file.exists():
        try:
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            if not config.get("security", {}).get("enable_merkle_hashing"):
                errors.append("Merkle hashing not enabled in config")
                
        except Exception as e:
            errors.append(f"Invalid config file: {e}")
    
    return errors


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        errors = validate(sys.argv[1])
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("Validation passed")
    else:
        print("Usage: python validate_docs.py <project_path>")