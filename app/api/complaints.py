from fastapi import APIRouter, Body, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.complaint_model import Complaint, ComplaintCreate, ComplaintStatusUpdate # Import ComplaintStatusUpdate
from ..services.complaint_service import ComplaintService
from ..dependencies import get_current_active_user, has_role # Import dependencies
from ..models.sql_models import UserSQL # Import UserSQL to type hint current_user

router = APIRouter()

@router.post("/complaints", response_model=Complaint)
async def submit_complaint(
    complaint: ComplaintCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    # Only 'citizen' role can submit complaints
    if not has_role(["citizen"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only citizens can submit complaints")

    complaint_service = ComplaintService(db)
    new_complaint = complaint_service.create_complaint(complaint)
    return new_complaint

@router.get("/complaints/{complaint_id}", response_model=Complaint)
async def get_complaint_status(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user) # Require authentication
):
    # Both 'citizen' and 'department_admin' can view complaints
    if not has_role(["citizen", "department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view complaints")

    complaint_service = ComplaintService(db)
    complaint = complaint_service.get_complaint_by_id(complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.get("/complaints/sorted", response_model=list[Complaint])
async def get_sorted_complaints(
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user)
):
    if not has_role(["department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only department administrators can view sorted complaints")

    complaint_service = ComplaintService(db)
    # Assuming get_all_complaints can be modified to accept sorting parameters or we fetch all and sort here.
    # For simplicity, let's fetch all and sort in Python for now. We can optimize later if needed.
    complaints = complaint_service.get_all_complaints()
    
    # Sort complaints by urgency_score in descending order, handling None values gracefully
    sorted_complaints = sorted(complaints, key=lambda c: c.urgency_score if c.urgency_score is not None else -1, reverse=True)
    
    return sorted_complaints

@router.patch("/complaints/{complaint_id}/status", response_model=Complaint)
async def update_complaint_status(
    complaint_id: int,
    status_update: ComplaintStatusUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: UserSQL = Depends(get_current_active_user)
):
    if not has_role(["department_admin"])(current_user=current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only department administrators can update complaint status")

    complaint_service = ComplaintService(db)
    updated_complaint = complaint_service.update_complaint_status(complaint_id, status_update.status)
    
    if updated_complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return updated_complaint
