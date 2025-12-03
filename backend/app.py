from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from scipy import sparse
import pickle
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"
MODELS_DIR = BASE_DIR / "models"

# Load docs
DOCS = json.load(open(DATA_CLEAN / "preprocessed_dataset.json", encoding="utf-8"))

# Load TF-IDF vectorizer & matrix
VECTORIZER = pickle.load(open(MODELS_DIR / "tfidf_vectorizer.pkl", "rb"))
X_TFIDF = sparse.load_npz(MODELS_DIR / "tfidf_matrix.npz")

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEARCH FUNCTION ---
def search_tfidf(query, top_k=10):
    q_vec = VECTORIZER.transform([query])
    scores = (X_TFIDF @ q_vec.T).toarray().ravel()
    idx = np.argsort(scores)[::-1][:top_k]
    results = []

    for i in idx:
        results.append({
            "score": float(scores[i]),
            "document": DOCS[i]
        })

    return results

# --- API ROUTES ---

@app.get("/")
def home():
    return {"status": "OK", "message": "Search API running"}

@app.get("/search")
def search_api(q: str, top_k: int = 10):
    results = search_tfidf(q, top_k)
    return {"query": q, "results": results}