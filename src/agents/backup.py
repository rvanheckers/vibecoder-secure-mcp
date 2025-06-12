#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Backup Agent
"""

import os
import shutil
import json
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


def snapshot(project_path: str) -> str:
    """
    Create a backup snapshot of the project.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Snapshot ID
    """
    project_dir = Path(project_path)
    backup_dir = project_dir / ".goldminer" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate snapshot ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    
    # Create snapshot directory
    snapshot_dir = backup_dir / snapshot_id
    snapshot_dir.mkdir(exist_ok=True)
    
    # Define directories/files to backup
    backup_targets = [
        "docs",
        "src",
        ".goldminer/manifest.json",
        ".goldminer/config.yml",
        "goldminer.toml",
        "goldminer.lock",
        "ai-plugin.json",
        "requirements.txt",
        "Makefile"
    ]
    
    # Create backup
    backup_manifest = {
        "snapshot_id": snapshot_id,
        "timestamp": datetime.now().isoformat(),
        "project_path": str(project_dir),
        "files": []
    }
    
    for target in backup_targets:
        source_path = project_dir / target
        if source_path.exists():
            try:
                if source_path.is_file():
                    # Copy single file
                    dest_path = snapshot_dir / target
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    
                    backup_manifest["files"].append({
                        "path": target,
                        "type": "file",
                        "size": source_path.stat().st_size,
                        "hash": _compute_file_hash(source_path)
                    })
                    
                elif source_path.is_dir():
                    # Copy directory recursively
                    dest_path = snapshot_dir / target
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    
                    # Add directory contents to manifest
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            rel_path = target + "/" + str(file_path.relative_to(source_path))
                            backup_manifest["files"].append({
                                "path": rel_path,
                                "type": "file",
                                "size": file_path.stat().st_size,
                                "hash": _compute_file_hash(file_path)
                            })
                            
            except Exception as e:
                print(f"Warning: Could not backup {target}: {e}")
    
    # Write backup manifest
    manifest_path = snapshot_dir / "backup_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(backup_manifest, f, indent=2)
    
    # Create compressed archive
    archive_path = backup_dir / f"{snapshot_id}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(snapshot_dir, arcname=snapshot_id)
    
    # Remove uncompressed snapshot directory
    shutil.rmtree(snapshot_dir)
    
    # Update backup index
    _update_backup_index(backup_dir, snapshot_id, backup_manifest)
    
    print(f"Snapshot created: {snapshot_id}")
    print(f"Archive: {archive_path}")
    
    return snapshot_id


def restore(snapshot_id: str, project_path: Optional[str] = None) -> bool:
    """
    Restore from a backup snapshot.
    
    Args:
        snapshot_id: ID of the snapshot to restore
        project_path: Target project path (defaults to current directory)
        
    Returns:
        True if restore was successful
    """
    if not project_path:
        project_path = os.getcwd()
    
    project_dir = Path(project_path)
    backup_dir = project_dir / ".goldminer" / "backups"
    
    # Find snapshot archive
    archive_path = backup_dir / f"{snapshot_id}.tar.gz"
    if not archive_path.exists():
        print(f"Snapshot not found: {snapshot_id}")
        return False
    
    try:
        # Extract snapshot
        temp_dir = backup_dir / "temp_restore"
        temp_dir.mkdir(exist_ok=True)
        
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(temp_dir)
        
        snapshot_dir = temp_dir / snapshot_id
        
        # Read backup manifest
        manifest_path = snapshot_dir / "backup_manifest.json"
        if not manifest_path.exists():
            print("Invalid snapshot: missing manifest")
            return False
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Confirm restore with user
        print(f"Restoring snapshot: {snapshot_id}")
        print(f"Created: {manifest['timestamp']}")
        print(f"Files: {len(manifest['files'])}")
        
        response = input("Continue with restore? (y/N): ")
        if response.lower() != 'y':
            print("Restore cancelled")
            shutil.rmtree(temp_dir)
            return False
        
        # Perform restore
        restored_count = 0
        for file_info in manifest["files"]:
            source_path = snapshot_dir / file_info["path"]
            dest_path = project_dir / file_info["path"]
            
            if source_path.exists():
                try:
                    # Create parent directories
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    
                    # Verify integrity
                    if _compute_file_hash(dest_path) == file_info["hash"]:
                        restored_count += 1
                    else:
                        print(f"Warning: Hash mismatch for {file_info['path']}")
                        
                except Exception as e:
                    print(f"Error restoring {file_info['path']}: {e}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print(f"Restore completed: {restored_count}/{len(manifest['files'])} files")
        return restored_count == len(manifest["files"])
        
    except Exception as e:
        print(f"Error during restore: {e}")
        return False


def list_snapshots(project_path: str) -> List[Dict[str, Any]]:
    """
    List available backup snapshots.
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        List of snapshot information
    """
    project_dir = Path(project_path)
    backup_dir = project_dir / ".goldminer" / "backups"
    
    if not backup_dir.exists():
        return []
    
    # Read backup index
    index_path = backup_dir / "backup_index.json"
    if not index_path.exists():
        return []
    
    try:
        with open(index_path) as f:
            index = json.load(f)
        
        return index.get("snapshots", [])
        
    except Exception as e:
        print(f"Error reading backup index: {e}")
        return []


def cleanup_old_snapshots(project_path: str, keep_count: int = 10) -> int:
    """
    Clean up old backup snapshots, keeping only the most recent ones.
    
    Args:
        project_path: Path to the project directory
        keep_count: Number of snapshots to keep
        
    Returns:
        Number of snapshots removed
    """
    snapshots = list_snapshots(project_path)
    
    if len(snapshots) <= keep_count:
        return 0
    
    # Sort by timestamp (newest first)
    snapshots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Remove old snapshots
    project_dir = Path(project_path)
    backup_dir = project_dir / ".goldminer" / "backups"
    removed_count = 0
    
    for snapshot in snapshots[keep_count:]:
        snapshot_id = snapshot["snapshot_id"]
        archive_path = backup_dir / f"{snapshot_id}.tar.gz"
        
        try:
            if archive_path.exists():
                archive_path.unlink()
                removed_count += 1
                print(f"Removed old snapshot: {snapshot_id}")
                
        except Exception as e:
            print(f"Error removing snapshot {snapshot_id}: {e}")
    
    # Update backup index
    if removed_count > 0:
        remaining_snapshots = snapshots[:keep_count]
        _write_backup_index(backup_dir, remaining_snapshots)
    
    return removed_count


def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file"""
    hasher = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def _update_backup_index(backup_dir: Path, snapshot_id: str, manifest: Dict[str, Any]) -> None:
    """Update backup index with new snapshot"""
    index_path = backup_dir / "backup_index.json"
    
    # Read existing index
    if index_path.exists():
        try:
            with open(index_path) as f:
                index = json.load(f)
        except Exception:
            index = {"snapshots": []}
    else:
        index = {"snapshots": []}
    
    # Add new snapshot
    snapshot_info = {
        "snapshot_id": snapshot_id,
        "timestamp": manifest["timestamp"],
        "file_count": len(manifest["files"]),
        "total_size": sum(f.get("size", 0) for f in manifest["files"])
    }
    
    index["snapshots"].append(snapshot_info)
    
    # Write updated index
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def _write_backup_index(backup_dir: Path, snapshots: List[Dict[str, Any]]) -> None:
    """Write backup index"""
    index = {"snapshots": snapshots}
    index_path = backup_dir / "backup_index.json"
    
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python backup.py <project_path> <command> [args...]")
        print("Commands:")
        print("  snapshot             - Create new snapshot")
        print("  restore <snapshot_id> - Restore from snapshot")  
        print("  list                 - List available snapshots")
        print("  cleanup [keep_count] - Clean up old snapshots")
        sys.exit(1)
    
    project_path = sys.argv[1]
    command = sys.argv[2]
    
    if command == "snapshot":
        snapshot_id = snapshot(project_path)
        print(f"Created snapshot: {snapshot_id}")
        
    elif command == "restore":
        if len(sys.argv) < 4:
            print("Error: snapshot_id required for restore")
            sys.exit(1)
        
        snapshot_id = sys.argv[3]
        success = restore(snapshot_id, project_path)
        sys.exit(0 if success else 1)
        
    elif command == "list":
        snapshots = list_snapshots(project_path)
        if snapshots:
            print("Available snapshots:")
            for snapshot in snapshots:
                print(f"  {snapshot['snapshot_id']} - {snapshot['timestamp']} ({snapshot['file_count']} files)")
        else:
            print("No snapshots found")
            
    elif command == "cleanup":
        keep_count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        removed = cleanup_old_snapshots(project_path, keep_count)
        print(f"Removed {removed} old snapshots")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)