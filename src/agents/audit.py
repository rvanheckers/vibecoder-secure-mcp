#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Audit Agent
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


def log_event(event: Dict[str, Any]) -> None:
    """
    Log an audit event to the append-only audit log.
    
    Args:
        event: Dictionary containing event information
    """
    # Ensure required fields
    if "timestamp" not in event:
        event["timestamp"] = datetime.now().isoformat()
    
    if "event_id" not in event:
        event["event_id"] = _generate_event_id(event)
    
    # Get project path from event or use current directory
    project_path = event.get("project_path", os.getcwd())
    audit_log_path = Path(project_path) / "audit.log"
    
    # Create audit log entry
    log_entry = {
        "event_id": event["event_id"],
        "timestamp": event["timestamp"],
        "event_type": event.get("event_type", "UNKNOWN"),
        "operation": event.get("operation", ""),
        "user": event.get("user", os.getenv("USER", "unknown")),
        "details": event.get("details", {}),
        "checksum": ""
    }
    
    # Compute checksum for integrity
    log_entry["checksum"] = _compute_entry_checksum(log_entry)
    
    # Append to audit log (append-only)
    try:
        with open(audit_log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        print(f"Audit event logged: {log_entry['event_type']} - {log_entry['operation']}")
        
    except Exception as e:
        print(f"Error logging audit event: {e}")


def read_audit_log(project_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Read audit log entries.
    
    Args:
        project_path: Path to the project directory
        limit: Maximum number of entries to return (None for all)
        
    Returns:
        List of audit log entries
    """
    audit_log_path = Path(project_path) / "audit.log"
    
    if not audit_log_path.exists():
        return []
    
    entries = []
    
    try:
        with open(audit_log_path) as f:
            lines = f.readlines()
        
        # Read entries (most recent first if limit specified)
        if limit:
            lines = lines[-limit:]
        
        for line in lines:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in audit log: {line}")
                    
    except Exception as e:
        print(f"Error reading audit log: {e}")
    
    return entries


def verify_audit_log(project_path: str) -> Tuple[bool, List[str]]:
    """
    Verify integrity of audit log.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    entries = read_audit_log(project_path)
    
    if not entries:
        issues.append("Audit log is empty or missing")
        return False, issues
    
    # Verify checksums
    for i, entry in enumerate(entries):
        if "checksum" not in entry:
            issues.append(f"Entry {i}: Missing checksum")
            continue
        
        stored_checksum = entry["checksum"]
        
        # Compute expected checksum
        entry_copy = entry.copy()
        entry_copy["checksum"] = ""
        expected_checksum = _compute_entry_checksum(entry_copy)
        
        if stored_checksum != expected_checksum:
            issues.append(f"Entry {i}: Checksum mismatch")
    
    # Check for required fields
    required_fields = ["event_id", "timestamp", "event_type", "operation"]
    for i, entry in enumerate(entries):
        for field in required_fields:
            if field not in entry:
                issues.append(f"Entry {i}: Missing required field '{field}'")
    
    # Check chronological order
    for i in range(1, len(entries)):
        prev_time = entries[i-1].get("timestamp", "")
        curr_time = entries[i].get("timestamp", "")
        
        if prev_time and curr_time and prev_time > curr_time:
            issues.append(f"Entry {i}: Chronological order violation")
    
    return len(issues) == 0, issues


def generate_audit_report(project_path: str, days: int = 7) -> Dict[str, Any]:
    """
    Generate audit report for specified time period.
    
    Args:
        project_path: Path to the project directory
        days: Number of days to include in report
        
    Returns:
        Dictionary containing audit report
    """
    entries = read_audit_log(project_path)
    
    # Filter entries by date
    cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
    recent_entries = []
    
    for entry in entries:
        try:
            entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
            if entry_time >= cutoff_date:
                recent_entries.append(entry)
        except (ValueError, KeyError):
            continue
    
    # Generate statistics
    event_types = {}
    operations = {}
    users = {}
    
    for entry in recent_entries:
        event_type = entry.get("event_type", "UNKNOWN")
        operation = entry.get("operation", "unknown")
        user = entry.get("user", "unknown")
        
        event_types[event_type] = event_types.get(event_type, 0) + 1
        operations[operation] = operations.get(operation, 0) + 1
        users[user] = users.get(user, 0) + 1
    
    # Verify log integrity
    is_valid, issues = verify_audit_log(project_path)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "report_period_days": days,
        "total_entries": len(entries),
        "recent_entries": len(recent_entries),
        "integrity_status": "VALID" if is_valid else "COMPROMISED",
        "integrity_issues": issues,
        "statistics": {
            "event_types": event_types,
            "operations": operations,
            "users": users
        },
        "recent_events": recent_entries[-10:]  # Last 10 events
    }
    
    return report


def log_generate_event(project_path: str, details: Dict[str, Any] = None) -> None:
    """Log document generation event"""
    event = {
        "project_path": project_path,
        "event_type": "GENERATE",
        "operation": "document_generation",
        "details": details or {}
    }
    log_event(event)


def log_validate_event(project_path: str, result: bool, errors: List[str] = None) -> None:
    """Log validation event"""
    event = {
        "project_path": project_path,
        "event_type": "VALIDATE",
        "operation": "document_validation",
        "details": {
            "result": "PASS" if result else "FAIL",
            "errors": errors or []
        }
    }
    log_event(event)


def log_heal_event(project_path: str, issues_healed: int, details: Dict[str, Any] = None) -> None:
    """Log auto-heal event"""
    event = {
        "project_path": project_path,
        "event_type": "HEAL",
        "operation": "auto_heal",
        "details": {
            "issues_healed": issues_healed,
            **(details or {})
        }
    }
    log_event(event)


def log_lock_event(project_path: str, merkle_root: str) -> None:
    """Log lock file update event"""
    event = {
        "project_path": project_path,
        "event_type": "LOCK",
        "operation": "update_lock_file",
        "details": {
            "merkle_root": merkle_root
        }
    }
    log_event(event)


def log_sign_event(project_path: str, signature: str) -> None:
    """Log signing event"""
    event = {
        "project_path": project_path,
        "event_type": "SIGN",
        "operation": "code_signing",
        "details": {
            "signature": signature
        }
    }
    log_event(event)


def log_backup_event(project_path: str, snapshot_id: str) -> None:
    """Log backup event"""
    event = {
        "project_path": project_path,
        "event_type": "BACKUP",
        "operation": "create_snapshot",
        "details": {
            "snapshot_id": snapshot_id
        }
    }
    log_event(event)


def _generate_event_id(event: Dict[str, Any]) -> str:
    """Generate unique event ID"""
    content = f"{event.get('timestamp', '')}{event.get('event_type', '')}{event.get('operation', '')}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _compute_entry_checksum(entry: Dict[str, Any]) -> str:
    """Compute checksum for audit log entry"""
    # Create deterministic string from entry
    content_parts = [
        entry.get("event_id", ""),
        entry.get("timestamp", ""),
        entry.get("event_type", ""),
        entry.get("operation", ""),
        entry.get("user", ""),
        json.dumps(entry.get("details", {}), sort_keys=True)
    ]
    
    content = "|".join(content_parts)
    return hashlib.sha256(content.encode()).hexdigest()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audit.py <project_path> [command] [args...]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "report"
    
    if command == "report":
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        report = generate_audit_report(project_path, days)
        print(json.dumps(report, indent=2))
        
    elif command == "verify":
        is_valid, issues = verify_audit_log(project_path)
        if is_valid:
            print("Audit log integrity: VALID")
        else:
            print("Audit log integrity: COMPROMISED")
            for issue in issues:
                print(f"  - {issue}")
                
    elif command == "read":
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
        entries = read_audit_log(project_path, limit)
        for entry in entries:
            print(json.dumps(entry, indent=2))
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)