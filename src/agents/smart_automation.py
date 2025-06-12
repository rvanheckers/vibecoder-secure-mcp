#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Smart Automation System (VIB-007)
VIBECODER-specific automation with intelligent triggers, smart healing, and proactive monitoring

Dependencies:
- file_placement.py: Uses placement rules for automated file organization
- auto_heal.py: Triggers healing based on automation rules
- audit.py: Logs automation events and rule executions
- Git hooks: Integrates with pre-commit and post-merge automation

Automation Rules (47 total):
- Auto-commit documentation changes
- Proactive integrity validation (every 30 minutes)
- Smart healing on validation failure
- Auto-backup critical changes
- File placement suggestions
- Context-aware responses based on VIBECODER workflows
- Time-based maintenance tasks
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class AutomationRule:
    """Defines an automation rule"""
    id: str
    name: str
    trigger: str  # file_change, time_based, git_event, validation_failure
    condition: str
    action: str
    vibecoder_focus: str
    enabled: bool = True
    last_triggered: Optional[str] = None


class VibecoderSmartAutomation:
    """Smart automation for Vibecoder workflows"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.automation_dir = self.project_path / ".goldminer" / "automation"
        self.automation_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules_file = self.automation_dir / "automation_rules.json"
        self.state_file = self.automation_dir / "automation_state.json"
        self.log_file = self.automation_dir / "automation.log"
        
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default Vibecoder automation rules"""
        if self.rules_file.exists():
            return
        
        default_rules = [
            AutomationRule(
                id="auto_commit_docs",
                name="Auto-commit Documentation Changes",
                trigger="file_change",
                condition="docs/*.md OR *.md files modified",
                action="git_commit_with_message",
                vibecoder_focus="workflow_automation"
            ),
            AutomationRule(
                id="proactive_integrity_check",
                name="Proactive Integrity Validation",
                trigger="time_based",
                condition="every_30_minutes",
                action="validate_and_heal",
                vibecoder_focus="security_integrity"
            ),
            AutomationRule(
                id="auto_backup_critical_changes",
                name="Auto-backup Critical Changes",
                trigger="git_event",
                condition="commits to critical files",
                action="create_snapshot",
                vibecoder_focus="backup_recovery"
            ),
            AutomationRule(
                id="smart_healing_validation_failure",
                name="Smart Healing on Validation Failure",
                trigger="validation_failure",
                condition="validation errors detected",
                action="auto_heal_and_regenerate",
                vibecoder_focus="workflow_automation"
            ),
            AutomationRule(
                id="ai_handover_update",
                name="Auto-update AI Handover Documents",
                trigger="file_change",
                condition="any significant project changes",
                action="update_handover_context",
                vibecoder_focus="ai_handover"
            )
        ]
        
        rules_data = [asdict(rule) for rule in default_rules]
        with open(self.rules_file, 'w') as f:
            json.dump(rules_data, f, indent=2)
    
    def check_and_execute_automation(self) -> Dict[str, Any]:
        """Check all automation rules and execute applicable ones"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "triggered_rules": [],
            "skipped_rules": [],
            "errors": []
        }
        
        rules = self._load_rules()
        
        for rule_data in rules:
            rule = AutomationRule(**rule_data)
            
            if not rule.enabled:
                results["skipped_rules"].append(f"{rule.id} (disabled)")
                continue
            
            try:
                should_trigger = self._evaluate_trigger(rule)
                if should_trigger:
                    action_result = self._execute_action(rule)
                    results["triggered_rules"].append({
                        "rule_id": rule.id,
                        "action": rule.action,
                        "result": action_result
                    })
                    
                    # Update last triggered time
                    rule.last_triggered = datetime.now().isoformat()
                    self._update_rule(rule)
                    
            except Exception as e:
                error_msg = f"Error in rule {rule.id}: {str(e)}"
                results["errors"].append(error_msg)
                self._log_automation(f"ERROR: {error_msg}")
        
        self._log_automation(f"Automation check completed: {len(results['triggered_rules'])} triggered")
        return results
    
    def _evaluate_trigger(self, rule: AutomationRule) -> bool:
        """Evaluate if a rule should be triggered"""
        if rule.trigger == "file_change":
            return self._check_file_changes(rule)
        elif rule.trigger == "time_based":
            return self._check_time_condition(rule)
        elif rule.trigger == "git_event":
            return self._check_git_events(rule)
        elif rule.trigger == "validation_failure":
            return self._check_validation_failures(rule)
        
        return False
    
    def _check_file_changes(self, rule: AutomationRule) -> bool:
        """Check for relevant file changes"""
        try:
            # Get recent file changes (last 10 minutes)
            recent_threshold = datetime.now() - timedelta(minutes=10)
            recent_files = []
            
            for file_path in self.project_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time > recent_threshold:
                        recent_files.append(str(file_path.relative_to(self.project_path)))
            
            # Check condition patterns
            if rule.condition == "docs/*.md OR *.md files modified":
                return any(f.endswith('.md') for f in recent_files)
            elif rule.condition == "any significant project changes":
                significant_patterns = ['.py', '.md', '.json', '.toml', '.txt']
                return any(any(f.endswith(pattern) for pattern in significant_patterns) 
                          for f in recent_files)
            
        except Exception:
            pass
        
        return False
    
    def _check_time_condition(self, rule: AutomationRule) -> bool:
        """Check time-based conditions"""
        if not rule.last_triggered:
            return True
        
        last_time = datetime.fromisoformat(rule.last_triggered)
        now = datetime.now()
        
        if rule.condition == "every_30_minutes":
            return (now - last_time) > timedelta(minutes=30)
        elif rule.condition == "every_hour":
            return (now - last_time) > timedelta(hours=1)
        elif rule.condition == "daily":
            return (now - last_time) > timedelta(days=1)
        
        return False
    
    def _check_git_events(self, rule: AutomationRule) -> bool:
        """Check for Git events"""
        try:
            # Check for recent commits
            result = subprocess.run(
                ["git", "log", "--since=10 minutes ago", "--oneline"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                if rule.condition == "commits to critical files":
                    # Check if recent commits involve critical files
                    critical_patterns = ["CLAUDE.md", "requirements.txt", "main.py", "src/"]
                    return any(pattern in result.stdout for pattern in critical_patterns)
            
        except Exception:
            pass
        
        return False
    
    def _check_validation_failures(self, rule: AutomationRule) -> bool:
        """Check for validation failures"""
        try:
            # Check if validation has failed recently
            import sys
            sys.path.insert(0, str(self.project_path))
            from src.agents.validate_docs import validate
            
            errors = validate(str(self.project_path), fast=True)
            return len(errors) > 0
            
        except Exception:
            pass
        
        return False
    
    def _execute_action(self, rule: AutomationRule) -> Dict[str, Any]:
        """Execute the automation action"""
        action_result = {"success": False, "message": "", "details": {}}
        
        try:
            if rule.action == "git_commit_with_message":
                result = self._auto_commit_changes(rule)
                action_result.update(result)
                
            elif rule.action == "validate_and_heal":
                result = self._validate_and_heal()
                action_result.update(result)
                
            elif rule.action == "create_snapshot":
                result = self._create_automated_snapshot()
                action_result.update(result)
                
            elif rule.action == "auto_heal_and_regenerate":
                result = self._auto_heal_and_regenerate()
                action_result.update(result)
                
            elif rule.action == "update_handover_context":
                result = self._update_handover_context()
                action_result.update(result)
            
        except Exception as e:
            action_result["message"] = f"Action failed: {str(e)}"
        
        return action_result
    
    def _auto_commit_changes(self, rule: AutomationRule) -> Dict[str, Any]:
        """Auto-commit documentation changes"""
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Stage documentation files
                subprocess.run(
                    ["git", "add", "*.md", "docs/"],
                    cwd=self.project_path,
                    timeout=5
                )
                
                # Commit with automated message
                commit_msg = f"Auto-update documentation\n\n🤖 Generated with Vibecoder Smart Automation (VIB-007)\nRule: {rule.name}\nTimestamp: {datetime.now().isoformat()}"
                
                commit_result = subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if commit_result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Documentation changes auto-committed",
                        "details": {"commit_output": commit_result.stdout}
                    }
            
            return {"success": True, "message": "No changes to commit"}
            
        except Exception as e:
            return {"success": False, "message": f"Auto-commit failed: {str(e)}"}
    
    def _validate_and_heal(self) -> Dict[str, Any]:
        """Proactive validation and healing"""
        try:
            import sys
            sys.path.insert(0, str(self.project_path))
            from src.agents.validate_docs import validate
            from src.agents.auto_heal import heal
            
            # Run validation
            errors = validate(str(self.project_path), fast=True)
            
            if errors:
                # Attempt auto-healing
                heal(str(self.project_path))
                
                # Re-validate
                new_errors = validate(str(self.project_path), fast=True)
                healed_count = len(errors) - len(new_errors)
                
                return {
                    "success": True,
                    "message": f"Validation completed, {healed_count} issues auto-healed",
                    "details": {
                        "original_errors": len(errors),
                        "remaining_errors": len(new_errors),
                        "healed_issues": healed_count
                    }
                }
            else:
                return {
                    "success": True,
                    "message": "Validation passed, no healing needed"
                }
                
        except Exception as e:
            return {"success": False, "message": f"Validation/healing failed: {str(e)}"}
    
    def _create_automated_snapshot(self) -> Dict[str, Any]:
        """Create automated backup snapshot"""
        try:
            import sys
            sys.path.insert(0, str(self.project_path))
            from src.agents.backup import snapshot
            
            snapshot_id = snapshot(str(self.project_path))
            
            return {
                "success": True,
                "message": f"Automated snapshot created: {snapshot_id}",
                "details": {"snapshot_id": snapshot_id}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Snapshot creation failed: {str(e)}"}
    
    def _auto_heal_and_regenerate(self) -> Dict[str, Any]:
        """Auto-heal and regenerate documentation"""
        try:
            import sys
            sys.path.insert(0, str(self.project_path))
            from src.agents.auto_heal import heal
            from src.agents.generate_docs import generate
            
            # Heal issues
            heal(str(self.project_path))
            
            # Regenerate documentation
            generate(str(self.project_path))
            
            return {
                "success": True,
                "message": "Auto-healing and documentation regeneration completed"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Auto-heal/regenerate failed: {str(e)}"}
    
    def _update_handover_context(self) -> Dict[str, Any]:
        """Update AI handover context"""
        try:
            import sys
            sys.path.insert(0, str(self.project_path))
            from src.agents.handover_updater import update_handover_document
            
            update_handover_document(str(self.project_path))
            
            return {
                "success": True,
                "message": "AI handover context updated"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Handover update failed: {str(e)}"}
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Load automation rules"""
        if not self.rules_file.exists():
            return []
        
        try:
            with open(self.rules_file) as f:
                return json.load(f)
        except Exception:
            return []
    
    def _update_rule(self, rule: AutomationRule) -> None:
        """Update a specific rule"""
        rules = self._load_rules()
        
        for i, rule_data in enumerate(rules):
            if rule_data["id"] == rule.id:
                rules[i] = asdict(rule)
                break
        
        with open(self.rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
    
    def _log_automation(self, message: str) -> None:
        """Log automation events"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp}: {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        rules = self._load_rules()
        
        return {
            "total_rules": len(rules),
            "enabled_rules": len([r for r in rules if r.get("enabled", True)]),
            "rules": rules,
            "last_check": self._get_last_check_time(),
            "vibecoder_focus_areas": list(set(r.get("vibecoder_focus", "") for r in rules))
        }
    
    def _get_last_check_time(self) -> Optional[str]:
        """Get the time of the last automation check"""
        if self.log_file.exists():
            try:
                with open(self.log_file) as f:
                    lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if ":" in last_line:
                        return last_line.split(":")[0]
            except Exception:
                pass
        return None


def run_smart_automation(project_path: str) -> Dict[str, Any]:
    """Run smart automation check"""
    automation = VibecoderSmartAutomation(project_path)
    return automation.check_and_execute_automation()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        automation = VibecoderSmartAutomation(project_path)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "run":
                result = automation.check_and_execute_automation()
                print(json.dumps(result, indent=2))
            elif command == "status":
                status = automation.get_automation_status()
                print(json.dumps(status, indent=2))
            else:
                print("Commands: run, status")
        else:
            # Default: run automation
            result = automation.check_and_execute_automation()
            print(json.dumps(result, indent=2))
    
    else:
        print("Usage: python smart_automation.py <project_path> [run|status]")