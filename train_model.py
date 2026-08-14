import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def train_and_save_model():
    data_path = os.path.join("data", "careers.csv")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    df = pd.read_csv(data_path)

    # ML Pipeline: TF-IDF + Logistic Regression
    X = df["skills_text"]
    y = df["career_title"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=1500)),
        ("clf", LogisticRegression(max_iter=1000, random_state=42))
    ])

    pipeline.fit(X, y)

    # Precompute and store metadata for the Streamlit App
    career_metadata = {}
    for _, row in df.iterrows():
        career_metadata[row["career_title"]] = {
            "core_skills": [s.strip() for s in row["core_skills"].split(",")],
            "bonus_skills": [s.strip() for s in row["bonus_skills"].split(",")],
            "salary_range": row["salary_range"],
            "difficulty": row["difficulty"]
        }

    # Bundle the model and data together
    model_payload = {
        "pipeline": pipeline,
        "career_metadata": career_metadata,
        "known_careers": list(pipeline.classes_)
    }

    joblib.dump(model_payload, "model.pkl")
    print(f"✅ Successfully trained on {len(df)} roles.")
    print("✅ Model and metadata saved to 'model.pkl'.")

if __name__ == "__main__":
    train_and_save_model()