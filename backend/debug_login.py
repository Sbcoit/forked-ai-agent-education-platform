#!/usr/bin/env python3
"""
Debug script to check login issues
"""

from sqlalchemy import create_engine, text
from database.connection import settings
from database.models import User
from database.connection import SessionLocal
from utilities.auth import verify_password, get_password_hash
import sys

def check_users_in_database():
    """Check what users exist in the database"""
    print("🔍 Checking users in database...")
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"📊 Found {len(users)} users:")
        
        for user in users:
            print(f"  • ID: {user.id}")
            print(f"    Email: {user.email}")
            print(f"    Username: {user.username}")
            print(f"    Full Name: {user.full_name}")
            print(f"    Is Active: {user.is_active}")
            print(f"    Has Password: {'Yes' if user.password_hash else 'No'}")
            print(f"    Created: {user.created_at}")
            print("-" * 40)
            
        return users
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        return []
    finally:
        db.close()

def check_specific_user(email):
    """Check if a specific user exists and verify password"""
    print(f"\n🔍 Checking user: {email}")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found!")
            return None
            
        print(f"✅ User found:")
        print(f"  • ID: {user.id}")
        print(f"  • Email: {user.email}")
        print(f"  • Username: {user.username}")
        print(f"  • Full Name: {user.full_name}")
        print(f"  • Is Active: {user.is_active}")
        print(f"  • Has Password Hash: {'Yes' if user.password_hash else 'No'}")
        
        if user.password_hash:
            print(f"  • Password Hash: {user.password_hash[:50]}...")
        
        return user
        
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None
    finally:
        db.close()

def test_password_verification(email, password):
    """Test password verification for a user"""
    print(f"\n🔐 Testing password verification for: {email}")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found!")
            return False
            
        if not user.password_hash:
            print(f"❌ User has no password hash!")
            return False
            
        # Test password verification
        is_valid = verify_password(password, user.password_hash)
        print(f"🔐 Password verification result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Error verifying password: {e}")
        return False
    finally:
        db.close()

def create_test_user(email, password, full_name, username):
    """Create a test user with proper password hashing"""
    print(f"\n👤 Creating test user: {email}")
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  User already exists!")
            return existing_user
            
        # Create new user with hashed password
        hashed_password = get_password_hash(password)
        print(f"🔐 Generated password hash: {hashed_password[:50]}...")
        
        new_user = User(
            email=email,
            full_name=full_name,
            username=username,
            password_hash=hashed_password,
            is_active=True,
            is_verified=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created successfully!")
        print(f"  • ID: {new_user.id}")
        print(f"  • Email: {new_user.email}")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Login Debug Tool")
    print("=" * 60)
    
    # Check all users
    users = check_users_in_database()
    
    # Check the specific user trying to log in
    target_email = "hendrik.krack@gmail.com"
    user = check_specific_user(target_email)
    
    if user:
        # Test with the actual password
        print(f"\n🔐 Let's test password verification.")
        print(f"Please enter the password for {target_email}:")
        
        # For testing, let's try a few common passwords
        test_passwords = ["test123", "password", "admin", "123456"]
        
        for test_pass in test_passwords:
            print(f"\n🧪 Testing password: '{test_pass}'")
            if test_password_verification(target_email, test_pass):
                print(f"✅ SUCCESS! Password '{test_pass}' works!")
                break
        else:
            print(f"\n❌ None of the test passwords worked.")
            print(f"💡 The user exists but password verification is failing.")
            print(f"   This suggests the actual password is different from what we're testing.")
            
    else:
        print(f"\n💡 User {target_email} doesn't exist. Let's create a test user...")
        
        # Create a test user
        test_user = create_test_user(
            email=target_email,
            password="test123",  # Simple test password
            full_name="Hendrik Krack",
            username="hendrikk"
        )
        
        if test_user:
            print(f"\n🧪 Testing login with created user...")
            test_password_verification(target_email, "test123")
            
            print(f"\n✅ You can now log in with:")
            print(f"   Email: {target_email}")
            print(f"   Password: test123") 