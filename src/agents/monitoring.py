#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Real-time Monitoring System (VIB-005 Prep)
Real-time project health dashboard for Vibecoder workflows
"""

import json
import time
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class HealthMetrics:
    """System health metrics"""
    timestamp: str
    project_status: str
    integrity_status: str
    file_count: int
    git_status: str
    last_activity: str
    memory_usage: float
    disk_usage: float


class VibecoderMonitor:
    """Real-time monitoring for Vibecoder workflows"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.metrics_dir = self.project_path / ".goldminer" / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.metrics_dir / "health_metrics.json"
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get comprehensive real-time project status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "project_health": self._check_project_health(),
            "vibecoder_focus": self._get_current_focus(),
            "integrity_status": self._check_integrity(),
            "recent_activity": self._get_recent_activity(),
            "performance_metrics": self._get_performance_metrics(),
            "alerts": self._check_alerts()
        }
        
        # Save metrics
        self._save_metrics(status)
        
        return status
    
    def _check_project_health(self) -> Dict[str, Any]:
        """Check overall project health"""
        health = {
            "status": "healthy",
            "checks": {
                "required_files": self._check_required_files(),
                "git_repository": self._check_git_status(),
                "documentation": self._check_documentation(),
                "dependencies": self._check_dependencies()
            }
        }
        
        # Determine overall health
        failed_checks = [k for k, v in health["checks"].items() if not v["status"]]
        if failed_checks:
            health["status"] = "warning" if len(failed_checks) < 2 else "critical"
            health["failed_checks"] = failed_checks
        
        return health
    
    def _get_current_focus(self) -> Dict[str, Any]:
        """Get current Vibecoder focus from roadmap"""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from src.agents.vibecoder_roadmap import get_current_vibecoder_focus
            return get_current_vibecoder_focus(str(self.project_path))
        except Exception as e:
            return {"error": f"Could not load focus: {str(e)}"}
    
    def _check_integrity(self) -> Dict[str, Any]:
        """Check project integrity"""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from src.agents.integrity import verify_integrity
            is_valid, issues = verify_integrity(str(self.project_path))
            return {
                "status": "valid" if is_valid else "invalid",
                "issues": issues,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent project activity"""
        activity = {
            "last_commit": self._get_last_commit(),
            "recent_file_changes": self._get_recent_file_changes(),
            "audit_events": self._get_recent_audit_events()
        }
        
        return activity
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            if HAS_PSUTIL:
                metrics = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage(str(self.project_path)).percent,
                    "file_count": len(list(self.project_path.rglob("*"))),
                    "project_size_mb": self._get_project_size()
                }
            else:
                metrics = {
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "disk_usage": 0,
                    "file_count": len(list(self.project_path.rglob("*"))),
                    "project_size_mb": self._get_project_size()
                }
        except Exception:
            metrics = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage": 0,
                "file_count": 0,
                "project_size_mb": 0
            }
        
        return metrics
    
    def _check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alerts that need attention"""
        alerts = []
        
        # Check for validation failures
        integrity = self._check_integrity()
        if integrity["status"] == "invalid":
            alerts.append({
                "level": "critical",
                "type": "integrity_failure",
                "message": "Project integrity validation failed",
                "details": integrity["issues"]
            })
        
        # Check for outdated documentation
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.rglob("*.md"))
            if not doc_files:
                alerts.append({
                    "level": "warning",
                    "type": "missing_docs",
                    "message": "No documentation files found",
                    "action": "Run 'make generate' to create documentation"
                })
        
        # Check Git status
        git_status = self._check_git_status()
        if not git_status["status"] and "uncommitted changes" in git_status.get("message", ""):
            alerts.append({
                "level": "info",
                "type": "uncommitted_changes",
                "message": "Uncommitted changes detected",
                "action": "Consider committing your changes"
            })
        
        return alerts
    
    def _check_required_files(self) -> Dict[str, Any]:
        """Check for required project files"""
        required_files = [
            "VIBECODER-MANUAL.md",
            "CLAUDE.md", 
            "Makefile",
            "requirements.txt",
            "main.py"
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (self.project_path / file_name).exists():
                missing_files.append(file_name)
        
        return {
            "status": len(missing_files) == 0,
            "missing_files": missing_files,
            "total_required": len(required_files)
        }
    
    def _check_git_status(self) -> Dict[str, Any]:
        """Check Git repository status"""
        git_dir = self.project_path / ".git"
        if not git_dir.exists():
            return {"status": False, "message": "Not a Git repository"}
        
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                changes = result.stdout.strip()
                return {
                    "status": True,
                    "clean": len(changes) == 0,
                    "message": "Clean working directory" if not changes else "Uncommitted changes present"
                }
            else:
                return {"status": False, "message": "Git status failed"}
        
        except Exception as e:
            return {"status": False, "message": f"Git check failed: {str(e)}"}
    
    def _check_documentation(self) -> Dict[str, Any]:
        """Check documentation status"""
        docs_dir = self.project_path / "docs"
        manual_file = self.project_path / "VIBECODER-MANUAL.md"
        claude_file = self.project_path / "CLAUDE.md"
        
        docs_exist = docs_dir.exists() and len(list(docs_dir.rglob("*.md"))) > 0
        manuals_exist = manual_file.exists() and claude_file.exists()
        
        return {
            "status": docs_exist and manuals_exist,
            "docs_directory": docs_exist,
            "manual_files": manuals_exist,
            "total_docs": len(list(self.project_path.rglob("*.md")))
        }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check if dependencies are installed"""
        requirements_file = self.project_path / "requirements.txt"
        if not requirements_file.exists():
            return {"status": False, "message": "Requirements file not found"}
        
        try:
            import fastapi
            import uvicorn
            return {"status": True, "message": "Core dependencies available"}
        except ImportError:
            return {"status": False, "message": "Core dependencies missing"}
    
    def _get_last_commit(self) -> Dict[str, Any]:
        """Get last Git commit info"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%cd", "--date=iso"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                return {
                    "hash": parts[0][:8] if len(parts) > 0 else "unknown",
                    "message": parts[1] if len(parts) > 1 else "unknown",
                    "date": parts[2] if len(parts) > 2 else "unknown"
                }
            
        except Exception:
            pass
        
        return {"hash": "unknown", "message": "unknown", "date": "unknown"}
    
    def _get_recent_file_changes(self) -> List[str]:
        """Get recently modified files"""
        try:
            recent_files = []
            current_time = time.time()
            
            for file_path in self.project_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    mod_time = file_path.stat().st_mtime
                    if (current_time - mod_time) < 3600:  # Last hour
                        recent_files.append(str(file_path.relative_to(self.project_path)))
            
            return recent_files[:10]  # Last 10 files
        
        except Exception:
            return []
    
    def _get_recent_audit_events(self) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        try:
            audit_file = self.project_path / "audit.log"
            if audit_file.exists():
                with open(audit_file) as f:
                    lines = f.readlines()
                
                # Get last 5 events
                recent_events = []
                for line in lines[-5:]:
                    try:
                        event = json.loads(line.strip())
                        recent_events.append({
                            "type": event.get("event_type", "unknown"),
                            "operation": event.get("operation", "unknown"),
                            "timestamp": event.get("timestamp", "unknown")
                        })
                    except:
                        continue
                
                return recent_events
        
        except Exception:
            pass
        
        return []
    
    def _get_project_size(self) -> float:
        """Get project size in MB"""
        try:
            total_size = 0
            for file_path in self.project_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return round(total_size / (1024 * 1024), 2)  # Convert to MB
        
        except Exception:
            return 0.0
    
    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file"""
        try:
            # Load existing metrics
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    all_metrics = json.load(f)
            else:
                all_metrics = []
            
            # Add new metrics
            all_metrics.append(metrics)
            
            # Keep last 100 entries
            if len(all_metrics) > 100:
                all_metrics = all_metrics[-100:]
            
            # Save
            with open(self.metrics_file, 'w') as f:
                json.dump(all_metrics, f, indent=2)
        
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")


def create_dashboard_html(project_path: str) -> str:
    """Create HTML dashboard for monitoring"""
    monitor = VibecoderMonitor(project_path)
    status = monitor.get_real_time_status()
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>VIBECODER-SECURE MCP Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: monospace; margin: 20px; background: #1a1a1a; color: #00ff00; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 2px solid #00ff00; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }}
        .card {{ border: 1px solid #00ff00; padding: 15px; background: #0a0a0a; }}
        .card h3 {{ margin-top: 0; color: #ffff00; }}
        .status-healthy {{ color: #00ff00; }}
        .status-warning {{ color: #ffaa00; }}
        .status-critical {{ color: #ff0000; }}
        .metric {{ margin: 5px 0; }}
        .alert {{ background: #330000; border: 1px solid #ff0000; padding: 10px; margin: 10px 0; }}
        .refresh {{ position: fixed; top: 10px; right: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 VIBECODER-SECURE MCP DASHBOARD</h1>
            <p>Real-time Project Monitoring | Last Update: {status['timestamp'][:19]}</p>
        </div>
        
        <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Project Health</h3>
                <div class="metric">Status: <span class="status-{status['project_health']['status']}">{status['project_health']['status'].upper()}</span></div>
                <div class="metric">Required Files: {'✅' if status['project_health']['checks']['required_files']['status'] else '❌'}</div>
                <div class="metric">Git Repository: {'✅' if status['project_health']['checks']['git_repository']['status'] else '❌'}</div>
                <div class="metric">Documentation: {'✅' if status['project_health']['checks']['documentation']['status'] else '❌'}</div>
            </div>
            
            <div class="card">
                <h3>🎯 Current Focus</h3>
                <div class="metric">Sprint: {status['vibecoder_focus'].get('current_sprint', 'Unknown')}</div>
                <div class="metric">Active Milestones: {len(status['vibecoder_focus'].get('active_milestones', []))}</div>
                <div class="metric">Next Milestones: {len(status['vibecoder_focus'].get('next_milestones', []))}</div>
            </div>
            
            <div class="card">
                <h3>🔒 Integrity Status</h3>
                <div class="metric">Status: <span class="status-{'healthy' if status['integrity_status']['status'] == 'valid' else 'critical'}">{status['integrity_status']['status'].upper()}</span></div>
                <div class="metric">Issues: {len(status['integrity_status'].get('issues', []))}</div>
            </div>
            
            <div class="card">
                <h3>⚡ Performance</h3>
                <div class="metric">Memory: {status['performance_metrics']['memory_percent']:.1f}%</div>
                <div class="metric">Disk: {status['performance_metrics']['disk_usage']:.1f}%</div>
                <div class="metric">Files: {status['performance_metrics']['file_count']}</div>
                <div class="metric">Size: {status['performance_metrics']['project_size_mb']} MB</div>
            </div>
        </div>
        
        {f'<div class="alert"><h3>🚨 Alerts</h3>' + ''.join([f'<div>{alert["level"].upper()}: {alert["message"]}</div>' for alert in status["alerts"]]) + '</div>' if status["alerts"] else ''}
    </div>
</body>
</html>"""
    
    return html


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        monitor = VibecoderMonitor(project_path)
        
        if len(sys.argv) > 2 and sys.argv[2] == "dashboard":
            # Create HTML dashboard
            html = create_dashboard_html(project_path)
            dashboard_file = Path(project_path) / "docs" / "dashboard.html"
            dashboard_file.parent.mkdir(exist_ok=True)
            
            with open(dashboard_file, 'w') as f:
                f.write(html)
            
            print(f"✅ Dashboard created: {dashboard_file}")
        else:
            # Show status
            status = monitor.get_real_time_status()
            print(json.dumps(status, indent=2))
    else:
        print("Usage: python monitoring.py <project_path> [dashboard]")