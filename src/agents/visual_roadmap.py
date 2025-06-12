#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Visual Roadmap Generator (VIB-009)
ASCII art roadmap visualization for Vibecoders to see progress and plan features visually
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class VisualMilestone:
    """Visual representation of a milestone"""
    id: str
    title: str
    status: str
    priority: str
    focus: str
    dependencies: List[str]
    progress_icon: str
    color_code: str


class VibecoderVisualRoadmap:
    """Generate beautiful ASCII art roadmaps for Vibecoder projects"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.roadmap_file = self.project_path / ".goldminer" / "vibecoder_roadmap.json"
        
        # Visual elements
        self.status_icons = {
            "completed": "✅",
            "in_progress": "🔄", 
            "planned": "📋",
            "blocked": "🚫"
        }
        
        self.priority_icons = {
            "critical": "🔥",
            "high": "⚡",
            "medium": "📌",
            "low": "💡"
        }
        
        self.focus_colors = {
            "core_pipeline": "🔵",
            "security_integrity": "🔒",
            "ai_handover": "🤖",
            "workflow_automation": "⚙️",
            "monitoring_observability": "📊",
            "developer_experience": "👨‍💻",
            "documentation": "📚",
            "backup_recovery": "💾"
        }
        
        self.sprint_icons = {
            "Foundation Phase": "🏗️",
            "Enhancement Phase": "🚀",
            "Production Phase": "🏭",
            "Optimization Phase": "⚡"
        }
    
    def generate_visual_roadmap(self, style: str = "timeline") -> str:
        """Generate visual roadmap in specified style"""
        roadmap_data = self._load_roadmap_data()
        
        if style == "timeline":
            return self._generate_timeline_view(roadmap_data)
        elif style == "tree":
            return self._generate_tree_view(roadmap_data)
        elif style == "progress":
            return self._generate_progress_view(roadmap_data)
        elif style == "grid":
            return self._generate_grid_view(roadmap_data)
        else:
            return self._generate_overview(roadmap_data)
    
    def _generate_timeline_view(self, roadmap_data: Dict[str, Any]) -> str:
        """Generate timeline-style roadmap"""
        milestones = self._get_visual_milestones(roadmap_data)
        current_sprint = roadmap_data.get("current_sprint", "Unknown")
        
        output = []
        output.append("🎯 VIBECODER ROADMAP - TIMELINE VIEW")
        output.append("=" * 50)
        output.append(f"{self.sprint_icons.get(current_sprint, '📋')} Current Sprint: {current_sprint}")
        output.append("")
        
        # Group by status for timeline
        completed = [m for m in milestones if m.status == "completed"]
        in_progress = [m for m in milestones if m.status == "in_progress"]
        planned = [m for m in milestones if m.status == "planned"]
        
        # Timeline sections
        if completed:
            output.append("🎉 COMPLETED MILESTONES:")
            output.append("─" * 30)
            for milestone in completed:
                line = f"{milestone.progress_icon} {milestone.id}: {milestone.title}"
                if milestone.focus:
                    line += f" {self.focus_colors.get(milestone.focus, '⚪')}"
                output.append(line)
            output.append("")
        
        if in_progress:
            output.append("🔄 CURRENT WORK:")
            output.append("─" * 20)
            for milestone in in_progress:
                line = f"{milestone.progress_icon} {milestone.id}: {milestone.title}"
                line += f" {self.priority_icons.get(milestone.priority, '📌')}"
                if milestone.focus:
                    line += f" {self.focus_colors.get(milestone.focus, '⚪')}"
                output.append(line)
            output.append("")
        
        if planned:
            output.append("📋 PLANNED MILESTONES:")
            output.append("─" * 25)
            for milestone in planned:
                deps_str = ""
                if milestone.dependencies:
                    deps_str = f" (depends: {', '.join(milestone.dependencies)})"
                line = f"{milestone.progress_icon} {milestone.id}: {milestone.title}{deps_str}"
                line += f" {self.priority_icons.get(milestone.priority, '📌')}"
                if milestone.focus:
                    line += f" {self.focus_colors.get(milestone.focus, '⚪')}"
                output.append(line)
        
        return "\n".join(output)
    
    def _generate_tree_view(self, roadmap_data: Dict[str, Any]) -> str:
        """Generate dependency tree view"""
        milestones = self._get_visual_milestones(roadmap_data)
        
        output = []
        output.append("🌳 VIBECODER ROADMAP - DEPENDENCY TREE")
        output.append("=" * 45)
        output.append("")
        
        # Build dependency tree
        milestone_dict = {m.id: m for m in milestones}
        roots = [m for m in milestones if not m.dependencies or all(dep not in milestone_dict for dep in m.dependencies)]
        
        def print_tree(milestone: VisualMilestone, indent: int = 0, printed: set = None):
            if printed is None:
                printed = set()
            
            if milestone.id in printed:
                return []
            
            printed.add(milestone.id)
            prefix = "  " * indent + ("├─ " if indent > 0 else "")
            
            line = f"{prefix}{milestone.progress_icon} {milestone.id}: {milestone.title}"
            line += f" {self.priority_icons.get(milestone.priority, '📌')}"
            if milestone.focus:
                line += f" {self.focus_colors.get(milestone.focus, '⚪')}"
            
            result = [line]
            
            # Find children (milestones that depend on this one)
            children = [m for m in milestones if milestone.id in m.dependencies]
            for child in children:
                result.extend(print_tree(child, indent + 1, printed))
            
            return result
        
        for root in roots:
            output.extend(print_tree(root))
            output.append("")
        
        return "\n".join(output)
    
    def _generate_progress_view(self, roadmap_data: Dict[str, Any]) -> str:
        """Generate progress dashboard view"""
        milestones = self._get_visual_milestones(roadmap_data)
        
        total = len(milestones)
        completed = len([m for m in milestones if m.status == "completed"])
        in_progress = len([m for m in milestones if m.status == "in_progress"])
        planned = len([m for m in milestones if m.status == "planned"])
        
        progress_percentage = (completed / total * 100) if total > 0 else 0
        
        output = []
        output.append("📊 VIBECODER ROADMAP - PROGRESS DASHBOARD")
        output.append("=" * 50)
        output.append("")
        
        # Progress bar
        bar_length = 30
        filled_length = int(bar_length * completed // total) if total > 0 else 0
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        output.append(f"Overall Progress: [{bar}] {progress_percentage:.1f}%")
        output.append("")
        
        # Statistics
        output.append("📈 MILESTONE STATISTICS:")
        output.append("─" * 25)
        output.append(f"✅ Completed:   {completed:2d}/{total}")
        output.append(f"🔄 In Progress: {in_progress:2d}/{total}")
        output.append(f"📋 Planned:     {planned:2d}/{total}")
        output.append("")
        
        # Focus area breakdown
        focus_stats = {}
        for milestone in milestones:
            focus = milestone.focus or "other"
            if focus not in focus_stats:
                focus_stats[focus] = {"total": 0, "completed": 0}
            focus_stats[focus]["total"] += 1
            if milestone.status == "completed":
                focus_stats[focus]["completed"] += 1
        
        output.append("🎯 FOCUS AREA PROGRESS:")
        output.append("─" * 25)
        for focus, stats in sorted(focus_stats.items()):
            icon = self.focus_colors.get(focus, "⚪")
            progress = stats["completed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            mini_bar_length = 10
            mini_filled = int(mini_bar_length * stats["completed"] // stats["total"]) if stats["total"] > 0 else 0
            mini_bar = "█" * mini_filled + "░" * (mini_bar_length - mini_filled)
            
            output.append(f"{icon} {focus:<20} [{mini_bar}] {progress:5.1f}% ({stats['completed']}/{stats['total']})")
        
        return "\n".join(output)
    
    def _generate_grid_view(self, roadmap_data: Dict[str, Any]) -> str:
        """Generate grid-style roadmap"""
        milestones = self._get_visual_milestones(roadmap_data)
        
        output = []
        output.append("📋 VIBECODER ROADMAP - GRID VIEW")
        output.append("=" * 45)
        output.append("")
        
        # Header
        header = f"{'ID':<8} {'Status':<8} {'Priority':<8} {'Focus':<20} {'Title':<30}"
        output.append(header)
        output.append("─" * len(header))
        
        # Sort milestones by ID
        sorted_milestones = sorted(milestones, key=lambda x: x.id)
        
        for milestone in sorted_milestones:
            status_icon = milestone.progress_icon
            priority_icon = self.priority_icons.get(milestone.priority, "📌")
            focus_icon = self.focus_colors.get(milestone.focus, "⚪")
            
            # Truncate title if too long
            title = milestone.title[:28] + ".." if len(milestone.title) > 30 else milestone.title
            
            row = f"{milestone.id:<8} {status_icon:<8} {priority_icon:<8} {focus_icon} {milestone.focus:<18} {title:<30}"
            output.append(row)
        
        return "\n".join(output)
    
    def _generate_overview(self, roadmap_data: Dict[str, Any]) -> str:
        """Generate comprehensive overview"""
        output = []
        output.append("🎯 VIBECODER ROADMAP - COMPLETE OVERVIEW")
        output.append("=" * 55)
        output.append("")
        
        # Add all views
        output.append(self._generate_progress_view(roadmap_data))
        output.append("\n" + "─" * 55 + "\n")
        output.append(self._generate_timeline_view(roadmap_data))
        
        return "\n".join(output)
    
    def _get_visual_milestones(self, roadmap_data: Dict[str, Any]) -> List[VisualMilestone]:
        """Convert roadmap data to visual milestones"""
        milestones = []
        
        milestone_data = roadmap_data.get("milestones", {})
        for milestone_id, data in milestone_data.items():
            visual_milestone = VisualMilestone(
                id=milestone_id,
                title=data.get("title", "Unknown"),
                status=data.get("status", "planned"),
                priority=data.get("priority", "medium"),
                focus=data.get("vibecoder_focus", ""),
                dependencies=data.get("dependencies", []),
                progress_icon=self.status_icons.get(data.get("status", "planned"), "📋"),
                color_code=self.focus_colors.get(data.get("vibecoder_focus", ""), "⚪")
            )
            milestones.append(visual_milestone)
        
        return milestones
    
    def _load_roadmap_data(self) -> Dict[str, Any]:
        """Load roadmap data from file"""
        if not self.roadmap_file.exists():
            return {"milestones": {}, "current_sprint": "Unknown"}
        
        try:
            with open(self.roadmap_file) as f:
                return json.load(f)
        except Exception:
            return {"milestones": {}, "current_sprint": "Unknown"}
    
    def generate_roadmap_html(self) -> str:
        """Generate HTML version of roadmap for web viewing"""
        roadmap_data = self._load_roadmap_data()
        milestones = self._get_visual_milestones(roadmap_data)
        
        total = len(milestones)
        completed = len([m for m in milestones if m.status == "completed"])
        progress_percentage = (completed / total * 100) if total > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>VIBECODER Roadmap</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Courier New', monospace; margin: 20px; background: #1a1a1a; color: #00ff00; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 10px; }}
        .progress-bar {{ width: 100%; height: 30px; background: #333; border: 1px solid #00ff00; margin: 20px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #00ff00, #ffff00); width: {progress_percentage}%; }}
        .milestone {{ border: 1px solid #00ff00; margin: 10px 0; padding: 15px; background: #0a0a0a; }}
        .milestone.completed {{ border-color: #00ff00; background: #002200; }}
        .milestone.in_progress {{ border-color: #ffff00; background: #222200; }}
        .milestone.planned {{ border-color: #666; background: #111; }}
        .milestone-header {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .milestone-meta {{ color: #aaa; font-size: 12px; margin-top: 10px; }}
        .focus-tag {{ display: inline-block; padding: 2px 8px; background: #333; border-radius: 3px; margin-left: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 VIBECODER ROADMAP</h1>
            <p>Visual Progress Tracking | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="progress-section">
            <h2>📊 Overall Progress: {progress_percentage:.1f}%</h2>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p>{completed}/{total} milestones completed</p>
        </div>
        
        <div class="milestones-section">
            <h2>🎯 Milestones</h2>"""
        
        # Sort milestones by ID
        sorted_milestones = sorted(milestones, key=lambda x: x.id)
        
        for milestone in sorted_milestones:
            deps_text = f" (depends: {', '.join(milestone.dependencies)})" if milestone.dependencies else ""
            
            html += f"""
            <div class="milestone {milestone.status}">
                <div class="milestone-header">
                    {milestone.progress_icon} {milestone.id}: {milestone.title}
                    <span class="focus-tag">{milestone.focus}</span>
                </div>
                <div class="milestone-meta">
                    Priority: {self.priority_icons.get(milestone.priority, '📌')} {milestone.priority.upper()}
                    {deps_text}
                </div>
            </div>"""
        
        html += """
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_roadmap_visualization(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Save all roadmap visualizations to files"""
        if output_dir is None:
            output_dir = self.project_path / "docs"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Save text visualizations
        styles = ["timeline", "tree", "progress", "grid", "overview"]
        for style in styles:
            content = self.generate_visual_roadmap(style)
            file_path = output_dir / f"roadmap_{style}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            files_created[style] = str(file_path)
        
        # Save HTML version
        html_content = self.generate_roadmap_html()
        html_path = output_dir / "roadmap.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        files_created["html"] = str(html_path)
        
        return files_created


def generate_visual_roadmap(project_path: str, style: str = "overview") -> str:
    """Generate visual roadmap for project"""
    generator = VibecoderVisualRoadmap(project_path)
    return generator.generate_visual_roadmap(style)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        style = sys.argv[2] if len(sys.argv) > 2 else "overview"
        
        generator = VibecoderVisualRoadmap(project_path)
        
        if style == "save":
            files = generator.save_roadmap_visualization()
            print("📁 Roadmap visualizations saved:")
            for style_name, file_path in files.items():
                print(f"  {style_name}: {file_path}")
        else:
            roadmap = generator.generate_visual_roadmap(style)
            print(roadmap)
    
    else:
        print("Usage: python visual_roadmap.py <project_path> [timeline|tree|progress|grid|overview|save]")