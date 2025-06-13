#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Milestone Discipline Enforcer (VIB-015)
Prevents ad-hoc work by enforcing milestone-driven development discipline

Dependencies:
- vibecoder_roadmap.py: Checks current active milestones and focus
- smart_automation.py: Integrates with automation rules for enforcement
- main.py: Called via make check-focus before starting work

Enforces:
- No ad-hoc work without corresponding VIB milestone
- Current milestone focus validation before task execution
- Warning system for scope creep and derailing prevention
- TODO to milestone mapping requirements
- Automatic milestone creation suggestions for unplanned work
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class FocusViolation:
    """Represents a focus/discipline violation"""
    violation_type: str
    description: str
    severity: str  # warning, error, critical
    suggested_action: str
    suggested_milestone: Optional[str] = None

class VibecoderMilestoneDiscipline:
    """Enforces milestone-driven discipline for VIBECODER workflows"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.roadmap_file = self.project_path / ".goldminer" / "vibecoder_roadmap.json"
        
    def check_current_focus(self) -> Dict[str, Any]:
        """Check if there's a clear current milestone focus"""
        if not self.roadmap_file.exists():
            return {
                "status": "error",
                "message": "No roadmap file found - run 'make roadmap' first",
                "violations": []
            }
        
        with open(self.roadmap_file) as f:
            roadmap = json.load(f)
        
        violations = []
        active_milestones = self._get_active_milestones(roadmap)
        
        # Check 1: Must have exactly one active milestone
        if len(active_milestones) == 0:
            violations.append(FocusViolation(
                violation_type="no_active_milestone",
                description="No active milestone found - you must have a current VIB focus",
                severity="critical",
                suggested_action="Start VIB-006 (AI Context Preservation) or VIB-005 (Monitoring)",
                suggested_milestone="VIB-006"
            ))
        elif len(active_milestones) > 1:
            violations.append(FocusViolation(
                violation_type="multiple_active_milestones",
                description=f"Multiple active milestones ({len(active_milestones)}) - focus on ONE milestone at a time",
                severity="error",
                suggested_action="Complete current milestone before starting new ones"
            ))
        
        # Check 2: Validate next milestones are properly planned
        next_milestones = self._get_next_milestones(roadmap)
        if len(next_milestones) == 0:
            violations.append(FocusViolation(
                violation_type="no_planned_milestones",
                description="No planned milestones - add your TODOs as new VIB milestones",
                severity="warning",
                suggested_action="Create VIB milestones for upcoming work"
            ))
        
        return {
            "status": "pass" if len([v for v in violations if v.severity in ["error", "critical"]]) == 0 else "fail",
            "active_milestones": active_milestones,
            "next_milestones": next_milestones[:3],  # Top 3 priorities
            "violations": [self._violation_to_dict(v) for v in violations],
            "focus_guidance": self._generate_focus_guidance(active_milestones, next_milestones)
        }
    
    def suggest_milestone_for_work(self, work_description: str) -> Dict[str, Any]:
        """Suggest creating a milestone for ad-hoc work"""
        # Analyze work description to suggest VIB number and category
        categories = {
            "header": "developer_experience",
            "cleanup": "developer_experience", 
            "documentation": "documentation",
            "test": "quality_assurance",
            "fix": "bug_fix",
            "feature": "feature_development",
            "security": "security_integrity",
            "automation": "workflow_automation",
            "monitoring": "monitoring_observability"
        }
        
        # Determine category based on keywords
        work_lower = work_description.lower()
        suggested_category = "developer_experience"  # default
        
        for keyword, category in categories.items():
            if keyword in work_lower:
                suggested_category = category
                break
        
        # Get next available VIB number
        next_vib_number = self._get_next_vib_number()
        
        return {
            "suggested_vib_id": f"VIB-{next_vib_number:03d}",
            "suggested_category": suggested_category,
            "suggested_title": self._generate_milestone_title(work_description),
            "message": f"Create {f'VIB-{next_vib_number:03d}'} milestone before starting this work",
            "template": {
                "id": f"VIB-{next_vib_number:03d}",
                "title": self._generate_milestone_title(work_description),
                "description": work_description,
                "status": "planned",
                "priority": "medium",
                "vibecoder_focus": suggested_category,
                "estimated_effort": "small"
            }
        }
    
    def enforce_milestone_discipline(self, proposed_work: str) -> Dict[str, Any]:
        """Main enforcement function - call before starting any work"""
        focus_check = self.check_current_focus()
        
        if focus_check["status"] == "fail":
            return {
                "allowed": False,
                "reason": "Focus violations must be resolved first",
                "violations": focus_check["violations"],
                "guidance": "Fix focus issues before starting new work"
            }
        
        active_milestones = focus_check["active_milestones"]
        
        if len(active_milestones) == 0:
            # No active milestone - suggest creating one
            milestone_suggestion = self.suggest_milestone_for_work(proposed_work)
            return {
                "allowed": False,
                "reason": "No active milestone for this work",
                "suggestion": milestone_suggestion,
                "guidance": "Create a VIB milestone for this work first"
            }
        
        # Check if proposed work aligns with active milestone
        active_milestone = active_milestones[0]
        alignment_score = self._check_work_alignment(proposed_work, active_milestone)
        
        if alignment_score < 0.7:  # 70% alignment threshold
            return {
                "allowed": False,
                "reason": f"Work doesn't align with active milestone {active_milestone['id']}",
                "active_milestone": active_milestone,
                "alignment_score": alignment_score,
                "suggestion": self.suggest_milestone_for_work(proposed_work),
                "guidance": "Either create new milestone or focus on current milestone tasks"
            }
        
        return {
            "allowed": True,
            "active_milestone": active_milestone,
            "alignment_score": alignment_score,
            "guidance": f"Work aligns with {active_milestone['id']} - proceed with focus"
        }
    
    def _get_active_milestones(self, roadmap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get currently active milestones"""
        active = []
        for milestone in roadmap.get("milestones", {}).values():
            if milestone.get("status") == "in_progress":
                active.append(milestone)
        return active
    
    def _get_next_milestones(self, roadmap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get next planned milestones sorted by priority"""
        planned = []
        for milestone in roadmap.get("milestones", {}).values():
            if milestone.get("status") == "planned":
                planned.append(milestone)
        
        # Sort by priority: critical, high, medium, low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        planned.sort(key=lambda m: priority_order.get(m.get("priority", "low"), 3))
        
        return planned
    
    def _get_next_vib_number(self) -> int:
        """Get next available VIB number"""
        if not self.roadmap_file.exists():
            return 15
        
        with open(self.roadmap_file) as f:
            roadmap = json.load(f)
        
        existing_numbers = []
        for milestone_id in roadmap.get("milestones", {}).keys():
            if milestone_id.startswith("VIB-"):
                try:
                    num = int(milestone_id.split("-")[1])
                    existing_numbers.append(num)
                except:
                    continue
        
        return max(existing_numbers, default=14) + 1
    
    def _generate_milestone_title(self, description: str) -> str:
        """Generate a milestone title from work description"""
        # Simple title generation - first 50 chars, capitalize
        title = description.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        return title.capitalize()
    
    def _check_work_alignment(self, work: str, milestone: Dict[str, Any]) -> float:
        """Check if proposed work aligns with milestone (0-1 score)"""
        # Simple keyword matching for alignment
        work_words = set(work.lower().split())
        milestone_words = set()
        
        milestone_words.update(milestone.get("title", "").lower().split())
        milestone_words.update(milestone.get("description", "").lower().split())
        milestone_words.update([milestone.get("vibecoder_focus", "").lower()])
        
        if not milestone_words:
            return 0.0
        
        overlap = len(work_words.intersection(milestone_words))
        return min(overlap / len(work_words), 1.0) if work_words else 0.0
    
    def _violation_to_dict(self, violation: FocusViolation) -> Dict[str, Any]:
        """Convert violation to dictionary"""
        return {
            "type": violation.violation_type,
            "description": violation.description,
            "severity": violation.severity,
            "suggested_action": violation.suggested_action,
            "suggested_milestone": violation.suggested_milestone
        }
    
    def _generate_focus_guidance(self, active: List[Dict], planned: List[Dict]) -> List[str]:
        """Generate focus guidance based on current state"""
        guidance = []
        
        if len(active) == 0:
            guidance.append("🎯 START a milestone: Run 'make milestone-start VIB-006' or create new milestone")
            
        if len(active) == 1:
            milestone = active[0]
            guidance.append(f"🎯 FOCUS: Currently working on {milestone['id']} - {milestone['title']}")
            guidance.append(f"📋 Complete this milestone before starting new work")
            
        if len(planned) > 0:
            next_milestone = planned[0]
            guidance.append(f"📅 NEXT: {next_milestone['id']} - {next_milestone['title']} ({next_milestone['priority']} priority)")
        
        guidance.append("⚠️ NO AD-HOC WORK: All tasks must have corresponding VIB milestone")
        
        return guidance


def enforce_discipline(project_path: str, proposed_work: str = "") -> Dict[str, Any]:
    """Main function for milestone discipline enforcement"""
    enforcer = VibecoderMilestoneDiscipline(project_path)
    
    if proposed_work:
        return enforcer.enforce_milestone_discipline(proposed_work)
    else:
        return enforcer.check_current_focus()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        work_description = " ".join(sys.argv[1:])
        result = enforce_discipline(".", work_description)
    else:
        result = enforce_discipline(".")
    
    print(json.dumps(result, indent=2))