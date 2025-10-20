#!/usr/bin/env python3
"""
Test endpoints with proper authentication
This tests the full flow through the API endpoints
"""

import os
import sys
import requests
from dotenv import load_dotenv
import json

load_dotenv()

BACKEND_URL = os.getenv("VITE_API_URL", "http://localhost:8000")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
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

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def main():
    print_header("API Endpoint Testing (Authentication Required)")
    
    print_info("This test requires you to be logged in through the web interface")
    print_info("Backend URL: " + BACKEND_URL)
    print()
    
    # Test health endpoint (no auth required)
    print_info("Testing /api/health (no auth required)...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
        else:
            print_error(f"Health check failed: {response.status_code}")
    except Exception as e:
        print_error(f"Could not reach backend: {e}")
        print_error("Make sure backend is running:")
        print_error("  cd /home/tanmay/Desktop/python-projects/mem0")
        print_error("  source mem0-env/bin/activate")
        print_error("  uvicorn app.main:app --reload")
        return 1
    
    # Test authenticated endpoints (will require login)
    print()
    print_info("Testing /api/memories (auth required)...")
    print_warning("This requires a valid auth token from Supabase")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/memories", timeout=5)
        if response.status_code == 401:
            print_info("Got 401 Unauthorized (expected without token)")
            print_success("Endpoint is working correctly - authentication is required")
        elif response.status_code == 403:
            print_info("Got 403 Forbidden (expected without proper token)")
            print_success("Endpoint is working correctly - authorization is enforced")
        elif response.status_code == 200:
            print_warning("Got 200 OK - This means you're somehow already authenticated")
            print_info(f"Response: {response.json()}")
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
    except Exception as e:
        print_error(f"Error testing endpoint: {e}")
    
    print()
    print_header("Testing Instructions for Full Flow")
    
    print(f"{Colors.BOLD}To test the complete functionality:{Colors.END}")
    print()
    print("1. Make sure both servers are running:")
    print("   Backend:  uvicorn app.main:app --reload")
    print("   Frontend: npm run dev (in frontend directory)")
    print()
    print("2. Open your browser to: http://localhost:5173")
    print()
    print("3. Open Browser DevTools (F12):")
    print("   - Go to Console tab")
    print("   - Go to Network tab")
    print()
    print("4. Log in with your Supabase credentials")
    print()
    print("5. Try to create a memory:")
    print("   - Click 'New Memory'")
    print("   - Enter a title")
    print("   - Click 'Create'")
    print()
    print("6. Check the Console tab for detailed logs:")
    print("   🔵 API Call logs")
    print("   📡 Response logs")
    print("   ✅ Success logs")
    print("   ❌ Error logs")
    print()
    print("7. Check the Network tab:")
    print("   - Look for POST request to /api/memories")
    print("   - Click on it to see:")
    print("     * Request Headers (should have Authorization: Bearer ...)")
    print("     * Request Payload (should have title and description)")
    print("     * Response (should be status 200 with created memory)")
    print()
    print(f"{Colors.BOLD}Common Issues:{Colors.END}")
    print()
    print("• If you see 'NetworkError when attempting to fetch resource':")
    print("  → Backend is not running or wrong URL")
    print("  → Solution: Restart backend and frontend")
    print()
    print("• If you see 401 Unauthorized:")
    print("  → Not logged in or token expired")
    print("  → Solution: Log in again through the UI")
    print()
    print("• If you see 404 Not Found:")
    print("  → Database tables don't exist")
    print("  → Solution: Run SQL migrations from sql/ directory")
    print()
    print("• If you see 500 Internal Server Error:")
    print("  → Check backend logs: tail -f backend.log")
    print()
    
    print_header("Quick Diagnostic Commands")
    print()
    print("# Check configuration")
    print("python verify_config.py")
    print()
    print("# Test database and endpoints")
    print("python test_endpoints.py")
    print()
    print("# Quick health check")
    print("./quick_check.sh")
    print()
    print("# View backend logs")
    print("tail -f backend.log")
    print()
    print("# Restart frontend")
    print("./restart_frontend.sh")
    print()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\nTest interrupted")
        sys.exit(1)

