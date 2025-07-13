#!/usr/bin/env python3
"""
Script to create default business scenarios for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from database import engine
from models import BusinessScenario, User

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def create_default_scenarios():
    """Create default scenarios for testing"""
    
    # Check if scenarios already exist
    existing_scenarios = db.query(BusinessScenario).count()
    if existing_scenarios > 0:
        print(f"Found {existing_scenarios} existing scenarios. Skipping creation.")
        return
    
    scenarios = [
        {
            "title": "EcoFriendly Product Launch",
            "description": "Launch a solar-powered phone case in the San Francisco market",
            "industry": "eco-friendly",
            "challenge": "Navigate product development, marketing strategy, financial planning, and operations while maintaining sustainability focus",
            "learning_objectives": [
                "Cross-functional business operations",
                "Sustainable product development",
                "Market entry strategies",
                "Financial planning and budgeting",
                "Team coordination and communication"
            ],
            "source_type": "predefined",
            "source_data": None,
            "created_by": 1
        },
        {
            "title": "Healthcare Innovation",
            "description": "Launch a telemedicine platform for rural communities",
            "industry": "healthcare",
            "challenge": "Address regulatory compliance, technology infrastructure, patient adoption, and partnership development",
            "learning_objectives": [
                "Healthcare business models",
                "Regulatory environment navigation",
                "Social impact measurement",
                "Technology adoption strategies",
                "Partnership development"
            ],
            "source_type": "predefined",
            "source_data": None,
            "created_by": 1
        },
        {
            "title": "FinTech Startup Challenge",
            "description": "Create a mobile banking app for underbanked communities",
            "industry": "fintech",
            "challenge": "Build trust, ensure security, navigate financial regulations, and achieve user adoption",
            "learning_objectives": [
                "Financial services innovation",
                "Security and compliance",
                "User experience design",
                "Market penetration strategies",
                "Risk management"
            ],
            "source_type": "predefined",
            "source_data": None,
            "created_by": 1
        },
        {
            "title": "EdTech Platform Development",
            "description": "Develop an AI-powered learning platform for K-12 students",
            "industry": "education",
            "challenge": "Balance pedagogical effectiveness, technology integration, privacy concerns, and market adoption",
            "learning_objectives": [
                "Educational technology design",
                "AI ethics and implementation",
                "Privacy and data protection",
                "Stakeholder management",
                "Product-market fit"
            ],
            "source_type": "predefined",
            "source_data": None,
            "created_by": 1
        }
    ]
    
    # Create scenarios
    for scenario_data in scenarios:
        scenario = BusinessScenario(**scenario_data)
        db.add(scenario)
    
    # Commit all scenarios
    db.commit()
    print(f"Created {len(scenarios)} default scenarios!")
    
    # Print created scenarios
    for scenario in db.query(BusinessScenario).all():
        print(f"- {scenario.title} (ID: {scenario.id})")

def create_default_user():
    """Create a default user for testing"""
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        print("Default user already exists.")
        return
    
    user = User(
        email="test@example.com",
        full_name="Test User",
        role="teacher",
        hashed_password="dummy_hash_for_testing"
    )
    db.add(user)
    db.commit()
    print("Created default user!")

if __name__ == "__main__":
    print("Creating default data...")
    try:
        create_default_user()
        create_default_scenarios()
        print("✅ Default data created successfully!")
    except Exception as e:
        print(f"❌ Error creating default data: {e}")
        db.rollback()
    finally:
        db.close() 