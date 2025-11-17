from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import json

class ExtractedRule(BaseModel):
    rule_text: str
    keywords: List[str] = []
    relevance_score: Optional[float] = None

class CircularCreate(BaseModel):
    filename: str
    content_summary: Optional[str] = None
    language: Optional[str] = None
    extracted_rules: List[ExtractedRule] = []
    eligibility_criteria: Optional[str] = None
    deadlines: Optional[str] = None

class Circular(CircularCreate):
    id: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('extracted_rules', pre=True, always=True)
    def parse_extracted_rules(cls, v):
        if isinstance(v, str):
            try:
                return [ExtractedRule(**rule) for rule in json.loads(v)]
            except json.JSONDecodeError:
                return []
        return v
    
    def to_sql_dict(self):
        data = self.dict(exclude_unset=True)
        if "extracted_rules" in data and isinstance(data["extracted_rules"], list):
            data["extracted_rules"] = json.dumps([rule.dict() for rule in data["extracted_rules"]])
        return data
