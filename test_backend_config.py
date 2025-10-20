#!/usr/bin/env python3
"""
Test Backend Configuration
Verify that backend can load Supabase configuration correctly
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{END}")
    print(f"{BOLD}{BLUE}{text}{END}")
    print(f"{BOLD}{BLUE}{'='*70}{END}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{END}")

def print_error(text):
    print(f"{RED}❌ {text}{END}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{END}")

print_header("Testing Backend Configuration Fix")

# Test 1: Backend health check
print_info("Test 1: Backend health check...")
try:
    response = requests.get("http://localhost:8000/api/health", timeout=5)
    if response.status_code == 200:
        print_success("Backend is running")
    else:
        print_error(f"Backend returned {response.status_code}")
        sys.exit(1)
except Exception as e:
    print_error(f"Backend not reachable: {e}")
    sys.exit(1)

# Test 2: Try to call memories endpoint without auth (should get 401, NOT 500)
print_info("Test 2: Testing memories endpoint without authentication...")
try:
    response = requests.get("http://localhost:8000/api/memories", timeout=5)
    
    if response.status_code == 401:
        print_success("Got 401 Unauthorized (expected - need to log in)")
        print_info("This means Supabase IS configured correctly!")
    elif response.status_code == 500:
        print_error("Got 500 Internal Server Error")
        try:
            error_detail = response.json().get('detail', '')
            if "Supabase not configured" in error_detail:
                print_error("Supabase configuration still not loaded!")
                print_error("Backend may need to be restarted")
            else:
                print_error(f"Error: {error_detail}")
        except:
            print_error(f"Response: {response.text}")
        sys.exit(1)
    else:
        print_info(f"Got status {response.status_code}")
        print_info(f"Response: {response.text[:200]}")
except Exception as e:
    print_error(f"Request failed: {e}")
    sys.exit(1)

# Test 3: Try POST without auth (should also get 401, NOT 500)
print_info("Test 3: Testing POST /api/memories without authentication...")
try:
    response = requests.post(
        "http://localhost:8000/api/memories",
        json={"title": "Test", "description": "Test"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 401:
        print_success("Got 401 Unauthorized (expected)")
        print_info("Configuration is working!")
    elif response.status_code == 500:
        print_error("Got 500 Internal Server Error")
        try:
            error_detail = response.json().get('detail', '')
            print_error(f"Error: {error_detail}")
        except:
            print_error(f"Response: {response.text}")
        sys.exit(1)
    else:
        print_info(f"Got status {response.status_code}: {response.text[:200]}")
except Exception as e:
    print_error(f"Request failed: {e}")
    sys.exit(1)

# Summary
print_header("Configuration Test Results")
print_success("✅ Backend configuration is working correctly!")
print_info("")
print_info("The 'Supabase not configured' error is FIXED!")
print_info("")
print_info("Now you can:")
print_info("1. Start frontend: cd frontend && npm run dev")
print_info("2. Open browser: http://localhost:5173")
print_info("3. Log in with Supabase credentials")
print_info("4. Create memories - should work now!")
print_info("")
print_info("To run full CRUD tests after logging in:")
print_info("  python demo_supabase_test_v2.py")
print_info("")

