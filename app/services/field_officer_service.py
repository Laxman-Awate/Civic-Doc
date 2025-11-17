from typing import List, Dict, Any

class FieldOfficerService:
    def __init__(self):
        # In a real application, load rules or models for action step suggestions here
        pass

    def suggest_action_steps(self, category: str, urgency_score: int, description: str) -> Dict[str, Any]:
        # Dummy logic for action steps based on category and urgency
        suggested_actions: List[str] = []
        tools_required: List[str] = []
        safety_notes: List[str] = []
        sla_hours: int = 24 # Default SLA

        if category == "roads":
            suggested_actions = ["Inspect pothole severity", "Arrange for repair crew", "Place warning signs"]
            tools_required = ["Measuring tape", "Chalk", "Safety cones"]
            safety_notes = ["Beware of traffic", "Wear high-visibility clothing"]
            sla_hours = 48 if urgency_score > 70 else 72
        elif category == "water":
            suggested_actions = ["Locate leak source", "Shut off water supply if necessary", "Repair pipe"]
            tools_required = ["Wrench set", "Pipe sealant", "Flashlight"]
            safety_notes = ["Risk of electrocution near water", "Ensure proper ventilation"]
            sla_hours = 12 if urgency_score > 80 else 24
        elif category == "electricity":
            suggested_actions = ["Isolate power supply", "Inspect faulty wiring", "Replace damaged components"]
            tools_required = ["Voltmeter", "Insulated gloves", "Wire strippers"]
            safety_notes = ["High voltage hazard", "Work only with power off"]
            sla_hours = 6 if urgency_score > 90 else 12
        else:
            suggested_actions = ["Assess the situation", "Take necessary immediate action"]
            tools_required = ["Basic toolkit"]
            safety_notes = ["Follow general safety guidelines"]
            sla_hours = 24

        return {
            "suggested_actions": suggested_actions,
            "tools_required": tools_required,
            "safety_notes": safety_notes,
            "sla_hours": sla_hours
        }




