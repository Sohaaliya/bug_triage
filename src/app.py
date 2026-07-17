import random
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="AI Bug Triage and Resolution Assistant API", version="1.0")

# Load models and pipelines
try:
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    severity_model = joblib.load("models/severity_model.pkl")
    category_model = joblib.load("models/category_model.pkl")
    tech_model = joblib.load("models/technology_model.pkl")
    module_model = joblib.load("models/module_model.pkl")
    env_model = joblib.load("models/environment_model.pkl")
    
    severity_encoder = joblib.load("models/severity_encoder.pkl")
    category_encoder = joblib.load("models/category_encoder.pkl")
    tech_encoder = joblib.load("models/tech_encoder.pkl")
    module_encoder = joblib.load("models/module_encoder.pkl")
    env_encoder = joblib.load("models/env_encoder.pkl")
except Exception as e:
    print(f"Warning: Models not loaded. Please run training script first. Details: {e}")

class BugRequest(BaseModel):
    Bug_Title: str
    Bug_Description: str

class TriageResponse(BaseModel):
    bug_id: str
    predicted_severity: str
    predicted_category: str
    predicted_technology: str
    predicted_module: str
    predicted_environment: str
    suggested_priority: str
    recommended_action: str
    estimated_resolution_time_hours: int

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
    
    # Predict Targets
    severity_pred = severity_model.predict(vectorized_input)[0]
    severity_class = severity_encoder.inverse_transform([severity_pred])[0]
    
    category_pred = category_model.predict(vectorized_input)[0]
    category_class = category_encoder.inverse_transform([category_pred])[0]
    
    tech_pred = tech_model.predict(vectorized_input)[0]
    tech_class = tech_encoder.inverse_transform([tech_pred])[0]
    
    module_pred = module_model.predict(vectorized_input)[0]
    module_class = module_encoder.inverse_transform([module_pred])[0]
    
    env_pred = env_model.predict(vectorized_input)[0]
    env_class = env_encoder.inverse_transform([env_pred])[0]
    
    # Generate Resolution Advice
    triage_info = RESOLUTION_MAP.get(
        category_class, 
        {
            'action': 'Investigate configuration parameters, dependency trees, and trace log metrics.',
            'hours': {'Critical': 4, 'High': 16, 'Medium': 48, 'Low': 120}
        }
    )
    
    priority = PRIORITY_MAP.get(severity_class, 'P3')
    action = triage_info['action']
    est_hours = triage_info['hours'].get(severity_class, 48)
    rand_id = f"BUG-{random.randint(10000, 99999)}"
    
    return TriageResponse(
        bug_id=rand_id,
        predicted_severity=severity_class,
        predicted_category=category_class,
        predicted_technology=tech_class,
        predicted_module=module_class,
        predicted_environment=env_class,
        suggested_priority=priority,
        recommended_action=action,
        estimated_resolution_time_hours=est_hours
    )

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("src/statics/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>AI Bug Triage Assistant API is running!</h1><p>Frontend static page not found at src/statics/index.html</p>")