#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - VIBECODER Roadmap & Milestone Tracker (VIB-004)
Keeps AI agents focused on VIBECODER-specific goals and prevents project derailing

Dependencies:
- .goldminer/vibecoder_roadmap.json: Milestone data storage
- visual_roadmap.py: Provides data for visualization generation
- handover_updater.py: Updates current focus in CLAUDE.md
- main.py: Called via make roadmap and make check-focus commands

Manages:
- VIB milestone tracking (VIB-001 through VIB-013+)
- Current sprint and active milestone identification
- AI focus enforcement and derailing prevention
- Context warnings and VIBECODER-specific reminders
- Milestone dependency validation and completion tracking
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class VibecoderMilestone:
    """Vibecoder-specific milestone definition"""
    id: str
    title: str
    description: str
    status: str  # planned, in_progress, completed, blocked
    priority: str  # critical, high, medium, low
    vibecoder_focus: str  # core workflow area this impacts
    estimated_effort: str  # small, medium, large, epic
    dependencies: List[str]
    created_date: str
    target_date: Optional[str] = None
    completed_date: Optional[str] = None
    assigned_ai: Optional[str] = None
    context_notes: List[str] = None
    
    def __post_init__(self):
        if self.context_notes is None:
            self.context_notes = []


class VibecoderRoadmapManager:
    """Manages Vibecoder-focused roadmap and prevents AI derailing"""
    
    VIBECODER_FOCUS_AREAS = [
        "core_pipeline",
        "security_integrity", 
        "ai_handover",
        "workflow_automation",
        "monitoring_observability",
        "developer_experience",
        "documentation",
        "backup_recovery"
    ]
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.roadmap_file = self.project_path / ".goldminer" / "vibecoder_roadmap.json"
        self.context_file = self.project_path / ".goldminer" / "ai_context.json"
        self.roadmap_file.parent.mkdir(exist_ok=True)
        
    def load_roadmap(self) -> Dict[str, Any]:
        """Load current roadmap state"""
        if not self.roadmap_file.exists():
            return self._create_initial_roadmap()
        
        try:
            with open(self.roadmap_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading roadmap: {e}")
            return self._create_initial_roadmap()
    
    def save_roadmap(self, roadmap: Dict[str, Any]) -> None:
        """Save roadmap state"""
        roadmap["last_updated"] = datetime.now().isoformat()
        
        with open(self.roadmap_file, 'w') as f:
            json.dump(roadmap, f, indent=2)
    
    def add_milestone(self, milestone: VibecoderMilestone) -> None:
        """Add new Vibecoder milestone"""
        roadmap = self.load_roadmap()
        roadmap["milestones"][milestone.id] = asdict(milestone)
        self.save_roadmap(roadmap)
        
        # Log milestone creation
        self._log_roadmap_event("milestone_added", {
            "milestone_id": milestone.id,
            "title": milestone.title,
            "vibecoder_focus": milestone.vibecoder_focus
        })
    
    def start_milestone(self, milestone_id: str) -> None:
        """Start a planned milestone (change status to in_progress)"""
        roadmap = self.load_roadmap()
        
        if milestone_id not in roadmap["milestones"]:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        milestone = roadmap["milestones"][milestone_id]
        
        # Check if milestone can be started (dependencies completed)
        for dep_id in milestone.get("dependencies", []):
            if dep_id in roadmap["milestones"]:
                dep_status = roadmap["milestones"][dep_id]["status"]
                if dep_status != "completed":
                    raise ValueError(f"Cannot start {milestone_id}: dependency {dep_id} not completed")
        
        # Set other milestones to planned (only one active at a time)
        for mid, ms in roadmap["milestones"].items():
            if ms["status"] == "in_progress":
                ms["status"] = "planned"
        
        # Start this milestone
        milestone["status"] = "in_progress"
        milestone["assigned_ai"] = "Claude Code"
        
        self.save_roadmap(roadmap)
        
        # Log milestone start
        self._log_roadmap_event("milestone_started", {
            "milestone_id": milestone_id,
            "title": milestone["title"],
            "vibecoder_focus": milestone["vibecoder_focus"]
        })

    def update_milestone_status(self, milestone_id: str, status: str, notes: str = "") -> None:
        """Update milestone status with context preservation"""
        roadmap = self.load_roadmap()
        
        if milestone_id not in roadmap["milestones"]:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        milestone = roadmap["milestones"][milestone_id]
        old_status = milestone["status"]
        milestone["status"] = status
        
        if status == "completed":
            milestone["completed_date"] = datetime.now().isoformat()
        
        if notes:
            milestone["context_notes"].append(f"{datetime.now().isoformat()}: {notes}")
        
        self.save_roadmap(roadmap)
        
        # Log status change
        self._log_roadmap_event("milestone_updated", {
            "milestone_id": milestone_id,
            "old_status": old_status,
            "new_status": status,
            "notes": notes
        })
    
    def get_current_focus(self) -> Dict[str, Any]:
        """Get current Vibecoder focus for AI agent"""
        roadmap = self.load_roadmap()
        
        # Find highest priority in-progress items
        in_progress = []
        next_up = []
        
        for milestone_id, milestone in roadmap["milestones"].items():
            if milestone["status"] == "in_progress":
                in_progress.append(milestone)
            elif milestone["status"] == "planned" and milestone["priority"] in ["critical", "high"]:
                next_up.append(milestone)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        in_progress.sort(key=lambda x: priority_order.get(x["priority"], 3))
        next_up.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return {
            "current_sprint": roadmap.get("current_sprint", "Foundation"),
            "active_milestones": in_progress[:3],  # Top 3 active
            "next_milestones": next_up[:2],       # Next 2 planned
            "vibecoder_focus_reminder": roadmap["vibecoder_principles"],
            "context_warnings": self._get_derailing_warnings()
        }
    
    def prevent_derailing_check(self, proposed_work: str) -> Dict[str, Any]:
        """Check if proposed work aligns with Vibecoder focus"""
        roadmap = self.load_roadmap()
        focus = self.get_current_focus()
        
        # Simple keyword matching for focus areas
        vibecoder_keywords = [
            "vibecoder", "secure", "pipeline", "integrity", "audit", 
            "handover", "roadmap", "milestone", "workflow"
        ]
        
        generic_keywords = [
            "dashboard", "ui", "frontend", "visualization", "charts",
            "database", "orm", "api", "rest", "graphql"
        ]
        
        proposed_lower = proposed_work.lower()
        
        vibecoder_score = sum(1 for kw in vibecoder_keywords if kw in proposed_lower)
        generic_score = sum(1 for kw in generic_keywords if kw in proposed_lower)
        
        is_aligned = vibecoder_score > generic_score
        
        return {
            "is_vibecoder_aligned": is_aligned,
            "vibecoder_score": vibecoder_score,
            "generic_score": generic_score,
            "recommendation": "PROCEED" if is_aligned else "RECONSIDER",
            "focus_reminder": focus["vibecoder_focus_reminder"][0] if focus["vibecoder_focus_reminder"] else "",
            "suggested_alternatives": self._suggest_vibecoder_alternatives(proposed_work) if not is_aligned else []
        }
    
    def save_ai_context(self, context_data: Dict[str, Any]) -> None:
        """Save current AI session context for handover"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "session_id": context_data.get("session_id", "unknown"),
            "current_task": context_data.get("current_task", ""),
            "completed_tasks": context_data.get("completed_tasks", []),
            "next_planned_tasks": context_data.get("next_planned_tasks", []),
            "vibecoder_focus_area": context_data.get("vibecoder_focus_area", ""),
            "key_decisions": context_data.get("key_decisions", []),
            "warnings_flags": context_data.get("warnings_flags", [])
        }
        
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
    
    def load_ai_context(self) -> Dict[str, Any]:
        """Load AI context for handover"""
        if not self.context_file.exists():
            return {}
        
        try:
            with open(self.context_file) as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _create_initial_roadmap(self) -> Dict[str, Any]:
        """Create initial Vibecoder roadmap"""
        initial_roadmap = {
            "project_name": "VIBECODER-SECURE MCP",
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_sprint": "Foundation Phase",
            "vibecoder_principles": [
                "Always focus on Vibecoder-specific workflows and needs",
                "Security and integrity are non-negotiable",
                "AI handover continuity is critical",
                "Avoid generic solutions - everything must serve Vibecoder use cases",
                "Milestone tracking prevents scope creep and derailing"
            ],
            "focus_areas": self.VIBECODER_FOCUS_AREAS,
            "milestones": {},
            "sprints": {
                "foundation": {
                    "name": "Foundation Phase",
                    "status": "in_progress",
                    "goals": [
                        "Core pipeline implementation",
                        "Security & integrity framework", 
                        "AI handover system",
                        "GitHub integration"
                    ]
                }
            }
        }
        
        # Add initial milestones
        self._add_foundation_milestones(initial_roadmap)
        return initial_roadmap
    
    def _add_foundation_milestones(self, roadmap: Dict[str, Any]) -> None:
        """Add foundation phase milestones"""
        foundation_milestones = [
            VibecoderMilestone(
                id="VIB-001",
                title="Core Pipeline & Security Framework",
                description="Complete VIBECODER-SECURE MCP core implementation with all sub-agents",
                status="completed",
                priority="critical",
                vibecoder_focus="core_pipeline",
                estimated_effort="large",
                dependencies=[],
                created_date=datetime.now().isoformat(),
                completed_date=datetime.now().isoformat()
            ),
            VibecoderMilestone(
                id="VIB-002", 
                title="AI Handover Document System",
                description="Automated CLAUDE.md updates and context preservation",
                status="completed",
                priority="critical",
                vibecoder_focus="ai_handover",
                estimated_effort="medium",
                dependencies=["VIB-001"],
                created_date=datetime.now().isoformat(),
                completed_date=datetime.now().isoformat()
            ),
            VibecoderMilestone(
                id="VIB-003",
                title="GitHub Integration & Remote Repository",
                description="GitHub repo setup, authentication, and remote sync",
                status="completed", 
                priority="high",
                vibecoder_focus="workflow_automation",
                estimated_effort="small",
                dependencies=["VIB-001", "VIB-002"],
                created_date=datetime.now().isoformat(),
                completed_date=datetime.now().isoformat()
            ),
            VibecoderMilestone(
                id="VIB-004",
                title="Vibecoder Roadmap & Milestone Tracking",
                description="Build focus-maintaining milestone system to prevent AI derailing",
                status="in_progress",
                priority="critical",
                vibecoder_focus="ai_handover", 
                estimated_effort="medium",
                dependencies=["VIB-003"],
                created_date=datetime.now().isoformat()
            )
        ]
        
        for milestone in foundation_milestones:
            roadmap["milestones"][milestone.id] = asdict(milestone)
    
    def _get_derailing_warnings(self) -> List[str]:
        """Get warnings about potential derailing"""
        return [
            "🎯 Stay focused on Vibecoder-specific workflows",
            "⚠️ Avoid generic dashboard/UI features unless directly supporting Vibecoder needs",
            "🔒 Security and integrity must be maintained in all changes",
            "📋 Update milestones and context for seamless AI handovers"
        ]
    
    def _suggest_vibecoder_alternatives(self, proposed_work: str) -> List[str]:
        """Suggest Vibecoder-aligned alternatives"""
        return [
            "Focus on Vibecoder workflow automation",
            "Enhance security and integrity features",
            "Improve AI handover mechanisms", 
            "Build Vibecoder-specific monitoring tools"
        ]
    
    def _log_roadmap_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log roadmap events for audit trail"""
        try:
            from .audit import log_event
            log_event({
                "event_type": "ROADMAP",
                "operation": event_type,
                "details": data,
                "project_path": str(self.project_path)
            })
        except ImportError:
            # Fallback logging if audit module not available
            print(f"Roadmap event: {event_type} - {data}")


def get_current_vibecoder_focus(project_path: str) -> Dict[str, Any]:
    """Quick function to get current Vibecoder focus"""
    manager = VibecoderRoadmapManager(project_path)
    return manager.get_current_focus()


def check_vibecoder_alignment(project_path: str, proposed_work: str) -> Dict[str, Any]:
    """Quick function to check if work aligns with Vibecoder focus"""
    manager = VibecoderRoadmapManager(project_path)
    return manager.prevent_derailing_check(proposed_work)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        manager = VibecoderRoadmapManager(project_path)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "focus":
                focus = manager.get_current_focus()
                print(json.dumps(focus, indent=2))
            elif command == "check" and len(sys.argv) > 3:
                work = " ".join(sys.argv[3:])
                result = manager.prevent_derailing_check(work)
                print(json.dumps(result, indent=2))
            else:
                print("Commands: focus, check <proposed_work>")
        else:
            # Show current roadmap
            roadmap = manager.load_roadmap()
            print(json.dumps(roadmap, indent=2))
    else:
        print("Usage: python vibecoder_roadmap.py <project_path> [command]")