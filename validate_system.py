#!/usr/bin/env python3
"""
Comprehensive validation script for RAG Chatbot system.
Checks all files, configurations, and system completeness.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print result."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ MISSING {description}: {file_path}")
        return False

def check_directory_structure():
    """Check if all required directories and files exist."""
    print("🔍 Checking Project Structure...")
    print("=" * 50)
    
    checks = [
        # Root files
        ("README.md", "Main documentation"),
        ("docker-compose.yml", "Docker orchestration"),
        ("init.sql", "Database initialization"),
        ("start.sh", "Startup script"),
        ("test_system.py", "System test script"),
        (".env.example", "Environment template"),
        
        # Backend files
        ("backend/Dockerfile", "Backend container config"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/app/__init__.py", "Backend package init"),
        ("backend/app/main.py", "FastAPI application"),
        ("backend/app/models.py", "Database models"),
        ("backend/app/schemas.py", "Pydantic schemas"),
        ("backend/app/database.py", "Database connection"),
        ("backend/app/services/__init__.py", "Services package init"),
        ("backend/app/services/llm_service.py", "LLM service"),
        ("backend/app/services/mcp_client.py", "MCP client"),
        
        # MCP Server files
        ("mcp_server/Dockerfile", "MCP server container config"),
        ("mcp_server/requirements.txt", "MCP server dependencies"),
        ("mcp_server/server.py", "MCP server implementation"),
        ("mcp_server/resources/faq.txt", "FAQ content"),
        ("mcp_server/prompts/query_generate.txt", "Query generation prompt"),
        ("mcp_server/prompts/answer_generate.txt", "Answer generation prompt"),
        
        # Frontend files
        ("frontend/Dockerfile", "Frontend container config"),
        ("frontend/nginx.conf", "Nginx configuration"),
        ("frontend/index.html", "Dashboard HTML"),
        ("frontend/style.css", "Dashboard CSS"),
        ("frontend/script.js", "Dashboard JavaScript"),
    ]
    
    passed = 0
    total = len(checks)
    
    for file_path, description in checks:
        if check_file_exists(file_path, description):
            passed += 1
    
    print(f"\n📊 File Structure: {passed}/{total} files present")
    return passed == total

def check_file_contents():
    """Check critical file contents for required components."""
    print("\n🔍 Checking File Contents...")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check docker-compose.yml
    total_checks += 1
    try:
        with open("docker-compose.yml", 'r') as f:
            content = f.read()
            if all(service in content for service in ["postgres", "pgadmin", "mcp_server", "backend", "frontend"]):
                print("✅ docker-compose.yml contains all required services")
                checks_passed += 1
            else:
                print("❌ docker-compose.yml missing required services")
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
    
    # Check backend main.py
    total_checks += 1
    try:
        with open("backend/app/main.py", 'r') as f:
            content = f.read()
            if all(endpoint in content for endpoint in ["/query_generate", "/answer_generate", "/chat", "/messages"]):
                print("✅ Backend contains all required endpoints")
                checks_passed += 1
            else:
                print("❌ Backend missing required endpoints")
    except Exception as e:
        print(f"❌ Error reading backend main.py: {e}")
    
    # Check MCP server
    total_checks += 1
    try:
        with open("mcp_server/server.py", 'r') as f:
            content = f.read()
            if all(route in content for route in ["/resources/faq", "/prompts/query_generate", "/prompts/answer_generate"]):
                print("✅ MCP server contains all required routes")
                checks_passed += 1
            else:
                print("❌ MCP server missing required routes")
    except Exception as e:
        print(f"❌ Error reading MCP server.py: {e}")
    
    # Check frontend has dashboard functionality
    total_checks += 1
    try:
        with open("frontend/script.js", 'r') as f:
            content = f.read()
            if all(func in content for func in ["loadMessages", "loadStats", "searchMessages", "showMessageDetails"]):
                print("✅ Frontend contains dashboard functionality")
                checks_passed += 1
            else:
                print("❌ Frontend missing dashboard functionality")
    except Exception as e:
        print(f"❌ Error reading frontend script.js: {e}")
    
    # Check FAQ content exists
    total_checks += 1
    try:
        with open("mcp_server/resources/faq.txt", 'r') as f:
            content = f.read()
            if len(content.strip()) > 100 and "Q:" in content and "A:" in content:
                print("✅ FAQ content is properly formatted")
                checks_passed += 1
            else:
                print("❌ FAQ content is insufficient or improperly formatted")
    except Exception as e:
        print(f"❌ Error reading FAQ content: {e}")
    
    print(f"\n📊 Content Validation: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks

def check_requirements():
    """Check that all requirements files have necessary dependencies."""
    print("\n🔍 Checking Dependencies...")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Backend requirements
    total_checks += 1
    try:
        with open("backend/requirements.txt", 'r') as f:
            content = f.read()
            required = ["fastapi", "uvicorn", "sqlalchemy", "asyncpg", "langchain", "langchain-openai", "httpx"]
            if all(req in content.lower() for req in required):
                print("✅ Backend requirements contain all necessary packages")
                checks_passed += 1
            else:
                missing = [req for req in required if req not in content.lower()]
                print(f"❌ Backend requirements missing: {missing}")
    except Exception as e:
        print(f"❌ Error reading backend requirements: {e}")
    
    # MCP server requirements
    total_checks += 1
    try:
        with open("mcp_server/requirements.txt", 'r') as f:
            content = f.read()
            required = ["fastapi", "uvicorn"]
            if all(req in content.lower() for req in required):
                print("✅ MCP server requirements contain necessary packages")
                checks_passed += 1
            else:
                missing = [req for req in required if req not in content.lower()]
                print(f"❌ MCP server requirements missing: {missing}")
    except Exception as e:
        print(f"❌ Error reading MCP server requirements: {e}")
    
    print(f"\n📊 Dependencies: {checks_passed}/{total_checks} requirement files valid")
    return checks_passed == total_checks

def check_configuration():
    """Check configuration files and environment setup."""
    print("\n🔍 Checking Configuration...")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check .env.example
    total_checks += 1
    try:
        with open(".env.example", 'r') as f:
            content = f.read()
            required_vars = ["OPENAI_API_KEY", "DATABASE_URL", "MCP_SERVER_URL"]
            if all(var in content for var in required_vars):
                print("✅ .env.example contains all required variables")
                checks_passed += 1
            else:
                missing = [var for var in required_vars if var not in content]
                print(f"❌ .env.example missing variables: {missing}")
    except Exception as e:
        print(f"❌ Error reading .env.example: {e}")
    
    # Check nginx configuration
    total_checks += 1
    try:
        with open("frontend/nginx.conf", 'r') as f:
            content = f.read()
            if "proxy_pass" in content and "backend:8000" in content:
                print("✅ Nginx configuration has proper backend proxy")
                checks_passed += 1
            else:
                print("❌ Nginx configuration missing proper backend proxy")
    except Exception as e:
        print(f"❌ Error reading nginx.conf: {e}")
    
    print(f"\n📊 Configuration: {checks_passed}/{total_checks} configuration files valid")
    return checks_passed == total_checks

def check_executable_permissions():
    """Check that scripts have executable permissions."""
    print("\n🔍 Checking Executable Permissions...")
    print("=" * 50)
    
    scripts = ["start.sh", "test_system.py"]
    checks_passed = 0
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✅ {script} is executable")
                checks_passed += 1
            else:
                print(f"⚠️  {script} is not executable (run: chmod +x {script})")
        else:
            print(f"❌ {script} not found")
    
    print(f"\n📊 Permissions: {checks_passed}/{len(scripts)} scripts executable")
    return checks_passed == len(scripts)

def main():
    """Run all validation checks."""
    print("🚀 RAG Chatbot System Validation")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    all_checks = [
        check_directory_structure(),
        check_file_contents(),
        check_requirements(),
        check_configuration(),
        check_executable_permissions()
    ]
    
    passed_checks = sum(all_checks)
    total_checks = len(all_checks)
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULT: {passed_checks}/{total_checks} validation suites passed")
    
    if passed_checks == total_checks:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\n✨ Your RAG Chatbot system is complete and ready to use!")
        print("\n🚀 Quick Start:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OPENAI_API_KEY to .env")
        print("   3. Run: ./start.sh")
        print("   4. Access: http://localhost:3000")
        return 0
    else:
        print("❌ VALIDATION FAILED!")
        print(f"\n🔧 Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)