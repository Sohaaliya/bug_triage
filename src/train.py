import joblib
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.metrics import classification_report, accuracy_score

def train_models(processed_dir="data/processed"):
    # Load processed matrices
    X_train, y_train_sev, y_train_cat = joblib.load(f"{processed_dir}/train_data.pkl")
    X_test, y_test_sev, y_test_cat = joblib.load(f"{processed_dir}/test_data.pkl")
    
    # Load Label Encoders
    severity_encoder = joblib.load("models/severity_encoder.pkl")
    category_encoder = joblib.load("models/category_encoder.pkl")
    
    mlflow.set_experiment("Bug_Triage_Models")
    
    # --- 1. Train Severity Predictor (XGBoost Classifier) ---
    with mlflow.start_run(run_name="Severity_Model"):
        print("Training Severity Prediction Model...")
        severity_model = xgb.XGBClassifier(
            max_depth=6, 
            n_estimators=100, 
            learning_rate=0.1, 
            objective='multi:softprob',
            num_class=len(severity_encoder.classes_),
            random_state=42
        )
        severity_model.fit(X_train, y_train_sev)
        
        # Predictions & Metrics
        preds = severity_model.predict(X_test)
        acc = accuracy_score(y_test_sev, preds)
        
        mlflow.log_param("max_depth", 6)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.xgboost.log_model(severity_model, "severity_xgboost_model")
        joblib.dump(severity_model, "models/severity_model.pkl")
        print(f"Severity Model Accuracy: {acc:.4f}")

    # --- 2. Train Category (Root Cause) Predictor ---
    with mlflow.start_run(run_name="Category_Model"):
        print("Training Category Prediction Model...")
        category_model = xgb.XGBClassifier(
            max_depth=6, 
            n_estimators=100, 
            learning_rate=0.1, 
            objective='multi:softprob',
            num_class=len(category_encoder.classes_),
            random_state=42
        )
        category_model.fit(X_train, y_train_cat)
        
        # Predictions & Metrics
        preds = category_model.predict(X_test)
        acc = accuracy_score(y_test_cat, preds)
        
        mlflow.log_param("max_depth", 6)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.xgboost.log_model(category_model, "category_xgboost_model")
        joblib.dump(category_model, "models/category_model.pkl")
        print(f"Category Model Accuracy: {acc:.4f}")

if __name__ == "__main__":
    train_models()