from typing import Tuple


CATEGORIES = ["sewage","garbage","water","roads","electricity","pollution","safety"]
DEPARTMENTS = {
"sewage":"Sanitation Dept",
"garbage":"Sanitation Dept",
"water":"Water Board",
"roads":"PWD",
"electricity":"Electricity Dept",
"pollution":"Environment Dept",
"safety":"Police/Traffic"
}




def priority_score_from_probs(category_probs: dict, urgency_flag: bool, severity_est: int) -> int:
"""Compute 0-100 priority score. severity_est in 0-10."""
base = max(category_probs.values()) * 60 # category weight
urg = 30 if urgency_flag else 0
sev = (severity_est / 10) * 10
score = int(min(100, base + urg + sev))
return score




def route_to_department(category: str) -> str:
return DEPARTMENTS.get(category, "General Municipal Office")