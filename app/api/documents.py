from fastapi import APIRouter, UploadFile, File, HTTPException, status, Body, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..db import get_db
from ..services.pdf_processing_service import PdfProcessingService
from ..services.document_generation_service import DocumentGenerationService
from ..services.complaint_service import ComplaintService # Import ComplaintService
from ..models.circular_model import Circular, CircularCreate
from ..models.document_models import RTIDocument, SchemeApplication, OfficialNotice, WorkOrder
from ..dependencies import get_current_active_user, has_role
from ..models.sql_models import UserSQL
from typing import List, Dict # Import Dict for the response model

router = APIRouter()

@router.post("/upload-circular/", response_model=Circular)
async def upload_circular(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    if not has_role(["department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only department administrators can upload circulars")

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        pdf_processing_service = PdfProcessingService(db)
        pdf_content = await file.read()
        circular_data = pdf_processing_service.save_circular_data(file.filename, pdf_content)
        return circular_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

@router.get("/circulars", response_model=List[Circular])
async def get_all_circulars(
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    # Both citizens and department admins should be able to view circulars
    if not has_role(["citizen", "department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view circulars")

    try:
        pdf_processing_service = PdfProcessingService(db)
        circulars = pdf_processing_service.get_all_circulars()
        return circulars
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve circulars: {e}")

@router.post("/generate-rti", response_class=HTMLResponse)
async def generate_rti(
    rti_data: RTIDocument = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    if not has_role(["citizen", "department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to generate RTI documents")

    try:
        doc_generation_service = DocumentGenerationService(db)
        document_content = doc_generation_service.generate_rti_document(rti_data)
        return HTMLResponse(content=document_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate RTI document: {e}")

@router.post("/generate-scheme-application", response_class=HTMLResponse)
async def generate_scheme_application(
    app_data: SchemeApplication = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    if not has_role(["citizen", "department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to generate scheme applications")

    try:
        doc_generation_service = DocumentGenerationService(db)
        document_content = doc_generation_service.generate_scheme_application(app_data)
        return HTMLResponse(content=document_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scheme application: {e}")

@router.post("/generate-official-notice", response_class=HTMLResponse)
async def generate_official_notice(
    notice_data: OfficialNotice = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    if not has_role(["department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only department administrators can generate official notices")

    try:
        doc_generation_service = DocumentGenerationService(db)
        document_content = doc_generation_service.generate_official_notice(notice_data)
        return HTMLResponse(content=document_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate official notice: {e}")

@router.post("/generate-work-order", response_model=Dict[str, str]) # Change response_class to response_model for JSON
async def generate_work_order(
    work_order_data: WorkOrder = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    if not has_role(["department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only department administrators can generate work orders")

    try:
        doc_generation_service = DocumentGenerationService(db)
        complaint_service = ComplaintService(db) # Initialize ComplaintService

        if work_order_data.complaint_id:
            complaint = complaint_service.get_complaint_by_id(int(work_order_data.complaint_id))
            if complaint:
                # Pre-fill work_order_data from complaint details
                if not work_order_data.task_description and complaint.description:
                    work_order_data.task_description = f"Work related to complaint ID {complaint.id}: {complaint.description}"
                if not work_order_data.assigned_department and complaint.department:
                    work_order_data.assigned_department = complaint.department
                if not work_order_data.estimated_cost and complaint.estimated_cost:
                    work_order_data.estimated_cost = complaint.estimated_cost
                if not work_order_data.suggested_actions and complaint.suggested_actions:
                    work_order_data.suggested_actions = complaint.suggested_actions
                # Add caller_name and caller_contact from complaint if available
                # Assuming citizen_id can be used as caller_name for now, and no direct contact info in Complaint model
                if not work_order_data.caller_name and complaint.citizen_id:
                    work_order_data.caller_name = f"Citizen ID: {complaint.citizen_id}"
                # No direct caller_contact in Complaint model, leaving empty for now or setting a placeholder
                if not work_order_data.caller_contact:
                    work_order_data.caller_contact = "N/A (Contact via Complaint System)"

        document_content = doc_generation_service.generate_work_order(work_order_data)
        return {"generated_html": document_content, **work_order_data.dict(exclude_unset=True)} # Return JSON
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate work order: {e}")
