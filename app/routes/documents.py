from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from app.models import DocumentRequest
from app.db import complaints_col


router = APIRouter()
env = Environment(loader=FileSystemLoader('app/templates'))


@router.post('/generate', response_class=HTMLResponse)
async def generate(req: DocumentRequest):
# simple document generation
template_name = 'rti_template.html' if req.doc_type=='rti' else 'workorder_template.html'
tmpl = env.get_template(template_name)
context = {"req": req.dict()}
if req.complaint_id:
c = await complaints_col.find_one({"_id": req.complaint_id})
context['complaint'] = c
html = tmpl.render(**context)
return HTMLResponse(content=html)