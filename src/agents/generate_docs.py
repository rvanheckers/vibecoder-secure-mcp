#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Document Generation Agent (Core Documentation)
Generates standardized API, Security, and project documentation from templates

Dependencies:
- auto_heal.py: Called during healing to regenerate missing docs
- main.py: Triggered via /generate endpoint and make generate
- handover_updater.py: Updates CLAUDE.md after documentation generation

Generates:
- docs/API.md: FastAPI endpoint documentation
- docs/SECURITY.md: Security model and compliance documentation
- Maintains root README.md (does not duplicate in docs/)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


def generate(project_path: str) -> None:
    """
    Generate documentation for the VIBECODER-SECURE MCP project.
    
    Args:
        project_path: Path to the project directory
    """
    docs_dir = Path(project_path) / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # Generate main documentation (README.md stays in root, not docs)
    _generate_api_docs(docs_dir)
    _generate_security_docs(docs_dir)
    
    print(f"Documentation generated in {docs_dir}")


def _generate_readme(docs_dir: Path) -> None:
    """Generate README.md file"""
    readme_content = """# VIBECODER-SECURE MCP

Secure document pipeline with integrity validation and audit capabilities.

## Features

- Secure document generation and validation
- Merkle tree integrity checking
- Audit logging for all operations
- Automated backup and restore
- Git hooks integration

## Usage

```bash
make generate    # Generate documentation
make validate    # Validate integrity
make heal        # Auto-heal issues
make lock        # Update lock file
make sign        # Sign with GPG
make audit       # Generate audit log
make backup      # Create backup snapshot
```

## Security

All operations are logged and validated through cryptographic hashing.
"""
    
    with open(docs_dir / "README.md", "w") as f:
        f.write(readme_content)


def _generate_api_docs(docs_dir: Path) -> None:
    """Generate API documentation"""
    api_content = """# API Documentation

## Endpoints

### POST /generate
Generate project documentation

### POST /validate  
Validate document integrity

### POST /heal
Auto-heal detected issues

### POST /lock
Update integrity lock file

### POST /sign
Sign documents with GPG key

## Security

All endpoints require valid project path validation.
"""
    
    with open(docs_dir / "API.md", "w") as f:
        f.write(api_content)


def _generate_security_docs(docs_dir: Path) -> None:
    """Generate security documentation"""
    security_content = """# Security Model

## Integrity Validation

- Merkle tree hashing of all documents
- SHA-256 cryptographic verification
- Lock file prevents unauthorized changes

## Audit Trail

- All operations logged with timestamps
- Append-only audit log
- Immutable operation history

## Access Control

- Project path validation
- GPG signing requirements
- Human approval for deletions
"""
    
    with open(docs_dir / "SECURITY.md", "w") as f:
        f.write(security_content)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate(sys.argv[1])
    else:
        print("Usage: python generate_docs.py <project_path>")