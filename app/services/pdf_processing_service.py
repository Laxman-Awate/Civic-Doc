import fitz  # PyMuPDF
import pytesseract # python-tesseract
from PIL import Image
import io
import re
import json

from sqlalchemy.orm import Session
from ..models.circular_model import Circular, CircularCreate, ExtractedRule
from ..models.sql_models import CircularSQL
from ..services.multilingual_service import MultilingualService
from typing import List, Optional

class PdfProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.multilingual_service = MultilingualService()

    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        doc = fitz.open(pdf_file_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
            
            if not text.strip():
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                text += pytesseract.image_to_string(img)
        doc.close()
        return text

    def process_circular_nlp(self, text: str) -> dict:
        detected_language = self.multilingual_service.detect_language(text)
        content_summary = self.multilingual_service.summarize_text(text, detected_language)
        
        extracted_rules: List[ExtractedRule] = [
            ExtractedRule(rule_text="Rule 1: All citizens must apply by a certain date.", keywords=["apply", "date"]),
            ExtractedRule(rule_text="Rule 2: Eligibility requires proof of residency.", keywords=["eligibility", "residency"])
        ]
        eligibility_criteria = "Dummy eligibility: Must be a resident of the city."
        deadlines = "Dummy deadline: December 31, 2025."

        return {
            "content_summary": content_summary,
            "language": detected_language,
            "extracted_rules": extracted_rules,
            "eligibility_criteria": eligibility_criteria,
            "deadlines": deadlines
        }

    def save_circular_data(self, filename: str, pdf_content: bytes) -> Circular:
        temp_pdf_path = f"data/{filename}"
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_content)

        extracted_text = self.extract_text_from_pdf(temp_pdf_path)
        nlp_results = self.process_circular_nlp(extracted_text)

        circular_data = CircularCreate(
            filename=filename,
            content_summary=nlp_results["content_summary"],
            language=nlp_results["language"],
            extracted_rules=nlp_results["extracted_rules"],
            eligibility_criteria=nlp_results["eligibility_criteria"],
            deadlines=nlp_results["deadlines"]
        )

        db_circular = CircularSQL(**circular_data.to_sql_dict())

        self.db.add(db_circular)
        self.db.commit()
        self.db.refresh(db_circular)

        return Circular(**db_circular.__dict__)

    def get_circular_by_id(self, circular_id: int) -> Optional[Circular]:
        circular_data = self.db.query(CircularSQL).filter(CircularSQL.id == circular_id).first()
        if circular_data:
            circular_dict = circular_data.__dict__
            # The Pydantic model Circular has a validator for extracted_rules
            # that handles deserialization from string to List[ExtractedRule].
            # So, we can remove the manual parsing here and let the model handle it.
            return Circular(**circular_dict)
        return None

    def get_all_circulars(self) -> List[Circular]:
        circulars_data = self.db.query(CircularSQL).all()
        return [Circular(**circular_data.__dict__) for circular_data in circulars_data]
