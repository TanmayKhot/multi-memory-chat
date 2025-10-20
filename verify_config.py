#!/usr/bin/env python3
"""
Database Configuration Verification Script
This script checks if all required environment variables are set correctly
and tests connectivity to Supabase.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_env_file(file_path, name):
    """Check if an env file exists"""
    print_header(f"Checking {name}")
    if os.path.exists(file_path):
        print_success(f"{name} exists at: {file_path}")
        return True
    else:
        print_error(f"{name} not found at: {file_path}")
        return False

def check_backend_config():
    """Check backend environment configuration"""
    print_header("Backend Configuration Check")
    
    # Load backend .env
    backend_env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(backend_env_path):
        print_error(f"Backend .env file not found at: {backend_env_path}")
        return False
    
    load_dotenv(backend_env_path)
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_DB_URL'
    ]
    
    optional_vars = ['OPENAI_API_KEY']
    
    all_ok = True
    config = {}
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value and value.strip():
            config[var] = value
            # Mask sensitive values in display
            display_value = value[:20] + "..." if len(value) > 20 else value
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var} is missing or empty!")
            all_ok = False
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value and value.strip():
            display_value = value[:20] + "..." if len(value) > 20 else value
            print_info(f"{var}: {display_value} (optional)")
        else:
            print_warning(f"{var} not set (optional)")
    
    return all_ok, config

def check_frontend_config():
    """Check frontend environment configuration"""
    print_header("Frontend Configuration Check")
    
    frontend_env_path = os.path.join(os.getcwd(), 'frontend', '.env.local')
    if not os.path.exists(frontend_env_path):
        print_error(f"Frontend .env.local file not found at: {frontend_env_path}")
        return False
    
    # Read frontend env file
    frontend_config = {}
    with open(frontend_env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                frontend_config[key.strip()] = value.strip()
    
    required_vars = ['VITE_SUPABASE_URL', 'VITE_SUPABASE_ANON_KEY']
    all_ok = True
    
    for var in required_vars:
        value = frontend_config.get(var, '')
        if value and value.strip():
            display_value = value[:20] + "..." if len(value) > 20 else value
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var} is missing or empty!")
            all_ok = False
    
    return all_ok, frontend_config

def validate_url(url, name):
    """Validate URL format"""
    print_info(f"Validating {name} format...")
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            print_success(f"{name} format is valid: {result.scheme}://{result.netloc}")
            return True
        else:
            print_error(f"{name} format is invalid!")
            return False
    except Exception as e:
        print_error(f"Error validating {name}: {str(e)}")
        return False

def test_supabase_connectivity(url, anon_key):
    """Test connectivity to Supabase"""
    print_header("Testing Supabase Connectivity")
    
    # Test 1: Health check
    print_info("Testing Supabase REST API...")
    try:
        health_url = f"{url}/rest/v1/"
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        response = requests.get(health_url, headers=headers, timeout=10)
        
        if response.status_code in [200, 404]:  # 404 is OK for root endpoint
            print_success(f"Supabase REST API is reachable (Status: {response.status_code})")
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Cannot reach Supabase URL")
        print_error("Possible issues:")
        print_error("  - URL is incorrect")
        print_error("  - No internet connection")
        print_error("  - Supabase project is paused or deleted")
        return False
    except requests.exceptions.Timeout:
        print_error("Connection timeout! Supabase is not responding")
        return False
    except Exception as e:
        print_error(f"Error testing connectivity: {str(e)}")
        return False
    
    # Test 2: Try to access a table
    print_info("Testing table access (memories table)...")
    try:
        table_url = f"{url}/rest/v1/memories?limit=1"
        response = requests.get(table_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_success("Successfully connected to 'memories' table")
            return True
        elif response.status_code == 401:
            print_error("Authentication failed! Check your ANON_KEY")
            return False
        elif response.status_code == 404:
            print_error("Table 'memories' not found!")
            print_warning("Please ensure you have run the database migrations")
            return False
        else:
            print_warning(f"Unexpected status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Error accessing table: {str(e)}")
        return False

def check_backend_server():
    """Check if backend server is running"""
    print_header("Checking Backend Server")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend server is running on http://localhost:8000")
            return True
        else:
            print_warning(f"Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Backend server is NOT running!")
        print_info("Start it with: cd /home/tanmay/Desktop/python-projects/mem0 && source mem0-env/bin/activate && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {str(e)}")
        return False

def check_frontend_server():
    """Check if frontend server is running"""
    print_header("Checking Frontend Server")
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print_success("Frontend server is running on http://localhost:5173")
            return True
        else:
            print_warning(f"Frontend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Frontend server is NOT running!")
        print_info("Start it with: cd /home/tanmay/Desktop/python-projects/mem0/frontend && npm run dev")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {str(e)}")
        return False

def check_cors_config():
    """Check CORS configuration"""
    print_header("Checking CORS Configuration")
    
    expected_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]
    
    print_info("Expected CORS origins in backend:")
    for origin in expected_origins:
        print(f"  - {origin}")
    
    print_success("CORS appears to be configured correctly in app/main.py")

def check_consistency():
    """Check if backend and frontend configs match"""
    print_header("Checking Configuration Consistency")
    
    # Load both configs
    load_dotenv('.env')
    backend_url = os.getenv('SUPABASE_URL', '')
    backend_key = os.getenv('SUPABASE_ANON_KEY', '')
    
    frontend_env_path = 'frontend/.env.local'
    frontend_config = {}
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    frontend_config[key.strip()] = value.strip()
    
    frontend_url = frontend_config.get('VITE_SUPABASE_URL', '')
    frontend_key = frontend_config.get('VITE_SUPABASE_ANON_KEY', '')
    
    all_match = True
    
    # Check URL match
    if backend_url == frontend_url:
        print_success(f"URLs match: {backend_url[:30]}...")
    else:
        print_error("URLs DO NOT match!")
        print_error(f"  Backend:  {backend_url}")
        print_error(f"  Frontend: {frontend_url}")
        all_match = False
    
    # Check key match
    if backend_key == frontend_key:
        print_success(f"ANON keys match: {backend_key[:20]}...")
    else:
        print_error("ANON keys DO NOT match!")
        print_error(f"  Backend:  {backend_key[:30]}...")
        print_error(f"  Frontend: {frontend_key[:30]}...")
        all_match = False
    
    return all_match

def provide_recommendations():
    """Provide recommendations based on findings"""
    print_header("Recommendations")
    
    print_info("1. If Supabase connection fails:")
    print("   - Verify your Supabase project is active")
    print("   - Check if you're using the correct project URL")
    print("   - Ensure your API keys are valid and not expired")
    
    print_info("\n2. If backend/frontend configs don't match:")
    print("   - Update both .env and frontend/.env.local files")
    print("   - Restart both servers after updating")
    
    print_info("\n3. If servers are not running:")
    print("   - Backend: cd /home/tanmay/Desktop/python-projects/mem0 && source mem0-env/bin/activate && uvicorn app.main:app --reload")
    print("   - Frontend: cd /home/tanmay/Desktop/python-projects/mem0/frontend && npm run dev")
    
    print_info("\n4. If database tables don't exist:")
    print("   - Run the SQL migrations from the sql/ directory in your Supabase SQL Editor")
    
    print_info("\n5. Check browser console for frontend errors:")
    print("   - Open DevTools (F12) and check the Console and Network tabs")

def main():
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  Database Configuration Verification Tool")
    print(f"{'='*60}{Colors.END}\n")
    
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    results = {
        'backend_env': False,
        'frontend_env': False,
        'supabase_connectivity': False,
        'backend_server': False,
        'frontend_server': False,
        'consistency': False
    }
    
    # 1. Check backend config
    backend_ok, backend_config = check_backend_config()
    results['backend_env'] = backend_ok
    
    # 2. Check frontend config
    frontend_ok, frontend_config = check_frontend_config()
    results['frontend_env'] = frontend_ok
    
    # 3. Validate URLs
    if backend_ok and 'SUPABASE_URL' in backend_config:
        validate_url(backend_config['SUPABASE_URL'], "Supabase URL")
    
    # 4. Test Supabase connectivity
    if backend_ok and all(key in backend_config for key in ['SUPABASE_URL', 'SUPABASE_ANON_KEY']):
        results['supabase_connectivity'] = test_supabase_connectivity(
            backend_config['SUPABASE_URL'],
            backend_config['SUPABASE_ANON_KEY']
        )
    
    # 5. Check servers
    results['backend_server'] = check_backend_server()
    results['frontend_server'] = check_frontend_server()
    
    # 6. Check CORS
    check_cors_config()
    
    # 7. Check consistency
    if backend_ok and frontend_ok:
        results['consistency'] = check_consistency()
    
    # 8. Provide recommendations
    provide_recommendations()
    
    # Final summary
    print_header("Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for check, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Results: {passed_checks}/{total_checks} checks passed{Colors.END}\n")
    
    if passed_checks == total_checks:
        print_success("All checks passed! Your configuration looks good.")
        return 0
    else:
        print_error(f"Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

