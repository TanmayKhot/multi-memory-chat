#!/usr/bin/env python3
"""
Detailed Network Error Debugger
This script helps diagnose exactly why the NetworkError is occurring
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from supabase import create_client
import subprocess

load_dotenv()

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_detail(text):
    print(f"{Colors.CYAN}   {text}{Colors.END}")

def print_step(num, text):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}Step {num}: {text}{Colors.END}")

def check_backend_detailed():
    """Detailed backend check"""
    print_header("Checking Backend Server in Detail")
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Can we connect at all?
    print_step(1, "Testing basic connectivity")
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=3)
        print_success(f"Backend is reachable")
        print_detail(f"Status Code: {response.status_code}")
        print_detail(f"Response: {response.json()}")
        print_detail(f"Response Time: {response.elapsed.total_seconds():.3f}s")
    except requests.exceptions.ConnectionError as e:
        print_error(f"Cannot connect to backend!")
        print_detail(f"Error: {str(e)}")
        print_warning("Backend is NOT running!")
        return False
    except requests.exceptions.Timeout:
        print_error("Backend is responding too slowly (timeout)")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False
    
    # Test 2: Test the actual endpoint that's failing
    print_step(2, "Testing /api/memories endpoint (without auth)")
    try:
        response = requests.get(f"{backend_url}/api/memories", timeout=3)
        print_detail(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Endpoint exists and requires authentication (correct!)")
        elif response.status_code == 403:
            print_success("Endpoint exists, got 403 Forbidden (expected without token)")
        elif response.status_code == 200:
            print_warning("Endpoint returned 200 without auth (unusual)")
            print_detail(f"Response: {response.json()}")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
            print_detail(f"Response: {response.text[:200]}")
    except Exception as e:
        print_error(f"Error accessing endpoint: {str(e)}")
        return False
    
    # Test 3: Check if backend can handle POST to /api/memories
    print_step(3, "Testing POST to /api/memories (without auth)")
    try:
        test_data = {"title": "Test Memory", "description": "Test"}
        response = requests.post(
            f"{backend_url}/api/memories",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=3
        )
        print_detail(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("POST endpoint requires authentication (correct!)")
        elif response.status_code == 403:
            print_success("POST endpoint returned 403 (expected without token)")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
            try:
                print_detail(f"Response: {response.json()}")
            except:
                print_detail(f"Response: {response.text[:200]}")
    except Exception as e:
        print_error(f"Error posting to endpoint: {str(e)}")
        return False
    
    return True

def check_frontend_config():
    """Check frontend configuration in detail"""
    print_header("Checking Frontend Configuration")
    
    frontend_env = "frontend/.env.local"
    
    print_step(1, "Checking if frontend/.env.local exists")
    if os.path.exists(frontend_env):
        print_success(f"File exists: {frontend_env}")
        
        with open(frontend_env, 'r') as f:
            content = f.read()
            
        print_step(2, "Checking environment variables")
        
        vars_to_check = {
            'VITE_SUPABASE_URL': None,
            'VITE_SUPABASE_ANON_KEY': None,
            'VITE_API_URL': None
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key in vars_to_check:
                    vars_to_check[key] = value
        
        all_ok = True
        for var, value in vars_to_check.items():
            if value:
                display_value = value[:30] + "..." if len(value) > 30 else value
                print_success(f"{var} = {display_value}")
            else:
                print_error(f"{var} is not set!")
                all_ok = False
        
        # Check VITE_API_URL specifically
        if vars_to_check.get('VITE_API_URL'):
            api_url = vars_to_check['VITE_API_URL']
            if api_url == 'http://localhost:8000':
                print_success("VITE_API_URL is correctly set to http://localhost:8000")
            else:
                print_warning(f"VITE_API_URL is set to: {api_url}")
                print_warning("Expected: http://localhost:8000")
        
        return all_ok
    else:
        print_error(f"Frontend .env.local not found at: {frontend_env}")
        return False

def check_frontend_running():
    """Check if frontend is actually running"""
    print_header("Checking Frontend Server")
    
    print_step(1, "Testing if frontend is accessible")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print_success("Frontend is running on http://localhost:5173")
            return True
        else:
            print_warning(f"Frontend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Frontend is NOT running!")
        print_warning("Frontend needs to be started")
        return False
    except requests.exceptions.Timeout:
        print_error("Frontend is responding too slowly")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {str(e)}")
        return False

def check_processes():
    """Check what processes are running"""
    print_header("Checking Running Processes")
    
    print_step(1, "Looking for backend processes")
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'uvicorn'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print_success(f"Found {len(pids)} uvicorn process(es)")
            for pid in pids:
                print_detail(f"PID: {pid}")
        else:
            print_error("No uvicorn processes found!")
            print_warning("Backend is not running")
    except Exception as e:
        print_warning(f"Could not check processes: {e}")
    
    print_step(2, "Looking for frontend processes")
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'vite'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print_success(f"Found {len(pids)} vite process(es)")
            for pid in pids:
                print_detail(f"PID: {pid}")
            
            if len(pids) > 1:
                print_warning(f"Multiple vite processes detected! This might cause issues.")
                print_warning("Consider restarting frontend: ./restart_frontend.sh")
        else:
            print_error("No vite processes found!")
            print_warning("Frontend is not running")
    except Exception as e:
        print_warning(f"Could not check processes: {e}")

def check_browser_access():
    """Simulate what the browser is doing"""
    print_header("Simulating Browser Request")
    
    print_info("This simulates what happens when you click 'Create Memory'")
    print()
    
    print_step(1, "Simulating frontend API call")
    
    backend_url = "http://localhost:8000"
    endpoint = "/api/memories"
    
    print_detail(f"Request URL: {backend_url}{endpoint}")
    print_detail(f"Method: POST")
    print_detail(f"Headers: Content-Type: application/json")
    print_detail(f"Headers: Authorization: Bearer <token>")
    print_detail(f"Body: {{\"title\": \"Test Memory\"}}")
    print()
    
    print_step(2, "Attempting request WITHOUT authentication")
    
    try:
        response = requests.post(
            f"{backend_url}{endpoint}",
            json={"title": "Test Memory", "description": "Test Description"},
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:5173"  # Simulate browser origin
            },
            timeout=5
        )
        
        print_detail(f"Status Code: {response.status_code}")
        print_detail(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print_success("Got 401 Unauthorized (expected without token)")
            print_info("This means the endpoint is working correctly!")
            print_info("The issue is likely in the frontend not sending the request")
        else:
            print_warning(f"Got unexpected status: {response.status_code}")
            try:
                print_detail(f"Response body: {response.json()}")
            except:
                print_detail(f"Response body: {response.text[:200]}")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print_error("Connection FAILED!")
        print_error("This is the NetworkError you're seeing!")
        print()
        print_detail(f"Error details: {str(e)}")
        print()
        print_warning("Possible causes:")
        print_detail("1. Backend is not running")
        print_detail("2. Backend is running on different port")
        print_detail("3. Firewall blocking connection")
        print_detail("4. VITE_API_URL in frontend not loaded")
        return False
        
    except requests.exceptions.Timeout:
        print_error("Request TIMEOUT!")
        print_warning("Backend is too slow to respond")
        return False
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def check_cors():
    """Check CORS preflight"""
    print_header("Checking CORS Configuration")
    
    backend_url = "http://localhost:8000"
    
    print_step(1, "Simulating CORS preflight request")
    
    try:
        response = requests.options(
            f"{backend_url}/api/memories",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            },
            timeout=5
        )
        
        print_detail(f"Status Code: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        for header, value in cors_headers.items():
            if value:
                print_success(f"{header}: {value}")
            else:
                print_warning(f"{header}: Not set")
        
        if response.status_code in [200, 204]:
            print_success("CORS preflight passed")
            return True
        else:
            print_warning(f"Unexpected preflight status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"CORS check failed: {str(e)}")
        return False

def analyze_logs():
    """Check backend logs for errors"""
    print_header("Analyzing Backend Logs")
    
    log_file = "backend.log"
    
    if not os.path.exists(log_file):
        print_warning("backend.log not found")
        return
    
    print_step(1, "Looking for recent errors in backend.log")
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last 50 lines
        recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        # Look for errors
        errors = [line for line in recent_lines if 'ERROR' in line or '❌' in line or 'Error' in line]
        
        if errors:
            print_warning(f"Found {len(errors)} recent error(s):")
            for error in errors[-5:]:  # Show last 5 errors
                print_detail(error.strip())
        else:
            print_success("No recent errors in backend.log")
        
        # Look for recent POST to /api/memories
        memory_posts = [line for line in recent_lines if 'POST' in line and '/api/memories' in line]
        
        if memory_posts:
            print_info(f"Found {len(memory_posts)} recent POST /api/memories request(s)")
            print_detail("Last request:")
            print_detail(memory_posts[-1].strip())
        else:
            print_warning("No recent POST /api/memories requests found in logs")
            print_info("This suggests the request isn't reaching the backend!")
            
    except Exception as e:
        print_error(f"Could not read log file: {e}")

def main():
    print(f"\n{Colors.BOLD}{'='*70}")
    print("  DETAILED NETWORK ERROR DEBUGGER")
    print(f"{'='*70}{Colors.END}\n")
    
    print_info("This tool will help identify exactly why the NetworkError is occurring")
    print()
    
    results = {}
    
    # Run all checks
    results['Backend Running'] = check_backend_detailed()
    results['Frontend Config'] = check_frontend_config()
    results['Frontend Running'] = check_frontend_running()
    check_processes()
    results['Browser Simulation'] = check_browser_access()
    results['CORS'] = check_cors()
    analyze_logs()
    
    # Final diagnosis
    print_header("DIAGNOSIS & RECOMMENDATIONS")
    
    # Count issues
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    print(f"\n{Colors.BOLD}Test Results: {passed}/{len(results)} passed{Colors.END}\n")
    
    # Provide specific diagnosis
    if not results['Backend Running']:
        print_error("PRIMARY ISSUE: Backend is not running or not accessible")
        print()
        print_info("Solution:")
        print_detail("cd /home/tanmay/Desktop/python-projects/mem0")
        print_detail("source mem0-env/bin/activate")
        print_detail("uvicorn app.main:app --reload")
        
    elif not results['Frontend Running']:
        print_error("PRIMARY ISSUE: Frontend is not running")
        print()
        print_info("Solution:")
        print_detail("./restart_frontend.sh")
        
    elif not results['Frontend Config']:
        print_error("PRIMARY ISSUE: Frontend configuration is incomplete")
        print()
        print_info("Solution:")
        print_detail("Check frontend/.env.local has all required variables")
        print_detail("Then restart frontend: ./restart_frontend.sh")
        
    elif not results['Browser Simulation']:
        print_error("PRIMARY ISSUE: Cannot connect to backend from frontend perspective")
        print()
        print_info("Most likely cause: Frontend hasn't loaded VITE_API_URL")
        print()
        print_info("Solution:")
        print_detail("./restart_frontend.sh")
        print()
        print_info("After restarting, in browser DevTools (F12):")
        print_detail("Console > Type: import.meta.env.VITE_API_URL")
        print_detail("Should show: http://localhost:8000")
        print_detail("If undefined, environment variables aren't loaded")
        
    else:
        print_success("All backend checks passed!")
        print()
        print_info("The issue is likely in the browser/frontend runtime")
        print()
        print_info("Next steps:")
        print_detail("1. Restart frontend: ./restart_frontend.sh")
        print_detail("2. Open browser to: http://localhost:5173")
        print_detail("3. Open DevTools (F12)")
        print_detail("4. Go to Console tab")
        print_detail("5. Type: import.meta.env.VITE_API_URL")
        print_detail("6. Should show: http://localhost:8000")
        print()
        print_detail("7. Try creating a memory again")
        print_detail("8. Watch Console for 🔵 API Call logs")
        print_detail("9. Check Network tab for failed requests")
    
    print()
    print_header("BROWSER DEBUGGING INSTRUCTIONS")
    
    print(f"{Colors.BOLD}When you try to create a memory in the browser:{Colors.END}")
    print()
    print("1. Open DevTools (F12)")
    print()
    print("2. Console Tab - Look for:")
    print_detail("🔵 API Call: POST /memories {title: '...'}")
    print_detail("   ↓")
    print_detail("📡 Response: POST /memories - Status: XXX")
    print_detail("   ↓")
    print_detail("✅ Success OR ❌ Error")
    print()
    print("   If you DON'T see these logs:")
    print_detail("→ Frontend code isn't running properly")
    print_detail("→ Hard refresh: Ctrl+Shift+R")
    print()
    print("3. Network Tab - Look for:")
    print_detail("POST request to /api/memories")
    print_detail("Click on it to see:")
    print_detail("  • Status: Should be 200, 401, or 403")
    print_detail("  • Headers: Check Request URL")
    print_detail("  • Response: Check error message")
    print()
    print("   If request is RED (failed):")
    print_detail("→ This is the NetworkError")
    print_detail("→ Click on it and look at error details")
    print_detail("→ Common: 'Failed to fetch' = Can't reach backend")
    print()
    print("4. Check what URL is being called:")
    print_detail("In Console, type: import.meta.env.VITE_API_URL")
    print_detail("Should output: http://localhost:8000")
    print_detail("If undefined: Frontend env vars not loaded → restart frontend")
    print()
    
    print_header("IMMEDIATE ACTION ITEMS")
    print()
    print(f"{Colors.BOLD}Run these commands:{Colors.END}")
    print()
    print("1. Restart frontend:")
    print(f"   {Colors.CYAN}./restart_frontend.sh{Colors.END}")
    print()
    print("2. Open browser and check console:")
    print(f"   {Colors.CYAN}http://localhost:5173{Colors.END}")
    print(f"   {Colors.CYAN}Press F12 for DevTools{Colors.END}")
    print()
    print("3. Try creating memory and watch:")
    print(f"   {Colors.CYAN}Console tab - for API logs{Colors.END}")
    print(f"   {Colors.CYAN}Network tab - for failed requests{Colors.END}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nDebugging interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

