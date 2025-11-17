from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ComplaintCreate(BaseModel):
    citizen_id: str
    description: str
    language: Optional[str] = None
    category: Optional[str] = None
    urgency_score: Optional[int] = None
    department: Optional[str] = None
    estimated_cost: Optional[float] = None
    required_resources: List[str] = []
    suggested_actions: List[str] = []
    tools_required: List[str] = []
    safety_notes: List[str] = []
    sla_hours: Optional[int] = None
    status: str = "pending"

class Complaint(ComplaintCreate):
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        # No populate_by_name needed for SQL

    @validator('required_resources', 'suggested_actions', 'tools_required', 'safety_notes', pre=True, always=True)
    def parse_list_from_str(cls, v):
        if v is None: # Explicitly handle None values
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    # For converting lists back to comma-separated strings when saving to DB
    def to_sql_dict(self):
        data = self.dict(exclude_unset=True)
        for field in ['required_resources', 'suggested_actions', 'tools_required', 'safety_notes']:
            if field in data and isinstance(data[field], list):
                data[field] = ",".join(data[field])
        return data

class ComplaintStatusUpdate(BaseModel):
    status: str
