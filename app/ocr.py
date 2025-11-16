import pytesseract
from PIL import Image
import fitz # PyMuPDF
from io import BytesIO




def image_to_text(image_bytes: bytes) -> str:
img = Image.open(BytesIO(image_bytes))
return pytesseract.image_to_string(img, lang='eng')




def pdf_to_text(pdf_path: str) -> str:
text = []
doc = fitz.open(pdf_path)
for page in doc:
text.append(page.get_text())
return "\n".join(text)