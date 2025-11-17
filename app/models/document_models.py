from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RTIDocument(BaseModel):
    applicant_name: str
    address: str
    information_sought: str
    circular_id: Optional[str] = None # Reference to a processed circular
    complaint_id: Optional[str] = None # New: Reference to a complaint for dynamic fields
    circular_summary: Optional[str] = None
    extracted_rules: List[dict] = [] # List of dict to be flexible with ExtractedRule
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class SchemeApplication(BaseModel):
    applicant_name: str
    address: str
    scheme_name: str
    required_documents: List[str] = []
    circular_id: Optional[str] = None
    circular_summary: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    deadlines: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class OfficialNotice(BaseModel):
    recipient: str
    sender: str
    subject: str
    body: Optional[str] = None
    complaint_id: Optional[str] = None # Reference to a complaint for auto-generation
    circular_id: Optional[str] = None # Reference to a circular for auto-generation
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkOrder(BaseModel):
    complaint_id: Optional[str] = None # Reference to a complaint
    assigned_department: Optional[str] = None
    task_description: Optional[str] = None
    caller_name: Optional[str] = None
    caller_contact: Optional[str] = None
    estimated_cost: Optional[float] = None
    suggested_actions: List[str] = []
    status: str = "pending"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


