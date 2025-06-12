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
    Automatically update ALL leading documents (CLAUDE.md, README.md) with current project state.
    Ensures sync between VIBECODER-MANUAL.md (master) and other docs.
    
    Args:
        project_path: Path to the project directory
    """
    project_dir = Path(project_path)
    claude_md_path = project_dir / "CLAUDE.md"
    readme_md_path = project_dir / "README.md"
    
    if not claude_md_path.exists():
        print("Warning: CLAUDE.md not found, creating new handover document")
        _create_initial_handover_document(project_dir)
        return
    
    # Gather current project state
    project_state = _gather_project_state(project_dir)
    
    # Update CLAUDE.md with current state
    _update_document_content(claude_md_path, project_state)
    
    # Update README.md with current agent count and structure
    if readme_md_path.exists():
        _sync_readme_with_reality(readme_md_path, project_state)
    
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
    """Get file count statistics including agents and Makefile targets"""
    counts = {
        "total_files": 0,
        "python_files": 0,
        "docs_files": 0,
        "config_files": 0,
        "agent_files": 0,
        "makefile_targets": 0
    }
    
    try:
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                counts["total_files"] += 1
                
                if file_path.suffix == ".py":
                    counts["python_files"] += 1
                    
                    # Count agent files specifically
                    if "agents" in str(file_path) and file_path.name != "__init__.py":
                        counts["agent_files"] += 1
                        
                elif file_path.suffix in [".md", ".txt", ".rst"]:
                    counts["docs_files"] += 1
                elif file_path.suffix in [".yml", ".yaml", ".toml", ".json"]:
                    counts["config_files"] += 1
        
        # Count Makefile targets
        makefile_path = project_dir / "Makefile"
        if makefile_path.exists():
            with open(makefile_path) as f:
                makefile_content = f.read()
            import re
            targets = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*):', makefile_content, re.MULTILINE)
            counts["makefile_targets"] = len(set(targets))  # Remove duplicates
                    
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


def _sync_readme_with_reality(readme_path: Path, state: Dict[str, Any]) -> None:
    """Sync README.md with actual project structure and agent count"""
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update agent count in features section
        agent_count = state['file_counts']['agent_files']
        makefile_targets = state['file_counts']['makefile_targets']
        
        # Update "15 agents + 15 targets" to actual counts
        old_pattern = r'(\d+) agents \+ (\d+) (Makefile )?targets'
        new_text = f"{agent_count} agents + {makefile_targets} Makefile targets"
        
        import re
        content = re.sub(old_pattern, new_text, content)
        
        # Update directory schema to show actual agents
        actual_agents = _get_actual_agent_list(readme_path.parent)
        
        # Find and replace the architecture section
        arch_start = content.find("## 🏗️ Architecture")
        if arch_start != -1:
            arch_end = content.find("##", arch_start + 1)
            if arch_end == -1:
                arch_end = len(content)
            
            # Generate new architecture section
            new_arch = _generate_architecture_section(actual_agents, agent_count, makefile_targets)
            content = content[:arch_start] + new_arch + content[arch_end:]
        
        # Write back
        with open(readme_path, 'w') as f:
            f.write(content)
            
    except Exception as e:
        print(f"Warning: Could not sync README.md: {e}")


def _get_actual_agent_list(project_dir: Path) -> List[str]:
    """Get list of actual agent files"""
    agents_dir = project_dir / "src" / "agents"
    if not agents_dir.exists():
        return []
    
    agents = []
    for agent_file in agents_dir.glob("*.py"):
        if agent_file.name not in ["__init__.py", "__pycache__"]:
            agents.append(agent_file.name)
    
    return sorted(agents)


def _generate_architecture_section(agents: List[str], agent_count: int, target_count: int) -> str:
    """Generate updated architecture section with actual agent list"""
    
    # Core agents to highlight
    core_agents = [
        ("generate_docs.py", "Documentation generation"),
        ("validate_docs.py", "Integrity validation"), 
        ("auto_heal.py", "Auto-healing & recovery"),
        ("integrity.py", "Merkle tree hashing"),
        ("audit.py", "Audit logging"),
        ("backup.py", "Backup & restore"),
        ("smart_automation.py", "Context-aware automation"),
        ("enhanced_context.py", "AI context preservation"),
        ("monitoring.py", "Real-time monitoring"),
        ("duplicate_detection.py", "Git-aware duplicate detection"),
        ("file_placement.py", "Intelligent file organization"),
        ("visual_roadmap.py", "Interactive roadmap generation")
    ]
    
    # Build agent list showing critical ones
    agent_list = ""
    for agent, description in core_agents:
        if agent in agents:
            agent_list += f"│   ├── {agent:<20} # {description}\n"
    
    # Add "and X more..." if there are additional agents
    additional_count = len(agents) - len([a for a, _ in core_agents if a in agents])
    if additional_count > 0:
        agent_list += f"│   └── ... and {additional_count} more agents\n"
    
    return f"""## 🏗️ Architecture

**UNBREAKABLE SYSTEM**: {agent_count} agents, {target_count} Makefile targets

```
├── main.py                 # FastAPI MCP hub orchestrator
├── src/agents/            # {agent_count} UNBREAKABLE AGENTS
{agent_list}├── docs/                  # Generated documentation & HTML dashboards
├── .goldminer/           # Configuration, metrics & JSON logic
└── CLAUDE.md             # AI handover document (auto-updated)
```

"""


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