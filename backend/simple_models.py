# Simplified Database Models for CrewAI Education Platform
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String, default="teacher")  # teacher, student
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scenarios = relationship("BusinessScenario", back_populates="creator")
    simulations = relationship("SimulationSession", back_populates="user")

class BusinessScenario(Base):
    __tablename__ = "business_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    industry = Column(String)
    challenge = Column(Text)
    learning_objectives = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="scenarios")
    simulations = relationship("SimulationSession", back_populates="scenario")

class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("business_scenarios.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="active")  # active, completed
    crew_output = Column(Text)  # Final crew result
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    scenario = relationship("BusinessScenario", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    messages = relationship("SimulationMessage", back_populates="simulation")

class SimulationMessage(Base):
    __tablename__ = "simulation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_sessions.id"))
    user_message = Column(Text)
    crew_response = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("SimulationSession", back_populates="messages") 