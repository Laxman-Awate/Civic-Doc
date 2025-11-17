import random

class ComplaintCategorizer:
    def __init__(self):
        # In a real application, load your TF-IDF vectorizer and XGBoost model here
        # For now, we'll use dummy logic
        pass

    def categorize_and_prioritize(self, description: str) -> dict:
        # Dummy categorization and prioritization logic
        categories = ["sewage", "garbage", "water", "roads", "electricity", "pollution", "safety"]
        departments = {
            "sewage": "Sanitation Dept",
            "garbage": "Sanitation Dept",
            "water": "Water Board",
            "roads": "PWD",
            "electricity": "Electricity Dept",
            "pollution": "Environment Dept",
            "safety": "Police Dept"
        }
        
        predicted_category = random.choice(categories)
        urgency_score = random.randint(0, 100)
        assigned_department = departments.get(predicted_category, "General Dept")

        return {
            "category": predicted_category,
            "urgency_score": urgency_score,
            "department": assigned_department
        }




