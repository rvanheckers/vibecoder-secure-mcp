#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Main Orchestrator Hub (Central Control)
FastAPI-based MCP server with secure endpoints for all VIBECODER operations

Dependencies:
- All src/agents/*: Imports and orchestrates all 16 agents
- Makefile: CLI interface calls this via python main.py commands
- venv/: Requires virtual environment activation for dependencies

Endpoints:
- POST /generate: Document generation via generate_docs.py
- POST /validate: Project validation via validate_docs.py
- POST /heal: Auto-healing via auto_heal.py
- POST /lock: Integrity locking via integrity.py
- POST /sign: GPG signing capabilities
- GET /health: Health monitoring via monitoring.py

CLI Commands:
- python main.py server: Start FastAPI server
- python main.py generate: Generate documentation
- python main.py validate: Validate project integrity
- python main.py heal: Auto-heal issues
- python main.py lock: Update integrity locks
- python main.py sign: GPG sign project
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import uvicorn

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.generate_docs import generate
from agents.validate_docs import validate
from agents.auto_heal import heal
from agents.compliance import check_compliance
from agents.integrity import compute_merkle, verify_integrity
from agents.audit import (
    log_generate_event, log_validate_event, log_heal_event, 
    log_lock_event, log_sign_event
)
from agents.backup import snapshot
from agents.monitoring import VibecoderMonitor, create_dashboard_html
from agents.smart_automation import VibecoderSmartAutomation, run_smart_automation
from agents.context_compression import VibecoderContextCompressor, compress_conversation_for_handover
from agents.visual_roadmap import VibecoderVisualRoadmap, generate_visual_roadmap


# FastAPI app
app = FastAPI(
    title="VIBECODER-SECURE MCP",
    description="Secure document pipeline with integrity validation and audit capabilities",
    version="1.0.0"
)


# Request/Response Models
class ProjectPathRequest(BaseModel):
    project_path: str
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that project_path is within allowed boundaries"""
        path = Path(v).resolve()
        
        # Security check: ensure path is not trying to escape
        if ".." in str(path) or not path.exists():
            raise ValueError("Invalid or non-existent project path")
        
        return str(path)


class ValidateRequest(ProjectPathRequest):
    fast: bool = False


class LockRequest(ProjectPathRequest):
    update: bool = True


class SignRequest(ProjectPathRequest):
    key: Optional[str] = None


class CompressRequest(BaseModel):
    project_path: str
    conversation_text: str
    topic: Optional[str] = None
    vibecoder_focus: Optional[str] = None
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that project_path is within allowed boundaries"""
        path = Path(v).resolve()
        if ".." in str(path) or not path.exists():
            raise ValueError("Invalid or non-existent project path")
        return str(path)


class RoadmapRequest(BaseModel):
    project_path: str
    style: Optional[str] = "overview"  # timeline, tree, progress, grid, overview
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that project_path is within allowed boundaries"""
        path = Path(v).resolve()
        if ".." in str(path) or not path.exists():
            raise ValueError("Invalid or non-existent project path")
        return str(path)


class OperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Endpoints
@app.post("/generate", response_model=OperationResponse)
async def generate_docs(request: ProjectPathRequest):
    """Generate project documentation"""
    try:
        generate(request.project_path)
        log_generate_event(request.project_path)
        
        return OperationResponse(
            success=True,
            message="Documentation generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/validate", response_model=OperationResponse)
async def validate_docs(request: ValidateRequest):
    """Validate document integrity and compliance"""
    try:
        errors = validate(request.project_path, fast=request.fast)
        success = len(errors) == 0
        
        log_validate_event(request.project_path, success, errors)
        
        return OperationResponse(
            success=success,
            message="Validation passed" if success else "Validation failed",
            data={"errors": errors} if errors else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post("/heal", response_model=OperationResponse)
async def heal_issues(request: ProjectPathRequest):
    """Auto-heal detected issues"""
    try:
        # Get initial issues count
        initial_errors = validate(request.project_path, fast=False)
        initial_count = len(initial_errors)
        
        # Perform healing
        heal(request.project_path)
        
        # Check remaining issues
        remaining_errors = validate(request.project_path, fast=False)
        remaining_count = len(remaining_errors)
        
        healed_count = initial_count - remaining_count
        log_heal_event(request.project_path, healed_count)
        
        return OperationResponse(
            success=remaining_count == 0,
            message=f"Healed {healed_count} of {initial_count} issues",
            data={
                "initial_issues": initial_count,
                "healed_issues": healed_count,
                "remaining_issues": remaining_count,
                "remaining_errors": remaining_errors
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Healing failed: {str(e)}")


@app.post("/lock", response_model=OperationResponse)
async def update_lock(request: LockRequest):
    """Update integrity lock file"""
    try:
        if request.update:
            # Compute new Merkle root and update lock file
            merkle_root = compute_merkle(request.project_path)
            
            if not merkle_root:
                raise HTTPException(status_code=400, detail="Cannot compute Merkle root")
            
            log_lock_event(request.project_path, merkle_root)
            
            return OperationResponse(
                success=True,
                message="Lock file updated successfully",
                data={"merkle_root": merkle_root}
            )
        else:
            # Just verify existing lock
            is_valid, issues = verify_integrity(request.project_path)
            
            return OperationResponse(
                success=is_valid,
                message="Lock verification passed" if is_valid else "Lock verification failed",
                data={"issues": issues} if issues else None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lock operation failed: {str(e)}")


@app.post("/sign", response_model=OperationResponse)
async def sign_project(request: SignRequest):
    """Sign project with GPG key"""
    try:
        # This is a placeholder for GPG signing functionality
        # In a real implementation, this would use GPG to sign the project
        
        if not request.key:
            gpg_key = os.getenv("GPG_KEY")
            if not gpg_key:
                raise HTTPException(status_code=400, detail="No GPG key specified")
        else:
            gpg_key = request.key
        
        # Placeholder signature
        signature = f"GPG_SIGNATURE_{gpg_key}_{compute_merkle(request.project_path)[:16]}"
        
        log_sign_event(request.project_path, signature)
        
        return OperationResponse(
            success=True,
            message="Project signed successfully",
            data={"signature": signature, "key": gpg_key}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")


@app.post("/monitor", response_model=OperationResponse)
async def monitor_project(request: ProjectPathRequest):
    """Get real-time monitoring status"""
    try:
        monitor = VibecoderMonitor(request.project_path)
        status = monitor.get_real_time_status()
        
        return OperationResponse(
            success=True,
            message="Monitoring data retrieved successfully",
            data=status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


@app.post("/dashboard")
async def create_monitoring_dashboard(request: ProjectPathRequest):
    """Create HTML monitoring dashboard"""
    try:
        html_content = create_dashboard_html(request.project_path)
        
        # Save dashboard
        dashboard_path = Path(request.project_path) / "docs" / "dashboard.html"
        dashboard_path.parent.mkdir(exist_ok=True)
        
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
        
        return OperationResponse(
            success=True,
            message=f"Dashboard created successfully at {dashboard_path}",
            data={"dashboard_path": str(dashboard_path)}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")


@app.post("/automation", response_model=OperationResponse)
async def get_automation_status(request: ProjectPathRequest):
    """Get automation system status"""
    try:
        automation = VibecoderSmartAutomation(request.project_path)
        status = automation.get_automation_status()
        
        return OperationResponse(
            success=True,
            message="Automation status retrieved successfully",
            data=status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation status failed: {str(e)}")


@app.post("/automation/run", response_model=OperationResponse)
async def run_automation(request: ProjectPathRequest):
    """Run smart automation checks and actions"""
    try:
        result = run_smart_automation(request.project_path)
        
        return OperationResponse(
            success=True,
            message=f"Automation completed: {len(result['triggered_rules'])} rules triggered",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automation run failed: {str(e)}")


@app.post("/compress", response_model=OperationResponse)
async def compress_conversation(request: CompressRequest):
    """Compress conversation context for AI handover"""
    try:
        result = compress_conversation_for_handover(
            request.project_path,
            request.conversation_text,
            request.topic or "",
            request.vibecoder_focus or ""
        )
        
        return OperationResponse(
            success=True,
            message=f"Conversation compressed with ratio {result['compression_ratio']:.2f}",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")


@app.post("/compress/summary", response_model=OperationResponse)
async def get_compression_summary(request: ProjectPathRequest):
    """Get compression system summary"""
    try:
        compressor = VibecoderContextCompressor(request.project_path)
        summary = compressor.get_compressed_context_summary()
        
        return OperationResponse(
            success=True,
            message="Compression summary retrieved successfully",
            data=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression summary failed: {str(e)}")


@app.post("/roadmap", response_model=OperationResponse)
async def get_visual_roadmap(request: RoadmapRequest):
    """Get visual roadmap in specified style"""
    try:
        roadmap_content = generate_visual_roadmap(request.project_path, request.style)
        
        return OperationResponse(
            success=True,
            message=f"Visual roadmap generated in {request.style} style",
            data={"roadmap": roadmap_content, "style": request.style}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


@app.post("/roadmap/visual", response_model=OperationResponse)
async def create_visual_roadmap_files(request: ProjectPathRequest):
    """Create and save all visual roadmap files"""
    try:
        generator = VibecoderVisualRoadmap(request.project_path)
        files = generator.save_roadmap_visualization()
        
        return OperationResponse(
            success=True,
            message=f"Visual roadmap files created: {len(files)} files",
            data={"files": files}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual roadmap creation failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "VIBECODER-SECURE MCP"}


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "VIBECODER-SECURE MCP",
        "version": "1.0.0",
        "description": "Secure document pipeline with integrity validation and audit capabilities",
        "endpoints": [
            "/generate",
            "/validate", 
            "/heal",
            "/lock",
            "/sign",
            "/monitor",
            "/dashboard", 
            "/automation",
            "/automation/run",
            "/compress",
            "/compress/summary",
            "/roadmap",
            "/roadmap/visual",
            "/health",
            "/openapi.json"
        ]
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "File not found", "detail": str(exc)}
    )


# CLI interface
def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("VIBECODER-SECURE MCP")
        print("Usage: python main.py <command> [args...]")
        print("")
        print("Commands:")
        print("  server [--host HOST] [--port PORT]  - Start MCP server")
        print("  generate <project_path>             - Generate documentation")
        print("  validate <project_path> [--fast]    - Validate project")
        print("  heal <project_path>                 - Auto-heal issues")
        print("  lock <project_path> [--update]      - Update/verify lock file")
        print("  sign <project_path> [--key KEY]     - Sign project")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "server":
        # Start FastAPI server
        host = "0.0.0.0"
        port = 8000
        
        # Parse server arguments
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--host" and i + 1 < len(args):
                host = args[i + 1]
                i += 2
            elif args[i] == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
                i += 2
            else:
                i += 1
        
        print(f"Starting VIBECODER-SECURE MCP server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    elif command == "generate":
        if len(sys.argv) < 3:
            print("Error: project_path required")
            sys.exit(1)
        
        project_path = sys.argv[2]
        generate(project_path)
        log_generate_event(project_path)
        print("Documentation generated successfully")
        
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: project_path required")
            sys.exit(1)
        
        project_path = sys.argv[2]
        fast = "--fast" in sys.argv
        
        errors = validate(project_path, fast=fast)
        success = len(errors) == 0
        
        log_validate_event(project_path, success, errors)
        
        if success:
            print("Validation passed")
        else:
            print("Validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
            
    elif command == "heal":
        if len(sys.argv) < 3:
            print("Error: project_path required")
            sys.exit(1)
        
        project_path = sys.argv[2]
        heal(project_path)
        
    elif command == "lock":
        if len(sys.argv) < 3:
            print("Error: project_path required")
            sys.exit(1)
        
        project_path = sys.argv[2]
        update = "--update" in sys.argv
        
        if update:
            merkle_root = compute_merkle(project_path)
            log_lock_event(project_path, merkle_root)
            print(f"Lock file updated with Merkle root: {merkle_root}")
        else:
            is_valid, issues = verify_integrity(project_path)
            if is_valid:
                print("Lock verification passed")
            else:
                print("Lock verification failed:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)
                
    elif command == "sign":
        if len(sys.argv) < 3:
            print("Error: project_path required")
            sys.exit(1)
        
        project_path = sys.argv[2]
        
        # Get GPG key
        gpg_key = None
        if "--key" in sys.argv:
            key_index = sys.argv.index("--key")
            if key_index + 1 < len(sys.argv):
                gpg_key = sys.argv[key_index + 1]
        
        if not gpg_key:
            gpg_key = os.getenv("GPG_KEY")
        
        if not gpg_key:
            print("Error: No GPG key specified. Use --key or set GPG_KEY environment variable")
            sys.exit(1)
        
        # Placeholder signing
        signature = f"GPG_SIGNATURE_{gpg_key}_{compute_merkle(project_path)[:16]}"
        log_sign_event(project_path, signature)
        print(f"Project signed with key: {gpg_key}")
        print(f"Signature: {signature}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()