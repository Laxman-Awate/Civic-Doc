from fastapi import APIRouter, HTTPException
from app.models import ComplaintCreate, ComplaintDB
from app.db import complaints_col
from app.ml.predict import predict
from app.utils import priority_score_from_probs, route_to_department


router = APIRouter()


@router.post('/complaints', response_model=ComplaintDB)
async def create_complaint(payload: ComplaintCreate):
# classify
res = predict(payload.message)
category = res['category']
probs = res['probs']
urgency_flag = 'urgent' in payload.message.lower() or max(probs.values())<0.4
severity_est = 5
score = priority_score_from_probs(probs, urgency_flag, severity_est)
routed = route_to_department(category)


doc = payload.dict()
doc.update({
'category': category,
'priority_score': score,
'urgency': 'high' if urgency_flag else 'normal',
'routed_to': routed,
'status': 'pending'
})
res = await complaints_col.insert_one(doc)
doc['id'] = str(res.inserted_id)
return doc


@router.get('/complaints/{cid}')
async def get_complaint(cid: str):
doc = await complaints_col.find_one({"_id": cid})
if not doc:
raise HTTPException(status_code=404, detail='Not found')
doc['id'] = str(doc['_id'])
return doc