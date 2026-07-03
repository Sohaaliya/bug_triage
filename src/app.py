import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="AI Bug Triage and Resolution Assistant API", version="1.0")

# Load models and pipelines
try:
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    severity_model = joblib.load("models/severity_model.pkl")
    category_model = joblib.load("models/category_model.pkl")
    severity_encoder = joblib.load("models/severity_encoder.pkl")
    category_encoder = joblib.load("models/category_encoder.pkl")
except Exception as e:
    print(f"Warning: Models not loaded. Please run training script first. Details: {e}")

class BugRequest(BaseModel):
    Bug_Title: str
    Bug_Description: str

class TriageResponse(BaseModel):
    predicted_severity: str
    predicted_category: str
    suggested_priority: str
    recommended_action: str
    estimated_resolution_time_hours: int

# Rule engine/knowledge map for resolutions
RESOLUTION_MAP = {
    'Authentication': {
        'action': 'Verify redirect rules, rotate authentication key variables, and secure cookie properties.',
        'hours': {'Critical': 4, 'High': 16, 'Medium': 48, 'Low': 120}
    },
    'Database': {
        'action': 'Expand connection pool limits, verify index coverage, and optimize locking order.',
        'hours': {'Critical': 6, 'High': 18, 'Medium': 48, 'Low': 120}
    },
    'API': {
        'action': 'Inject request schema validation, adjust rate limit parameters, and add CORS headers.',
        'hours': {'Critical': 4, 'High': 12, 'Medium': 36, 'Low': 96}
    },
    'UI': {
        'action': 'Fix hook dependencies arrays, resolve grid viewport CSS, and align dialog wrappers.',
        'hours': {'Critical': 6, 'High': 18, 'Medium': 48, 'Low': 110}
    },
    'Network': {
        'action': 'Verify DNS forwarders, update Ingress rules, and refresh PEER routing maps.',
        'hours': {'Critical': 3, 'High': 12, 'Medium': 36, 'Low': 96}
    },
    'Security': {
        'action': 'Sanitize user string parameters, mask credentials in logs, and apply parameter binding.',
        'hours': {'Critical': 2, 'High': 10, 'Medium': 24, 'Low': 72}
    }
}

PRIORITY_MAP = {
    'Critical': 'P1',
    'High': 'P2',
    'Medium': 'P3',
    'Low': 'P4'
}

@app.post("/triage", response_model=TriageResponse)
def triage_bug(request: BugRequest):
    if not vectorizer or not severity_model or not category_model:
        raise HTTPException(status_code=500, detail="Inference models are not loaded on server.")
    
    # Preprocess text input
    input_text = f"{request.Bug_Title} {request.Bug_Description}"
    vectorized_input = vectorizer.transform([input_text])
    
    # Predict Severity
    severity_pred_encoded = severity_model.predict(vectorized_input)[0]
    severity_class = severity_encoder.inverse_transform([severity_pred_encoded])[0]
    
    # Predict Category
    category_pred_encoded = category_model.predict(vectorized_input)[0]
    category_class = category_encoder.inverse_transform([category_pred_encoded])[0]
    
    # Generate Resolution Advice
    triage_info = RESOLUTION_MAP.get(
        category_class, 
        {
            'action': 'Investigate configurations and dependencies inside logs.',
            'hours': {'Critical': 4, 'High': 16, 'Medium': 48, 'Low': 120}
        }
    )
    
    priority = PRIORITY_MAP.get(severity_class, 'P3')
    action = triage_info['action']
    est_hours = triage_info['hours'].get(severity_class, 48)
    
    return TriageResponse(
        predicted_severity=severity_class,
        predicted_category=category_class,
        suggested_priority=priority,
        recommended_action=action,
        estimated_resolution_time_hours=est_hours
    )

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "AI Bug Triage Assistant"}