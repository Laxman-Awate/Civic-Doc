from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.dialects.postgresql import ARRAY # Removed PostgreSQL specific import
from datetime import datetime

Base = declarative_base()

class ComplaintSQL(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(String, index=True)
    description = Column(Text)
    language = Column(String, nullable=True)
    category = Column(String, nullable=True)
    urgency_score = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    required_resources = Column(Text, nullable=True) # Stored as comma-separated string
    suggested_actions = Column(Text, nullable=True) # Stored as comma-separated string
    tools_required = Column(Text, nullable=True) # Stored as comma-separated string
    safety_notes = Column(Text, nullable=True) # Stored as comma-separated string
    sla_hours = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class CircularSQL(Base):
    __tablename__ = "circulars"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content_summary = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    extracted_rules = Column(Text, nullable=True) # Stored as JSON string
    eligibility_criteria = Column(Text, nullable=True)
    deadlines = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class UserSQL(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="citizen") # e.g., "citizen", "department_admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

