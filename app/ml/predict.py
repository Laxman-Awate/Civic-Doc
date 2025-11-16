import joblib
from typing import Dict
from .config import settings


clf = None
tfidf = None




def load():
global clf, tfidf
if clf is None:
clf = joblib.load(settings.model_path)
if tfidf is None:
tfidf = joblib.load(settings.tfidf_path)




def predict(text: str) -> Dict:
load()
X = tfidf.transform([text])
pred = clf.predict(X)[0]
probs = clf.predict_proba(X)[0]
labels = clf.classes_.tolist()
prob_map = {labels[i]: float(probs[i]) for i in range(len(labels))}
return {"category": pred, "probs": prob_map}