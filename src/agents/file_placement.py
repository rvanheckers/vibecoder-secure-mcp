#!/usr/bin/env python3
"""
VIB-012: Intelligent File Placement System
Smart file organization assistant for Vibecoder project structure
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FilePlacementSuggestion:
    """Represents a file placement suggestion"""
    current_path: str
    suggested_path: str
    confidence: float
    reason: str
    category: str
    action_required: str
    potential_conflicts: List[str]


@dataclass
class PlacementReport:
    """Complete file placement analysis report"""
    timestamp: str
    total_files_analyzed: int
    misplaced_files: int
    suggestions: List[FilePlacementSuggestion]
    project_health_score: float
    recommendations: List[str]
    vibecoder_compliance: Dict[str, Any]


class VibecoderFilePlacement:
    """Intelligent file placement for Vibecoder project structure"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.suggestions = []
        
        # Vibecoder project structure rules
        self.placement_rules = {
            # Agent files
            'agents': {
                'pattern': r'.*\.py$',
                'content_patterns': [
                    r'class.*Agent',
                    r'def\s+(generate|validate|heal|monitor)',
                    r'from\s+agents\.',
                    r'VIB-\d+.*agent'
                ],
                'target_dir': 'src/agents/',
                'description': 'Python agent implementations'
            },
            
            # HTML dashboard files
            'dashboard_html': {
                'pattern': r'.*\.(html|htm)$',
                'content_patterns': [
                    r'VIBECODER.*Dashboard',
                    r'purple.*gradient',
                    r'test.*report',
                    r'roadmap.*html'
                ],
                'target_dir': 'docs/',
                'description': 'HTML dashboard and visualization files'
            },
            
            # Configuration files
            'config': {
                'pattern': r'.*\.(json|toml|yml|yaml)$',
                'content_patterns': [
                    r'goldminer',
                    r'vibecoder',
                    r'ai-plugin',
                    r'requirements'
                ],
                'target_dir': {
                    'goldminer': '.goldminer/',
                    'vibecoder': '.goldminer/',
                    'ai-plugin': '.',
                    'requirements': '.',
                    'package': '.'
                },
                'description': 'Configuration and metadata files'
            },
            
            # Documentation files
            'documentation': {
                'pattern': r'.*\.md$',
                'content_patterns': [
                    r'# API',
                    r'# Security',
                    r'Quick.*Reference'
                ],
                'target_dir': {
                    'api': 'docs/',
                    'security': 'docs/',
                    'manual': 'docs/manual/',
                    'readme': 'docs/',
                    'reference': 'docs/manual/'
                },
                'description': 'Documentation and manual files'
            },
            
            # Critical handover documents (stay in root)
            'handover_docs': {
                'pattern': r'(CLAUDE|VIBECODER-MANUAL|README)\.md$',
                'target_dir': '.',
                'description': 'Critical AI handover documents (must stay in root)'
            },
            
            # VIB milestone files
            'vib_files': {
                'pattern': r'.*VIB-\d+.*',
                'target_dir': '.goldminer/milestones/',
                'description': 'VIB milestone-related files'
            },
            
            # Test and script files
            'scripts': {
                'pattern': r'.*(test|script|deploy).*\.py$',
                'content_patterns': [
                    r'test.*suite',
                    r'deployment.*test',
                    r'comprehensive.*test',
                    r'if __name__ == "__main__"'
                ],
                'target_dir': 'scripts/',
                'description': 'Test scripts and deployment scripts'
            },
            
            # Backup and temporary files
            'backup_temp': {
                'pattern': r'.*(backup|temp|tmp|\~|\.bak).*',
                'target_dir': '.goldminer/backups/',
                'description': 'Backup and temporary files'
            },
            
            # Log files
            'logs': {
                'pattern': r'.*\.(log|out)$',
                'target_dir': '.goldminer/logs/',
                'description': 'Log and output files'
            }
        }
        
        # Files that should NEVER be moved
        self.protected_files = {
            'CLAUDE.md',
            'VIBECODER-MANUAL.md', 
            'README.md',
            'Makefile',
            'main.py',
            'requirements.txt',
            'goldminer.toml',
            'goldminer.lock',
            'ai-plugin.json',
            '.gitignore',
            'LICENSE'
        }
        
    def analyze_file_content(self, file_path: Path) -> Dict[str, any]:
        """Analyze file content to determine optimal placement"""
        try:
            if file_path.suffix in ['.py', '.md', '.html', '.json', '.toml', '.yml', '.yaml', '.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                return {
                    'has_vib_reference': bool(re.search(r'VIB-\d+', content)),
                    'is_agent': bool(re.search(r'class.*Agent|def\s+(generate|validate|heal)', content)),
                    'is_dashboard': bool(re.search(r'dashboard|VIBECODER.*Dashboard', content, re.IGNORECASE)),
                    'is_config': bool(re.search(r'goldminer|vibecoder|config', content, re.IGNORECASE)),
                    'is_test': bool(re.search(r'test|spec|assert', content, re.IGNORECASE)),
                    'content_size': len(content),
                    'line_count': content.count('\n')
                }
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return {}
    
    def get_file_purpose(self, file_path: Path) -> Tuple[str, float]:
        """Determine file purpose and confidence level"""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        content_analysis = self.analyze_file_content(file_path)
        
        # Check against placement rules
        for category, rules in self.placement_rules.items():
            confidence = 0.0
            
            # Pattern matching
            if re.match(rules['pattern'], str(file_path), re.IGNORECASE):
                confidence += 0.3
                
            # Content pattern matching
            if 'content_patterns' in rules:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in rules['content_patterns']:
                        if re.search(pattern, content, re.IGNORECASE):
                            confidence += 0.4
                            break
                except:
                    pass
            
            # Specific file analysis
            if category == 'agents' and content_analysis.get('is_agent'):
                confidence += 0.5
            elif category == 'dashboard_html' and content_analysis.get('is_dashboard'):
                confidence += 0.5
            elif category == 'config' and content_analysis.get('is_config'):
                confidence += 0.3
            elif category == 'tests' and content_analysis.get('is_test'):
                confidence += 0.4
            elif category == 'vib_files' and content_analysis.get('has_vib_reference'):
                confidence += 0.3
                
            # Filename indicators
            if category == 'handover_docs' and name in ['claude.md', 'vibecoder-manual.md', 'readme.md']:
                confidence = 1.0  # Always keep in root
            elif category == 'backup_temp' and any(x in name for x in ['backup', 'temp', 'tmp', '.bak', '~']):
                confidence += 0.6
            elif category == 'logs' and suffix in ['.log', '.out']:
                confidence += 0.4
                
            if confidence > 0.3:
                return category, min(confidence, 1.0)
        
        return 'unknown', 0.0
    
    def suggest_placement(self, file_path: Path) -> Optional[FilePlacementSuggestion]:
        """Generate placement suggestion for a file"""
        if file_path.name in self.protected_files:
            return None  # Never suggest moving protected files
            
        category, confidence = self.get_file_purpose(file_path)
        
        if category == 'unknown' or confidence < 0.4:
            return None
            
        rules = self.placement_rules[category]
        current_path = str(file_path.relative_to(self.project_path))
        
        # Determine target directory
        target_dir = rules['target_dir']
        if isinstance(target_dir, dict):
            # Complex mapping based on file content/name
            target_dir = self._resolve_complex_target(file_path, target_dir)
        
        suggested_path = str(Path(target_dir) / file_path.name)
        
        # Check if already in correct location
        current_dir = str(file_path.parent.relative_to(self.project_path))
        if current_dir == target_dir.rstrip('/'):
            return None  # Already in correct place
            
        # Check for potential conflicts
        conflicts = []
        suggested_full_path = self.project_path / suggested_path
        if suggested_full_path.exists():
            conflicts.append(f"File already exists at {suggested_path}")
            
        # Determine action required
        if conflicts:
            action_required = "manual_review"
        elif confidence > 0.8:
            action_required = "safe_move"
        else:
            action_required = "confirm_move"
            
        reason = f"{rules['description']} (confidence: {confidence:.1%})"
        
        return FilePlacementSuggestion(
            current_path=current_path,
            suggested_path=suggested_path,
            confidence=confidence,
            reason=reason,
            category=category,
            action_required=action_required,
            potential_conflicts=conflicts
        )
    
    def _resolve_complex_target(self, file_path: Path, target_mapping: Dict[str, str]) -> str:
        """Resolve complex target directory mappings"""
        name = file_path.name.lower()
        
        for key, directory in target_mapping.items():
            if key in name:
                return directory
                
        # Default to first value if no match
        return list(target_mapping.values())[0]
    
    def scan_project_files(self) -> List[Path]:
        """Scan project for all relevant files"""
        files = []
        
        # Get all files, respecting .gitignore patterns
        ignore_patterns = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}
        
        for root, dirs, filenames in os.walk(self.project_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if not any(pattern in str(file_path) for pattern in ignore_patterns):
                    files.append(file_path)
                    
        return files
    
    def calculate_project_health_score(self, suggestions: List[FilePlacementSuggestion]) -> float:
        """Calculate project organization health score"""
        total_files = len(self.scan_project_files())
        misplaced_files = len(suggestions)
        
        if total_files == 0:
            return 1.0
            
        # Base score from organization
        organization_score = max(0, 1.0 - (misplaced_files / total_files))
        
        # Bonus for having proper structure
        structure_bonus = 0.0
        required_dirs = ['src/agents', 'docs', '.goldminer']
        for dir_path in required_dirs:
            if (self.project_path / dir_path).exists():
                structure_bonus += 0.1
                
        return min(1.0, organization_score + structure_bonus)
    
    def generate_recommendations(self, suggestions: List[FilePlacementSuggestion]) -> List[str]:
        """Generate Vibecoder-specific organization recommendations"""
        recommendations = []
        
        # Category-specific recommendations
        categories = set(s.category for s in suggestions)
        
        if 'agents' in categories:
            recommendations.append("🤖 Move agent files to src/agents/ for proper organization")
        
        if 'dashboard_html' in categories:
            recommendations.append("📊 Move HTML files to docs/ to maintain dashboard system structure")
            
        if 'config' in categories:
            recommendations.append("⚙️ Organize config files according to their purpose and scope")
            
        if 'vib_files' in categories:
            recommendations.append("🎯 Organize VIB milestone files for better tracking")
            
        if 'backup_temp' in categories:
            recommendations.append("🧹 Clean up backup/temp files to .goldminer/backups/")
            
        # General recommendations
        recommendations.extend([
            "📋 Maintain clean project structure for AI handover clarity",
            "🔒 Ensure file organization doesn't break security or integrity",
            "🎯 Follow Vibecoder-specific organization principles",
            "💾 Create backups before any bulk file moves"
        ])
        
        return recommendations
    
    def run_analysis(self) -> PlacementReport:
        """Run complete file placement analysis"""
        print("🗂️ Starting Intelligent File Placement Analysis...")
        
        files = self.scan_project_files()
        print(f"📁 Analyzing {len(files)} files...")
        
        suggestions = []
        for file_path in files:
            suggestion = self.suggest_placement(file_path)
            if suggestion:
                suggestions.append(suggestion)
                
        health_score = self.calculate_project_health_score(suggestions)
        recommendations = self.generate_recommendations(suggestions)
        
        vibecoder_compliance = {
            'structure_score': health_score,
            'misplaced_agents': len([s for s in suggestions if s.category == 'agents']),
            'misplaced_docs': len([s for s in suggestions if s.category in ['documentation', 'dashboard_html']]),
            'protected_files_safe': all(f in [s.current_path for s in suggestions] for f in self.protected_files) == False
        }
        
        report = PlacementReport(
            timestamp=datetime.now().isoformat(),
            total_files_analyzed=len(files),
            misplaced_files=len(suggestions),
            suggestions=suggestions,
            project_health_score=health_score,
            recommendations=recommendations,
            vibecoder_compliance=vibecoder_compliance
        )
        
        print(f"✅ Analysis complete: {len(suggestions)} placement suggestions")
        return report
    
    def save_report(self, report: PlacementReport, output_path: str) -> None:
        """Save placement report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"📊 Placement report saved to {output_path}")
    
    def execute_moves(self, report: PlacementReport, auto_safe: bool = False) -> None:
        """Execute file moves based on suggestions"""
        safe_moves = [s for s in report.suggestions if s.action_required == 'safe_move']
        confirm_moves = [s for s in report.suggestions if s.action_required == 'confirm_move']
        manual_moves = [s for s in report.suggestions if s.action_required == 'manual_review']
        
        if auto_safe and safe_moves:
            print(f"🚀 Auto-executing {len(safe_moves)} safe moves...")
            for suggestion in safe_moves:
                self._move_file(suggestion)
                
        if confirm_moves:
            print(f"⚠️ {len(confirm_moves)} moves need confirmation")
            for suggestion in confirm_moves:
                print(f"   {suggestion.current_path} → {suggestion.suggested_path}")
                
        if manual_moves:
            print(f"🔍 {len(manual_moves)} moves need manual review")
            for suggestion in manual_moves:
                print(f"   {suggestion.current_path} → {suggestion.suggested_path} (conflicts: {suggestion.potential_conflicts})")
    
    def _move_file(self, suggestion: FilePlacementSuggestion) -> bool:
        """Execute a single file move"""
        try:
            source = self.project_path / suggestion.current_path
            target = self.project_path / suggestion.suggested_path
            
            # Create target directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source), str(target))
            print(f"✅ Moved {suggestion.current_path} → {suggestion.suggested_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error moving {suggestion.current_path}: {e}")
            return False


def run_file_placement_analysis(project_path: str) -> PlacementReport:
    """Main entry point for file placement analysis"""
    placer = VibecoderFilePlacement(project_path)
    return placer.run_analysis()


def main():
    """CLI entry point"""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
        
    action = sys.argv[2] if len(sys.argv) > 2 else "analyze"
    
    placer = VibecoderFilePlacement(project_path)
    report = placer.run_analysis()
    
    # Save report
    goldminer_dir = Path(project_path) / ".goldminer" / "file_placement"
    goldminer_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = goldminer_dir / "placement_report.json"
    placer.save_report(report, str(report_file))
    
    print(f"\n📊 VIB-012 File Placement Report:")
    print(f"   Files analyzed: {report.total_files_analyzed}")
    print(f"   Misplaced files: {report.misplaced_files}")
    print(f"   Health score: {report.project_health_score:.1%}")
    print(f"   Report saved: {report_file}")
    
    if action == "organize":
        placer.execute_moves(report, auto_safe=True)


if __name__ == "__main__":
    main()