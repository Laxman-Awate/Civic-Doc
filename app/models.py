from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ComplaintCreate(BaseModel):
citizen_name: Optional[str]
contact: Optional[str]
message: str
source: Optional[str] = "web"
location: Optional[str]


class ComplaintDB(ComplaintCreate):
id: Optional[str]
category: str
priority_score: int
urgency: str
routed_to: str
status: str = "pending"
created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentRequest(BaseModel):
doc_type: str # rti, application, notice, workorder
complaint_id: Optional[str]
circular_text: Optional[str]
language: str = "en"