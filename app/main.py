from fastapi import FastAPI
from app.routes import complaints, documents
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title='CivicDoc')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


app.include_router(complaints.router, prefix='/api')
app.include_router(documents.router, prefix='/api')


@app.get('/')
def health():
return {"ok": True}