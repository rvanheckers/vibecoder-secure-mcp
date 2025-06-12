#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Git-aware Duplicate Detection System (VIB-011)
Detects duplicate content across git-tracked files with VIBECODER focus and smart deduplication

Dependencies:
- Git repository: Uses git ls-files for tracked file detection
- file_placement.py: Suggests optimal locations for deduplicated files
- audit.py: Logs duplicate detection and resolution events

Detects:
- Exact file content duplicates across repository
- Partial content overlap with configurable similarity thresholds
- Git-aware analysis (only scans tracked files)
- VIBECODER-specific duplicate patterns and exceptions
"""

import os
import sys
import hashlib
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess


@dataclass
class DuplicateMatch:
    """Represents a duplicate content match"""
    file1: str
    file2: str
    similarity: float
    match_type: str
    content_hash: str
    line_ranges: Dict[str, Tuple[int, int]]
    recommendation: str


@dataclass
class DuplicateReport:
    """Complete duplicate detection report"""
    timestamp: str
    total_files_scanned: int
    git_tracked_files: int
    duplicates_found: int
    matches: List[DuplicateMatch]
    recommendations: List[str]
    vibecoder_focus: List[str]


class VibecoderDuplicateDetector:
    """Git-aware duplicate detection for Vibecoder workflows"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git_files = set()
        self.file_hashes = {}
        self.function_hashes = {}
        self.duplicate_matches = []
        
        # Vibecoder-specific patterns
        self.vibecoder_patterns = {
            'agent_imports': r'from\s+(agents\.|src\.agents\.)',
            'vib_comments': r'#.*VIB-\d+',
            'makefile_targets': r'^[a-zA-Z][a-zA-Z0-9_-]*:',
            'vibecoder_functions': r'def\s+(vibecoder_|vib_|check_|validate_|generate_)',
        }
        
    def get_git_tracked_files(self) -> Set[str]:
        """Get list of git-tracked files"""
        try:
            result = subprocess.run(
                ['git', 'ls-files'], 
                cwd=self.project_path,
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                files = set()
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        file_path = self.project_path / line.strip()
                        if file_path.exists() and file_path.is_file():
                            files.add(str(file_path))
                return files
            else:
                print(f"Git error: {result.stderr}")
                return set()
        except Exception as e:
            print(f"Error getting git files: {e}")
            return set()
    
    def compute_file_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Normalize whitespace for better duplicate detection
                normalized = re.sub(r'\s+', ' ', content.strip())
                return hashlib.sha256(normalized.encode()).hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return ""
    
    def extract_python_functions(self, file_path: str) -> Dict[str, str]:
        """Extract function definitions from Python files"""
        functions = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function source
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', start_line)
                    
                    lines = content.split('\n')
                    func_content = '\n'.join(lines[start_line-1:end_line])
                    
                    # Normalize function content
                    normalized = re.sub(r'\s+', ' ', func_content.strip())
                    func_hash = hashlib.sha256(normalized.encode()).hexdigest()
                    
                    functions[node.name] = {
                        'hash': func_hash,
                        'content': func_content,
                        'lines': (start_line, end_line),
                        'file': file_path
                    }
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            
        return functions
    
    def detect_similar_content(self, content1: str, content2: str) -> float:
        """Calculate content similarity between two strings"""
        # Simple similarity based on common lines
        lines1 = set(line.strip() for line in content1.split('\n') if line.strip())
        lines2 = set(line.strip() for line in content2.split('\n') if line.strip())
        
        if not lines1 or not lines2:
            return 0.0
            
        intersection = len(lines1.intersection(lines2))
        union = len(lines1.union(lines2))
        
        return intersection / union if union > 0 else 0.0
    
    def detect_vibecoder_patterns(self, file_path: str) -> List[str]:
        """Detect Vibecoder-specific patterns in files"""
        patterns_found = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern_name, pattern in self.vibecoder_patterns.items():
                if re.search(pattern, content, re.MULTILINE):
                    patterns_found.append(pattern_name)
                    
        except Exception as e:
            print(f"Error checking patterns in {file_path}: {e}")
            
        return patterns_found
    
    def generate_recommendations(self, matches: List[DuplicateMatch]) -> List[str]:
        """Generate Vibecoder-specific recommendations"""
        recommendations = []
        
        # Agent file duplicates
        agent_duplicates = [m for m in matches if 'agents/' in m.file1 and 'agents/' in m.file2]
        if agent_duplicates:
            recommendations.append(
                "🤖 Agent Duplicates: Consider creating shared utility functions in agents/__init__.py"
            )
        
        # Documentation duplicates
        doc_duplicates = [m for m in matches if any(f.endswith('.md') for f in [m.file1, m.file2])]
        if doc_duplicates:
            recommendations.append(
                "📚 Documentation Duplicates: Consider using shared templates or includes"
            )
        
        # Configuration duplicates
        config_duplicates = [m for m in matches if any(
            f.endswith(('.json', '.toml', '.yml')) for f in [m.file1, m.file2]
        )]
        if config_duplicates:
            recommendations.append(
                "⚙️ Config Duplicates: Consider centralizing configuration in goldminer.toml"
            )
        
        # High similarity functions
        high_sim = [m for m in matches if m.similarity > 0.8 and m.match_type == 'function']
        if high_sim:
            recommendations.append(
                "🔧 High Function Similarity: Consider refactoring into shared utility functions"
            )
        
        # Vibecoder-specific recommendations
        recommendations.extend([
            "🎯 Focus on Vibecoder workflow optimization",
            "🔒 Maintain security and integrity in any refactoring",
            "📋 Update AI handover documents after changes",
            "🧪 Run comprehensive tests after deduplication"
        ])
        
        return recommendations
    
    def run_detection(self) -> DuplicateReport:
        """Run complete duplicate detection analysis"""
        print("🔍 Starting Git-aware Duplicate Detection...")
        
        # Get git-tracked files
        self.git_files = self.get_git_tracked_files()
        print(f"📁 Found {len(self.git_files)} git-tracked files")
        
        # Filter for relevant file types
        relevant_files = []
        for file_path in self.git_files:
            path = Path(file_path)
            if path.suffix in ['.py', '.md', '.json', '.toml', '.yml', '.yaml', '.txt']:
                relevant_files.append(file_path)
        
        print(f"🎯 Analyzing {len(relevant_files)} relevant files")
        
        # Compute file hashes
        for file_path in relevant_files:
            file_hash = self.compute_file_hash(file_path)
            if file_hash:
                if file_hash in self.file_hashes:
                    # Exact duplicate found
                    other_file = self.file_hashes[file_hash]
                    match = DuplicateMatch(
                        file1=other_file,
                        file2=file_path,
                        similarity=1.0,
                        match_type='exact_file',
                        content_hash=file_hash,
                        line_ranges={},
                        recommendation="Consider removing duplicate file or consolidating content"
                    )
                    self.duplicate_matches.append(match)
                else:
                    self.file_hashes[file_hash] = file_path
        
        # Analyze Python functions
        python_files = [f for f in relevant_files if f.endswith('.py')]
        all_functions = {}
        
        for file_path in python_files:
            functions = self.extract_python_functions(file_path)
            for func_name, func_data in functions.items():
                func_hash = func_data['hash']
                
                if func_hash in all_functions:
                    # Duplicate function found
                    other_func = all_functions[func_hash]
                    if other_func['file'] != file_path:  # Different files
                        match = DuplicateMatch(
                            file1=other_func['file'],
                            file2=file_path,
                            similarity=1.0,
                            match_type='function',
                            content_hash=func_hash,
                            line_ranges={
                                other_func['file']: other_func['lines'],
                                file_path: func_data['lines']
                            },
                            recommendation=f"Function '{func_name}' is duplicated - consider shared utility"
                        )
                        self.duplicate_matches.append(match)
                else:
                    all_functions[func_hash] = func_data
        
        # Check for similar content (not exact duplicates)
        for i, file1 in enumerate(relevant_files):
            for file2 in relevant_files[i+1:]:
                try:
                    with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
                        content1 = f.read()
                    with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
                        content2 = f.read()
                    
                    similarity = self.detect_similar_content(content1, content2)
                    if similarity > 0.7:  # 70% similarity threshold
                        match = DuplicateMatch(
                            file1=file1,
                            file2=file2,
                            similarity=similarity,
                            match_type='similar_content',
                            content_hash=hashlib.sha256(f"{file1}{file2}".encode()).hexdigest()[:16],
                            line_ranges={},
                            recommendation=f"Files are {similarity:.1%} similar - review for consolidation"
                        )
                        self.duplicate_matches.append(match)
                        
                except Exception as e:
                    print(f"Error comparing {file1} and {file2}: {e}")
        
        # Generate report
        recommendations = self.generate_recommendations(self.duplicate_matches)
        
        vibecoder_focus = [
            "Duplicate detection focused on Vibecoder workflow optimization",
            "Git-aware analysis ensures only tracked files are considered",
            "Recommendations prioritize security and integrity maintenance",
            "Agent files and documentation receive special attention"
        ]
        
        report = DuplicateReport(
            timestamp=datetime.now().isoformat(),
            total_files_scanned=len(relevant_files),
            git_tracked_files=len(self.git_files),
            duplicates_found=len(self.duplicate_matches),
            matches=self.duplicate_matches,
            recommendations=recommendations,
            vibecoder_focus=vibecoder_focus
        )
        
        print(f"✅ Detection complete: {len(self.duplicate_matches)} duplicates found")
        return report
    
    def save_report(self, report: DuplicateReport, output_path: str) -> None:
        """Save report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"📊 Report saved to {output_path}")


def run_duplicate_detection(project_path: str) -> DuplicateReport:
    """Main entry point for duplicate detection"""
    detector = VibecoderDuplicateDetector(project_path)
    return detector.run_detection()


def main():
    """CLI entry point"""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    report = run_duplicate_detection(project_path)
    
    # Save to .goldminer directory
    goldminer_dir = Path(project_path) / ".goldminer" / "duplicate_detection"
    goldminer_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = goldminer_dir / "duplicate_report.json"
    detector = VibecoderDuplicateDetector(project_path)
    detector.save_report(report, str(report_file))
    
    print(f"\n📊 VIB-011 Duplicate Detection Report:")
    print(f"   Files scanned: {report.total_files_scanned}")
    print(f"   Duplicates found: {report.duplicates_found}")
    print(f"   Report saved: {report_file}")


if __name__ == "__main__":
    main()