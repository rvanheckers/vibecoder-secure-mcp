#!/usr/bin/env python3
"""
VIBECODER-SECURE MCP - Deployment Validation Test
Test all deployment configurations and files
"""

import os
import yaml
import json
from pathlib import Path


def test_dockerfile():
    """Test Dockerfile syntax and content"""
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        return False, "Dockerfile not found"
    
    content = dockerfile.read_text()
    
    # Check for required elements
    required_elements = [
        "FROM python:",
        "WORKDIR /app",
        "COPY requirements.txt",
        "RUN pip install",
        "COPY . .",
        "EXPOSE 8000",
        "CMD"
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        return False, f"Missing Dockerfile elements: {missing}"
    
    return True, "Dockerfile validation passed"


def test_docker_compose():
    """Test docker-compose.yml syntax"""
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        return False, "docker-compose.yml not found"
    
    try:
        with open(compose_file) as f:
            compose_data = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ["version", "services", "volumes"]
        for section in required_sections:
            if section not in compose_data:
                return False, f"Missing {section} section in docker-compose.yml"
        
        # Check service configuration
        if "vibecoder-mcp" not in compose_data["services"]:
            return False, "vibecoder-mcp service not defined"
        
        service = compose_data["services"]["vibecoder-mcp"]
        
        # Check essential service configuration
        if "build" not in service and "image" not in service:
            return False, "Service must have either build or image configuration"
        
        if "ports" not in service:
            return False, "Service must expose ports"
        
        return True, "docker-compose.yml validation passed"
        
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {str(e)}"


def test_github_actions():
    """Test GitHub Actions workflow files"""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return False, "GitHub Actions workflows directory not found"
    
    workflow_files = list(workflows_dir.glob("*.yml"))
    if not workflow_files:
        return False, "No GitHub Actions workflow files found"
    
    for workflow_file in workflow_files:
        try:
            with open(workflow_file) as f:
                workflow_data = yaml.safe_load(f)
            
            # Check required workflow elements
            if "name" not in workflow_data:
                return False, f"Workflow {workflow_file.name} missing name"
            
            if "on" not in workflow_data:
                return False, f"Workflow {workflow_file.name} missing trigger configuration"
            
            if "jobs" not in workflow_data:
                return False, f"Workflow {workflow_file.name} missing jobs"
                
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in {workflow_file.name}: {str(e)}"
    
    return True, f"GitHub Actions validation passed ({len(workflow_files)} workflows)"


def test_production_config():
    """Test production configuration files"""
    config_files = [
        ("production.yml", "Production Docker Compose"),
        ("pyproject.toml", "Python project configuration"),
        (".env.example", "Environment template"),
        ("deploy.sh", "Deployment script")
    ]
    
    missing_files = []
    for file_path, description in config_files:
        if not Path(file_path).exists():
            missing_files.append(f"{description} ({file_path})")
    
    if missing_files:
        return False, f"Missing configuration files: {', '.join(missing_files)}"
    
    # Test production.yml syntax
    try:
        with open("production.yml") as f:
            prod_data = yaml.safe_load(f)
        
        if "services" not in prod_data:
            return False, "production.yml missing services section"
            
    except yaml.YAMLError as e:
        return False, f"Invalid production.yml syntax: {str(e)}"
    
    # Check deploy script is executable
    deploy_script = Path("deploy.sh")
    if not os.access(deploy_script, os.X_OK):
        return False, "deploy.sh is not executable"
    
    return True, "Production configuration validation passed"


def test_requirements():
    """Test requirements.txt and dependencies"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        return False, "requirements.txt not found"
    
    content = requirements_file.read_text()
    
    # Check for essential dependencies
    essential_deps = ["fastapi", "uvicorn", "pyyaml", "gitpython", "psutil"]
    missing_deps = []
    
    for dep in essential_deps:
        if dep not in content.lower():
            missing_deps.append(dep)
    
    if missing_deps:
        return False, f"Missing essential dependencies: {missing_deps}"
    
    return True, f"Requirements validation passed"


def test_deployment_integration():
    """Test integration between deployment components"""
    
    # Check if main.py has server command
    main_file = Path("main.py")
    if not main_file.exists():
        return False, "main.py not found"
    
    main_content = main_file.read_text()
    if 'command == "server"' not in main_content:
        return False, "main.py missing server command"
    
    if "uvicorn.run" not in main_content:
        return False, "main.py missing uvicorn server setup"
    
    # Check FastAPI endpoints are available
    required_endpoints = [
        "/health",
        "/generate", 
        "/validate",
        "/monitor",
        "/roadmap"
    ]
    
    missing_endpoints = []
    for endpoint in required_endpoints:
        if f'"{endpoint}"' not in main_content and f"'{endpoint}'" not in main_content:
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        return False, f"Missing FastAPI endpoints: {missing_endpoints}"
    
    return True, "Deployment integration validation passed"


def run_all_tests():
    """Run all deployment tests"""
    tests = [
        ("Dockerfile", test_dockerfile),
        ("Docker Compose", test_docker_compose),
        ("GitHub Actions", test_github_actions),
        ("Production Config", test_production_config),
        ("Requirements", test_requirements),
        ("Integration", test_deployment_integration)
    ]
    
    print("🎯 VIBECODER-SECURE MCP - Deployment Validation")
    print("=" * 55)
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name:<20} {message}")
            
            if not success:
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL {test_name:<20} Exception: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 ALL DEPLOYMENT TESTS PASSED!")
        print("🚀 Ready for production deployment!")
    else:
        print("⚠️  Some deployment tests failed")
        print("🔧 Fix the issues above before deploying")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()