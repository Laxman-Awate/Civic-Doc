from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.document_models import RTIDocument, SchemeApplication, OfficialNotice, WorkOrder
from ..models.complaint_model import Complaint
from ..models.circular_model import Circular
from ..services.complaint_service import ComplaintService
from ..services.pdf_processing_service import PdfProcessingService
import json

class DocumentGenerationService:
    def __init__(self, db: Session):
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.db = db
        self.complaint_service = ComplaintService(db)
        self.pdf_processing_service = PdfProcessingService(db)

    def generate_rti_document(self, data: RTIDocument) -> str:
        render_data = data.dict()
        
        department_name = "[Department Name]" # Default placeholder
        office_address = "[Office Address]" # Default placeholder

        if data.complaint_id:
            complaint_details = self.complaint_service.get_complaint_by_id(int(data.complaint_id))
            if complaint_details:
                department_name = complaint_details.department # Use department from complaint
                # For now, a generic office address based on department
                office_address = f"{department_name} Office, [City/Municipality]"
                
        render_data["department_name"] = department_name
        render_data["office_address"] = office_address

        if data.circular_id:
            circular_details = self.pdf_processing_service.get_circular_by_id(int(data.circular_id))
            if circular_details:
                render_data.update({
                    "circular_summary": circular_details.content_summary,
                    "extracted_rules": circular_details.extracted_rules 
                })

        template = self.env.get_template("rti_template.j2")
        return template.render(render_data)

    def generate_scheme_application(self, data: SchemeApplication) -> str:
        render_data = data.dict()
        if data.circular_id:
            circular_details = self.pdf_processing_service.get_circular_by_id(int(data.circular_id))
            if circular_details:
                render_data.update({
                    "circular_summary": circular_details.content_summary,
                    "eligibility_criteria": circular_details.eligibility_criteria,
                    "deadlines": circular_details.deadlines
                })

        template = self.env.get_template("scheme_application_template.j2")
        return template.render(render_data)

    def generate_official_notice(self, data: OfficialNotice) -> str:
        render_data = data.dict()
        auto_generated_body_parts = []

        if data.complaint_id:
            complaint_details = self.complaint_service.get_complaint_by_id(int(data.complaint_id))
            if complaint_details:
                auto_generated_body_parts.append(f"Regarding your complaint (ID: {complaint_details.id}, Category: {complaint_details.category}, Urgency: {complaint_details.urgency_score}/100) submitted on {complaint_details.created_at.strftime('%Y-%m-%d')}: {complaint_details.description}")
                if complaint_details.suggested_actions:
                    auto_generated_body_parts.append(f"Suggested actions include: {', '.join(complaint_details.suggested_actions)}.")

        if data.circular_id:
            circular_details = self.pdf_processing_service.get_circular_by_id(int(data.circular_id))
            if circular_details:
                auto_generated_body_parts.append(f"Reference is made to circular '{circular_details.filename}' (ID: {circular_details.id}). Summary: {circular_details.content_summary}.")
                if circular_details.extracted_rules:
                    rules_text = "; ".join([rule['rule_text'] for rule in circular_details.extracted_rules])
                    auto_generated_body_parts.append(f"Key rules extracted: {rules_text}")

        if not data.body and auto_generated_body_parts:
            render_data["body"] = "\n\n".join(auto_generated_body_parts)
        elif data.body and auto_generated_body_parts:
            render_data["body"] = data.body + "\n\n" + "\n\n".join(auto_generated_body_parts)
        elif not data.body and not auto_generated_body_parts:
            render_data["body"] = "No specific details provided for this notice. Please add content or link to a complaint/circular."

        template = self.env.get_template("official_notice_template.j2")
        return template.render(render_data)

    def generate_work_order(self, data: WorkOrder) -> str:
        render_data = data.dict(exclude_unset=True) # Start with provided work_order_data

        if data.complaint_id:
            complaint_details = self.complaint_service.get_complaint_by_id(int(data.complaint_id))
            
            if complaint_details:
                # Fill in missing work order fields from complaint details
                if not render_data.get("task_description") and complaint_details.description:
                    render_data["task_description"] = f"Work related to complaint ID {complaint_details.id}: {complaint_details.description}"
                if not render_data.get("assigned_department") and complaint_details.department:
                    render_data["assigned_department"] = complaint_details.department
                if not render_data.get("estimated_cost") and complaint_details.estimated_cost:
                    render_data["estimated_cost"] = complaint_details.estimated_cost
                if not render_data.get("suggested_actions") and complaint_details.suggested_actions:
                    render_data["suggested_actions"] = complaint_details.suggested_actions
                if not render_data.get("caller_name") and complaint_details.citizen_id:
                    render_data["caller_name"] = f"Citizen ID: {complaint_details.citizen_id}"
                if not render_data.get("caller_contact"):
                    render_data["caller_contact"] = "N/A (Contact via Complaint System)"

        # Ensure list fields are in a format Jinja can iterate over (e.g., list of strings)
        # The Pydantic model's validator already handles string to list conversion for retrieval, so no manual joining here

        template = self.env.get_template("work_order_template.j2")
        return template.render(render_data)


