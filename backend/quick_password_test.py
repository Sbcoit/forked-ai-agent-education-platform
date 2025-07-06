#!/usr/bin/env python3
"""
Quick test to create or reset a user password for testing
"""

from database.connection import SessionLocal
from database.models import User
from utilities.auth import get_password_hash

def create_test_user():
    """Create a test user with known password"""
    db = SessionLocal()
    
    try:
        # Check if test user exists
        test_email = "test@example.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"🔄 Test user already exists, updating password...")
            # Update password
            existing_user.password_hash = get_password_hash("testpass123")
            db.commit()
            print(f"✅ Updated test user password")
            print(f"   Email: {test_email}")
            print(f"   Password: testpass123")
            print(f"   User ID: {existing_user.id}")
            return existing_user.id
        else:
            print(f"👤 Creating new test user...")
            # Create new test user
            new_user = User(
                email=test_email,
                full_name="Test User",
                username="testuser",
                password_hash=get_password_hash("testpass123"),
                is_active=True,
                is_verified=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ Created test user")
            print(f"   Email: {test_email}")
            print(f"   Password: testpass123")
            print(f"   User ID: {new_user.id}")
            return new_user.id
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def reset_existing_user_password():
    """Reset the password for hendrik.krack@gmail.com"""
    db = SessionLocal()
    
    try:
        # Get the existing user
        user = db.query(User).filter(User.email == "hendrik.krack@gmail.com").first()
        
        if user:
            print(f"🔄 Resetting password for existing user...")
            # Update password to known value
            user.password_hash = get_password_hash("newpass123")
            db.commit()
            
            print(f"✅ Password reset successful")
            print(f"   Email: hendrik.krack@gmail.com")
            print(f"   New Password: newpass123")
            print(f"   User ID: {user.id}")
            return user.id
        else:
            print(f"❌ User hendrik.krack@gmail.com not found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Password Setup for Testing")
    print("=" * 40)
    
    # Option 1: Reset existing user password
    print("Option 1: Reset existing user password")
    user_id = reset_existing_user_password()
    
    if not user_id:
        # Option 2: Create test user
        print("\nOption 2: Create test user")
        user_id = create_test_user()
    
    if user_id:
        print(f"\n✅ Ready for authentication testing!")
    else:
        print(f"\n❌ Failed to set up test user") 