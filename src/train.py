import joblib
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.metrics import accuracy_score

def train_models(processed_dir="data/processed"):
    # Load processed matrices
    X_train, y_train_sev, y_train_cat, y_train_tech, y_train_mod, y_train_env = joblib.load(f"{processed_dir}/train_data.pkl")
    X_test, y_test_sev, y_test_cat, y_test_tech, y_test_mod, y_test_env = joblib.load(f"{processed_dir}/test_data.pkl")
    
    # Load Encoders
    severity_encoder = joblib.load("models/severity_encoder.pkl")
    category_encoder = joblib.load("models/category_encoder.pkl")
    tech_encoder = joblib.load("models/tech_encoder.pkl")
    module_encoder = joblib.load("models/module_encoder.pkl")
    env_encoder = joblib.load("models/env_encoder.pkl")
    
    mlflow.set_experiment("Bug_Triage_Models")
    
    # Helper function to train and log each target model
    def train_and_log(model_name, X_tr, y_tr, X_te, y_te, num_classes, encoder, model_save_path):
        with mlflow.start_run(run_name=model_name):
            print(f"Training {model_name}...")
            model = xgb.XGBClassifier(
                max_depth=6, 
                n_estimators=100, 
                learning_rate=0.1, 
                objective='multi:softprob',
                num_class=num_classes,
                random_state=42
            )
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            acc = accuracy_score(y_te, preds)
            
            mlflow.log_param("max_depth", 6)
            mlflow.log_param("n_estimators", 100)
            mlflow.log_metric("accuracy", acc)
            mlflow.xgboost.log_model(model, f"{model_name.lower()}_model")
            joblib.dump(model, model_save_path)
            print(f"{model_name} Accuracy: {acc:.4f}\n")
            
    # Train all 5 classifiers
    train_and_log("Severity_Model", X_train, y_train_sev, X_test, y_test_sev, len(severity_encoder.classes_), severity_encoder, "models/severity_model.pkl")
    train_and_log("Category_Model", X_train, y_train_cat, X_test, y_test_cat, len(category_encoder.classes_), category_encoder, "models/category_model.pkl")
    train_and_log("Technology_Model", X_train, y_train_tech, X_test, y_test_tech, len(tech_encoder.classes_), tech_encoder, "models/technology_model.pkl")
    train_and_log("Module_Model", X_train, y_train_mod, X_test, y_test_mod, len(module_encoder.classes_), module_encoder, "models/module_model.pkl")
    train_and_log("Environment_Model", X_train, y_train_env, X_test, y_test_env, len(env_encoder.classes_), env_encoder, "models/environment_model.pkl")

if __name__ == "__main__":
    train_models()