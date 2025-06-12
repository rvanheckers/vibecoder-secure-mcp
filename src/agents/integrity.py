#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Integrity Verification Agent (Cryptographic Security)
Merkle tree-based integrity verification and tamper detection for project files

Dependencies:
- backup.py: Uses integrity hashes for backup verification
- audit.py: Uses compute_file_hash for audit log integrity
- compliance.py: Validates that Merkle hashing is enabled

Provides:
- SHA-256 Merkle tree computation for docs directory
- goldminer.lock file generation and verification
- Tamper detection and integrity validation
- File-level and directory-level hash verification
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


def compute_merkle(project_path: str) -> str:
    """
    Compute Merkle root hash for the entire project documentation.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Merkle root hash as hexadecimal string
    """
    project_dir = Path(project_path)
    docs_dir = project_dir / "docs"
    
    if not docs_dir.exists():
        return ""
    
    # Collect all file hashes
    file_hashes = []
    
    for file_path in sorted(docs_dir.rglob("*")):
        if file_path.is_file():
            file_hash = _compute_file_hash(file_path)
            relative_path = file_path.relative_to(docs_dir)
            file_hashes.append((str(relative_path), file_hash))
    
    if not file_hashes:
        return ""
    
    # Build Merkle tree
    merkle_root = _build_merkle_tree(file_hashes)
    
    # Update lock file with new Merkle root
    _update_lock_file(project_dir, merkle_root)
    
    return merkle_root


def verify_integrity(project_path: str) -> Tuple[bool, List[str]]:
    """
    Verify project integrity against stored Merkle root.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    project_dir = Path(project_path)
    issues = []
    
    # Read stored Merkle root from lock file
    stored_root = _get_stored_merkle_root(project_dir)
    if not stored_root:
        issues.append("No stored Merkle root found in lock file")
        return False, issues
    
    # Compute current Merkle root
    current_root = compute_merkle(project_path)
    if not current_root:
        issues.append("Cannot compute current Merkle root")
        return False, issues
    
    # Compare roots
    if stored_root != current_root:
        issues.append(f"Merkle root mismatch: stored={stored_root[:16]}..., current={current_root[:16]}...")
        return False, issues
    
    return True, []


def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file"""
    hasher = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Warning: Could not hash file {file_path}: {e}")
        return ""


def _build_merkle_tree(file_hashes: List[Tuple[str, str]]) -> str:
    """
    Build Merkle tree from file hashes.
    
    Args:
        file_hashes: List of (filename, hash) tuples
        
    Returns:
        Merkle root hash
    """
    if not file_hashes:
        return ""
    
    # Create leaf nodes: hash(filename + file_hash)
    leaves = []
    for filename, file_hash in file_hashes:
        leaf_data = f"{filename}:{file_hash}"
        leaf_hash = hashlib.sha256(leaf_data.encode()).hexdigest()
        leaves.append(leaf_hash)
    
    # Build tree bottom-up
    current_level = leaves
    
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs of nodes
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left  # Odd number of nodes, duplicate last one
            
            # Hash the concatenation
            combined = left + right
            parent_hash = hashlib.sha256(combined.encode()).hexdigest()
            next_level.append(parent_hash)
        
        current_level = next_level
    
    return current_level[0] if current_level else ""


def _update_lock_file(project_dir: Path, merkle_root: str) -> None:
    """Update lock file with new Merkle root"""
    lock_file = project_dir / "goldminer.lock"
    
    try:
        # Read existing lock file content
        if lock_file.exists():
            with open(lock_file) as f:
                content = f.read()
        else:
            content = """# VIBECODER-SECURE MCP Lock File
# Auto-generated - do not edit manually
version = "1.0.0"
lockfile_version = 1
created = "2025-06-12T00:00:00Z"

[integrity]
merkle_root = ""
last_validated = ""
"""
        
        # Update Merkle root and timestamp
        lines = content.split('\n')
        new_lines = []
        in_integrity_section = False
        
        for line in lines:
            if line.strip() == "[integrity]":
                in_integrity_section = True
                new_lines.append(line)
            elif in_integrity_section and line.startswith("merkle_root"):
                new_lines.append(f'merkle_root = "{merkle_root}"')
            elif in_integrity_section and line.startswith("last_validated"):
                timestamp = datetime.now().isoformat()
                new_lines.append(f'last_validated = "{timestamp}"')
            else:
                new_lines.append(line)
        
        # Write updated content
        with open(lock_file, 'w') as f:
            f.write('\n'.join(new_lines))
            
    except Exception as e:
        print(f"Warning: Could not update lock file: {e}")


def _get_stored_merkle_root(project_dir: Path) -> Optional[str]:
    """Get stored Merkle root from lock file"""
    lock_file = project_dir / "goldminer.lock"
    
    if not lock_file.exists():
        return None
    
    try:
        with open(lock_file) as f:
            content = f.read()
        
        # Parse Merkle root from file
        for line in content.split('\n'):
            if line.strip().startswith('merkle_root = "'):
                # Extract value between quotes
                start = line.find('"') + 1
                end = line.rfind('"')
                if start > 0 and end > start:
                    return line[start:end]
        
        return None
        
    except Exception as e:
        print(f"Warning: Could not read lock file: {e}")
        return None


def generate_integrity_report(project_path: str) -> Dict:
    """
    Generate comprehensive integrity report.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary containing integrity report
    """
    project_dir = Path(project_path)
    docs_dir = project_dir / "docs"
    
    # Basic statistics
    file_count = 0
    total_size = 0
    file_details = []
    
    if docs_dir.exists():
        for file_path in docs_dir.rglob("*"):
            if file_path.is_file():
                file_count += 1
                size = file_path.stat().st_size
                total_size += size
                
                file_details.append({
                    "path": str(file_path.relative_to(docs_dir)),
                    "size": size,
                    "hash": _compute_file_hash(file_path),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
    
    # Integrity verification
    is_valid, issues = verify_integrity(project_path)
    current_merkle = compute_merkle(project_path)
    stored_merkle = _get_stored_merkle_root(project_dir)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "integrity_status": "VALID" if is_valid else "INVALID",
        "statistics": {
            "file_count": file_count,
            "total_size": total_size
        },
        "merkle_roots": {
            "current": current_merkle,
            "stored": stored_merkle,
            "match": current_merkle == stored_merkle if both_exist(current_merkle, stored_merkle) else False
        },
        "issues": issues,
        "files": file_details
    }
    
    return report


def both_exist(a: Optional[str], b: Optional[str]) -> bool:
    """Check if both values exist and are not empty"""
    return bool(a and b)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        
        if len(sys.argv) > 2 and sys.argv[2] == "report":
            # Generate full report
            report = generate_integrity_report(project_path)
            print(json.dumps(report, indent=2))
        else:
            # Compute and display Merkle root
            merkle_root = compute_merkle(project_path)
            if merkle_root:
                print(f"Merkle root: {merkle_root}")
                
                # Verify integrity
                is_valid, issues = verify_integrity(project_path)
                if is_valid:
                    print("Integrity: VALID")
                else:
                    print("Integrity: INVALID")
                    for issue in issues:
                        print(f"  - {issue}")
            else:
                print("Could not compute Merkle root")
    else:
        print("Usage: python integrity.py <project_path> [report]")