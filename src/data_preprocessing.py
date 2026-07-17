import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

def preprocess_data(data_path="data/raw/bug_reports.csv", output_dir="data/processed"):
    # Load dataset
    df = pd.read_csv(data_path)
    
    # Fill empty text columns
    df['Bug_Title'] = df['Bug_Title'].fillna('')
    df['Bug_Description'] = df['Bug_Description'].fillna('')
    
    # Combine Title and Description as input feature
    df['input_text'] = df['Bug_Title'] + " " + df['Bug_Description']
    
    # Initialize Label Encoders
    severity_encoder = LabelEncoder()
    category_encoder = LabelEncoder()
    tech_encoder = LabelEncoder()
    module_encoder = LabelEncoder()
    env_encoder = LabelEncoder()
    
    # Fit and transform all targets
    df['severity_encoded'] = severity_encoder.fit_transform(df['Severity'])
    df['category_encoded'] = category_encoder.fit_transform(df['Root_Cause_Category'])
    df['tech_encoded'] = tech_encoder.fit_transform(df['Technology'])
    df['module_encoded'] = module_encoder.fit_transform(df['Module'])
    df['env_encoded'] = env_encoder.fit_transform(df['Environment'])
    
    # Train-test split (80% Train, 20% Test)
    X_train, X_test, y_train_sev, y_test_sev, y_train_cat, y_test_cat, y_train_tech, y_test_tech, y_train_mod, y_test_mod, y_train_env, y_test_env = train_test_split(
        df['input_text'], 
        df['severity_encoded'], 
        df['category_encoded'],
        df['tech_encoded'],
        df['module_encoded'],
        df['env_encoded'],
        test_size=0.2, 
        random_state=42
    )
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    # Save processed vectors and encoders
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
    joblib.dump(severity_encoder, "models/severity_encoder.pkl")
    joblib.dump(category_encoder, "models/category_encoder.pkl")
    joblib.dump(tech_encoder, "models/tech_encoder.pkl")
    joblib.dump(module_encoder, "models/module_encoder.pkl")
    joblib.dump(env_encoder, "models/env_encoder.pkl")
    
    # Save splits for tracking / training
    joblib.dump((X_train_vectorized, y_train_sev, y_train_cat, y_train_tech, y_train_mod, y_train_env), f"{output_dir}/train_data.pkl")
    joblib.dump((X_test_vectorized, y_test_sev, y_test_cat, y_test_tech, y_test_mod, y_test_env), f"{output_dir}/test_data.pkl")
    print("Preprocessing completed. Artifacts saved to models/ and data/processed/")

if __name__ == "__main__":
    preprocess_data()