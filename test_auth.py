#!/usr/bin/env python3
"""
Simple test script to verify authentication endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "username": "testuser",
        "password": "testpass123",
        "bio": "Test user for authentication testing",
        "profile_public": True,
        "allow_contact": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {data['id']}")
            print(f"Email: {data['email']}")
            print(f"Username: {data['username']}")
            return data
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    print(f"\nTesting user login for {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Access token: {data['access_token'][:50]}...")
            print(f"Token type: {data['token_type']}")
            print(f"User: {data['user']['full_name']}")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_get_current_user(token):
    """Test getting current user with token"""
    print(f"\nTesting get current user...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get current user successful!")
            print(f"User: {data['full_name']} ({data['email']})")
            print(f"Active: {data['is_active']}")
            print(f"Verified: {data['is_verified']}")
            return data
        else:
            print(f"❌ Get current user failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting current user: {e}")
        return None

def main():
    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test registration
    user = test_register()
    if not user:
        print("Registration failed, cannot continue with login test")
        return
    
    # Test login
    token = test_login(user['email'], "testpass123")
    if not token:
        print("Login failed, cannot continue with current user test")
        return
    
    # Test get current user
    current_user = test_get_current_user(token)
    
    print("\n" + "=" * 50)
    if current_user:
        print("🎉 All authentication tests passed!")
    else:
        print("❌ Some authentication tests failed")

if __name__ == "__main__":
    main() 