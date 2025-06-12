#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Handover Document Auto-Updater
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


def update_handover_document(project_path: str) -> None:
    """
    Automatically update the CLAUDE.md handover document with current project state.
    
    Args:
        project_path: Path to the project directory
    """
    project_dir = Path(project_path)
    claude_md_path = project_dir / "CLAUDE.md"
    
    if not claude_md_path.exists():
        print("Warning: CLAUDE.md not found, creating new handover document")
        _create_initial_handover_document(project_dir)
        return
    
    # Gather current project state
    project_state = _gather_project_state(project_dir)
    
    # Update document with current state
    _update_document_content(claude_md_path, project_state)
    
    print("Handover document updated successfully")


def _gather_project_state(project_dir: Path) -> Dict[str, Any]:
    """Gather current project state information"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "git_info": _get_git_info(project_dir),
        "file_counts": _get_file_counts(project_dir),
        "integrity_status": _get_integrity_status(project_dir),
        "recent_operations": _get_recent_operations(project_dir)
    }
    
    return state


def _get_git_info(project_dir: Path) -> Dict[str, str]:
    """Get Git repository information"""
    git_info = {
        "commit": "unknown",
        "branch": "unknown", 
        "status": "unknown"
    }
    
    try:
        # Get current commit hash
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_info["commit"] = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_info["branch"] = result.stdout.strip() or "detached"
        
        # Get status summary
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            git_info["status"] = f"{len(changes)} changes" if changes else "clean"
            
    except Exception as e:
        print(f"Warning: Could not get Git info: {e}")
    
    return git_info


def _get_file_counts(project_dir: Path) -> Dict[str, int]:
    """Get file count statistics"""
    counts = {
        "total_files": 0,
        "python_files": 0,
        "docs_files": 0,
        "config_files": 0
    }
    
    try:
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                counts["total_files"] += 1
                
                if file_path.suffix == ".py":
                    counts["python_files"] += 1
                elif file_path.suffix in [".md", ".txt", ".rst"]:
                    counts["docs_files"] += 1
                elif file_path.suffix in [".yml", ".yaml", ".toml", ".json"]:
                    counts["config_files"] += 1
                    
    except Exception as e:
        print(f"Warning: Could not count files: {e}")
    
    return counts


def _get_integrity_status(project_dir: Path) -> str:
    """Get current integrity status"""
    try:
        # Try to import and run validation
        import sys
        sys.path.insert(0, str(project_dir / "src"))
        
        from agents.validate_docs import validate
        errors = validate(str(project_dir), fast=True)
        
        if not errors:
            return "VALID"
        else:
            return f"ISSUES ({len(errors)} errors)"
            
    except Exception as e:
        return f"UNKNOWN ({str(e)[:50]}...)"


def _get_recent_operations(project_dir: Path) -> List[str]:
    """Get recent operations from audit log"""
    operations = []
    
    try:
        audit_log_path = project_dir / "audit.log"
        if audit_log_path.exists():
            with open(audit_log_path) as f:
                lines = f.readlines()
            
            # Get last 3 operations
            recent_lines = lines[-3:] if len(lines) >= 3 else lines
            
            for line in recent_lines:
                try:
                    import json
                    entry = json.loads(line.strip())
                    op = f"{entry.get('event_type', 'UNKNOWN')} - {entry.get('timestamp', '')[:16]}"
                    operations.append(op)
                except:
                    continue
                    
    except Exception:
        operations = ["No recent operations found"]
    
    return operations


def _update_document_content(claude_md_path: Path, state: Dict[str, Any]) -> None:
    """Update the CLAUDE.md document with current state"""
    
    try:
        with open(claude_md_path, 'r') as f:
            content = f.read()
        
        # Update timestamp
        content = _update_field(content, "Last Updated", f"{state['date']} (auto-generated)")
        
        # Update Git commit
        git_commit = state['git_info']['commit']
        git_status = state['git_info']['status']
        content = _update_field(content, "Git Commit", f"{git_commit} ({git_status})")
        
        # Update status section
        integrity_status = state['integrity_status']
        content = _update_field(content, "Status", f"OPERATIONAL - Integrity: {integrity_status}")
        
        # Update file counts in a comment section
        file_info = f"Files: {state['file_counts']['total_files']} total, {state['file_counts']['python_files']} Python, {state['file_counts']['docs_files']} docs"
        
        # Add/update auto-generated footer
        footer_marker = "*Auto-generated by VIBECODER-SECURE MCP"
        if footer_marker in content:
            # Update existing footer
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if footer_marker in line:
                    lines[i] = f"*Auto-generated by VIBECODER-SECURE MCP - Last scan: {state['date']} - {file_info}*"
                    break
            content = '\n'.join(lines)
        else:
            # Add new footer
            content += f"\n\n---\n\n*Auto-generated by VIBECODER-SECURE MCP - Last scan: {state['date']} - {file_info}*"
        
        # Write updated content
        with open(claude_md_path, 'w') as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error updating handover document: {e}")


def _update_field(content: str, field_name: str, new_value: str) -> str:
    """Update a field in the markdown content"""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith(f"**{field_name}**:"):
            lines[i] = f"**{field_name}**: {new_value}"
            break
    
    return '\n'.join(lines)


def _create_initial_handover_document(project_dir: Path) -> None:
    """Create initial handover document if it doesn't exist"""
    claude_md_path = project_dir / "CLAUDE.md"
    
    initial_content = f"""# VIBECODER-SECURE MCP - AI Handover Document

**Project**: VIBECODER-SECURE MCP  
**Created**: {datetime.now().strftime("%Y-%m-%d")}  
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")} (auto-generated)  
**Status**: OPERATIONAL  
**Git Commit**: unknown

## 🎯 Project Overview

Complete secure document pipeline with integrity validation, audit capabilities, and automated workflows.

This document is automatically maintained and updated by the handover_updater.py agent.

---

*Auto-generated by VIBECODER-SECURE MCP - Initial creation: {datetime.now().strftime("%Y-%m-%d")}*
"""
    
    with open(claude_md_path, 'w') as f:
        f.write(initial_content)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        update_handover_document(sys.argv[1])
    else:
        print("Usage: python handover_updater.py <project_path>")