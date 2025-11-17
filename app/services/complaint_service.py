from sqlalchemy.orm import Session
from ..models.complaint_model import Complaint, ComplaintCreate
from ..models.sql_models import ComplaintSQL
from ..models.categorization_model import ComplaintCategorizer
from ..services.multilingual_service import MultilingualService
from ..services.cost_estimation_service import CostEstimationService
from ..services.field_officer_service import FieldOfficerService
from typing import Optional, List
import json

class ComplaintService:
    def __init__(self, db: Session):
        self.db = db
        self.categorizer = ComplaintCategorizer()
        self.multilingual_service = MultilingualService()
        self.cost_estimation_service = CostEstimationService()
        self.field_officer_service = FieldOfficerService()

    def create_complaint(self, complaint_data: ComplaintCreate) -> Complaint:
        if not complaint_data.language:
            complaint_data.language = self.multilingual_service.detect_language(complaint_data.description)
        
        categorization_result = self.categorizer.categorize_and_prioritize(complaint_data.description)
        
        complaint_data.category = categorization_result["category"]
        complaint_data.urgency_score = categorization_result["urgency_score"]
        complaint_data.department = categorization_result["department"]

        cost_estimation_result = self.cost_estimation_service.estimate_cost_and_resources(
            complaint_data.category, 
            complaint_data.description
        )
        complaint_data.estimated_cost = cost_estimation_result["estimated_cost"]
        complaint_data.required_resources = cost_estimation_result["required_resources"]

        field_officer_suggestions = self.field_officer_service.suggest_action_steps(
            complaint_data.category,
            complaint_data.urgency_score,
            complaint_data.description
        )
        complaint_data.suggested_actions = field_officer_suggestions["suggested_actions"]
        complaint_data.tools_required = field_officer_suggestions["tools_required"]
        complaint_data.safety_notes = field_officer_suggestions["safety_notes"]
        complaint_data.sla_hours = field_officer_suggestions["sla_hours"]

        # Convert Pydantic model to SQLAlchemy model
        db_complaint = ComplaintSQL(**complaint_data.dict(exclude_unset=True))
        db_complaint.required_resources = ",".join(complaint_data.required_resources)
        db_complaint.suggested_actions = ",".join(complaint_data.suggested_actions)
        db_complaint.tools_required = ",".join(complaint_data.tools_required)
        db_complaint.safety_notes = ",".join(complaint_data.safety_notes)

        self.db.add(db_complaint)
        self.db.commit()
        self.db.refresh(db_complaint)

        return Complaint(**db_complaint.__dict__)

    def get_complaint_by_id(self, complaint_id: int) -> Optional[Complaint]:
        complaint_data = self.db.query(ComplaintSQL).filter(ComplaintSQL.id == complaint_id).first()
        if complaint_data:
            return Complaint(
                id=complaint_data.id,
                citizen_id=complaint_data.citizen_id,
                description=complaint_data.description,
                language=complaint_data.language,
                category=complaint_data.category,
                urgency_score=complaint_data.urgency_score,
                department=complaint_data.department,
                estimated_cost=complaint_data.estimated_cost,
                required_resources=complaint_data.required_resources, # Pydantic validator will handle conversion
                suggested_actions=complaint_data.suggested_actions, # Pydantic validator will handle conversion
                tools_required=complaint_data.tools_required, # Pydantic validator will handle conversion
                safety_notes=complaint_data.safety_notes, # Pydantic validator will handle conversion
                sla_hours=complaint_data.sla_hours,
                status=complaint_data.status,
                created_at=complaint_data.created_at
            )
        return None

    def get_all_complaints(self) -> List[Complaint]:
        all_complaints_data = self.db.query(ComplaintSQL).all()
        complaints = []
        for complaint_data in all_complaints_data:
            complaints.append(Complaint(
                id=complaint_data.id,
                citizen_id=complaint_data.citizen_id,
                description=complaint_data.description,
                language=complaint_data.language,
                category=complaint_data.category,
                urgency_score=complaint_data.urgency_score,
                department=complaint_data.department,
                estimated_cost=complaint_data.estimated_cost,
                required_resources=complaint_data.required_resources, # Pydantic validator will handle conversion
                suggested_actions=complaint_data.suggested_actions, # Pydantic validator will handle conversion
                tools_required=complaint_data.tools_required, # Pydantic validator will handle conversion
                safety_notes=complaint_data.safety_notes, # Pydantic validator will handle conversion
                sla_hours=complaint_data.sla_hours,
                status=complaint_data.status,
                created_at=complaint_data.created_at
            ))
        print(f"Complaints from DB (before Pydantic validation): {complaints}") # Debug print
        return complaints

    def update_complaint_status(self, complaint_id: int, new_status: str) -> Optional[Complaint]:
        db_complaint = self.db.query(ComplaintSQL).filter(ComplaintSQL.id == complaint_id).first()
        if db_complaint:
            db_complaint.status = new_status
            self.db.commit()
            self.db.refresh(db_complaint)
            # Convert SQLAlchemy model back to Pydantic model explicitly
            return Complaint(
                id=db_complaint.id,
                citizen_id=db_complaint.citizen_id,
                description=db_complaint.description,
                language=db_complaint.language,
                category=db_complaint.category,
                urgency_score=db_complaint.urgency_score,
                department=db_complaint.department,
                estimated_cost=db_complaint.estimated_cost,
                required_resources=db_complaint.required_resources,
                suggested_actions=db_complaint.suggested_actions,
                tools_required=db_complaint.tools_required,
                safety_notes=db_complaint.safety_notes,
                sla_hours=db_complaint.sla_hours,
                status=db_complaint.status,
                created_at=db_complaint.created_at
            )
        return None
