#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Compliance Agent
"""

import os
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


def check_compliance(project_path: str) -> List[str]:
    """
    Check project compliance with security and operational requirements.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        List of compliance violations (empty if compliant)
    """
    violations = []
    project_dir = Path(project_path)
    
    if not project_dir.exists():
        violations.append(f"Project directory does not exist: {project_path}")
        return violations
    
    # Check security compliance
    violations.extend(_check_security_compliance(project_dir))
    
    # Check operational compliance
    violations.extend(_check_operational_compliance(project_dir))
    
    # Check data integrity compliance
    violations.extend(_check_integrity_compliance(project_dir))
    
    # Check audit compliance
    violations.extend(_check_audit_compliance(project_dir))
    
    return violations


def _check_security_compliance(project_dir: Path) -> List[str]:
    """Check security-related compliance requirements"""
    violations = []
    
    # Check if security configuration is enabled
    config_file = project_dir / ".goldminer" / "config.yml"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            security_config = config.get("security", {})
            
            if not security_config.get("enable_merkle_hashing"):
                violations.append("Security violation: Merkle hashing not enabled")
            
            if not security_config.get("require_signatures"):
                violations.append("Security violation: Code signing not required")
            
            if not security_config.get("audit_logging"):
                violations.append("Security violation: Audit logging not enabled")
                
        except Exception as e:
            violations.append(f"Security violation: Cannot read config file: {e}")
    else:
        violations.append("Security violation: Missing security configuration")
    
    # Check for sensitive data exposure
    violations.extend(_check_sensitive_data(project_dir))
    
    return violations


def _check_operational_compliance(project_dir: Path) -> List[str]:
    """Check operational compliance requirements"""
    violations = []
    
    # Check required operational files
    required_files = [
        ("Makefile", "Missing operational file: Makefile"),
        ("requirements.txt", "Missing operational file: requirements.txt"),
        ("ai-plugin.json", "Missing operational file: ai-plugin.json")
    ]
    
    for file_path, error_msg in required_files:
        if not (project_dir / file_path).exists():
            violations.append(error_msg)
    
    # Check Git configuration
    if not (project_dir / ".git").exists():
        violations.append("Operational violation: Git repository not initialized")
    
    # Check backup configuration
    config_file = project_dir / ".goldminer" / "config.yml"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            backup_config = config.get("backup", {})
            if not backup_config.get("auto_snapshot"):
                violations.append("Operational violation: Auto-snapshot not enabled")
                
        except Exception:
            pass
    
    return violations


def _check_integrity_compliance(project_dir: Path) -> List[str]:
    """Check data integrity compliance"""
    violations = []
    
    # Check lock file exists and is valid
    lock_file = project_dir / "goldminer.lock"
    if not lock_file.exists():
        violations.append("Integrity violation: Missing lock file")
    else:
        try:
            with open(lock_file) as f:
                lock_content = f.read()
            
            if not lock_content.strip():
                violations.append("Integrity violation: Empty lock file")
            
            # Check for required sections
            if "[integrity]" not in lock_content:
                violations.append("Integrity violation: Lock file missing integrity section")
                
        except Exception as e:
            violations.append(f"Integrity violation: Cannot read lock file: {e}")
    
    # Check documentation integrity
    docs_dir = project_dir / "docs"
    if docs_dir.exists():
        required_docs = ["README.md", "API.md", "SECURITY.md"]
        for doc in required_docs:
            doc_path = docs_dir / doc
            if not doc_path.exists():
                violations.append(f"Integrity violation: Missing documentation: {doc}")
            elif doc_path.stat().st_size == 0:
                violations.append(f"Integrity violation: Empty documentation: {doc}")
    
    return violations


def _check_audit_compliance(project_dir: Path) -> List[str]:
    """Check audit trail compliance"""
    violations = []
    
    # Check if audit logging is properly configured
    audit_log = project_dir / "audit.log"
    if audit_log.exists():
        try:
            with open(audit_log) as f:
                log_content = f.read()
            
            if not log_content.strip():
                violations.append("Audit violation: Empty audit log")
            
            # Check for recent activity (within last 24 hours)
            mod_time = audit_log.stat().st_mtime
            current_time = datetime.now().timestamp()
            
            if (current_time - mod_time) > 86400:  # 24 hours
                violations.append("Audit violation: No recent audit activity")
                
        except Exception as e:
            violations.append(f"Audit violation: Cannot read audit log: {e}")
    
    return violations


def _check_sensitive_data(project_dir: Path) -> List[str]:
    """Check for sensitive data exposure"""
    violations = []
    
    # List of patterns that might indicate sensitive data
    sensitive_patterns = [
        "password",
        "secret",
        "key",
        "token",
        "api_key",
        "private_key"
    ]
    
    # Check configuration files for sensitive data
    config_files = [
        project_dir / ".goldminer" / "config.yml",
        project_dir / "goldminer.toml",
        project_dir / "ai-plugin.json"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file) as f:
                    content = f.read().lower()
                
                for pattern in sensitive_patterns:
                    if pattern in content and "=" in content:
                        violations.append(f"Security violation: Potential sensitive data in {config_file.name}")
                        break
                        
            except Exception:
                pass
    
    return violations


def generate_compliance_report(project_path: str) -> Dict[str, Any]:
    """
    Generate a comprehensive compliance report.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Dictionary containing compliance report
    """
    violations = check_compliance(project_path)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "compliance_status": "COMPLIANT" if not violations else "NON_COMPLIANT",
        "total_violations": len(violations),
        "violations": violations,
        "recommendations": _generate_recommendations(violations)
    }
    
    return report


def _generate_recommendations(violations: List[str]) -> List[str]:
    """Generate recommendations based on violations"""
    recommendations = []
    
    for violation in violations:
        if "Merkle hashing not enabled" in violation:
            recommendations.append("Enable merkle_hashing in .goldminer/config.yml")
        elif "Code signing not required" in violation:
            recommendations.append("Enable require_signatures in .goldminer/config.yml")
        elif "Missing lock file" in violation:
            recommendations.append("Run 'make lock' to generate integrity lock file")
        elif "Git repository not initialized" in violation:
            recommendations.append("Run 'git init' to initialize Git repository")
        elif "Missing documentation" in violation:
            recommendations.append("Run 'make generate' to create missing documentation")
    
    return recommendations


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        violations = check_compliance(sys.argv[1])
        if violations:
            print("Compliance violations found:")
            for violation in violations:
                print(f"  - {violation}")
            
            print("\nCompliance Report:")
            report = generate_compliance_report(sys.argv[1])
            print(json.dumps(report, indent=2))
            
            sys.exit(1)
        else:
            print("Project is compliant with all requirements")
    else:
        print("Usage: python compliance.py <project_path>")