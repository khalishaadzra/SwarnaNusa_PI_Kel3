from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from scipy import sparse
import pickle
from pathlib import Path
from evaluation import evaluate

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

# --- JACCARD ---
def jaccard_similarity(q_tokens, d_tokens):
    set_q = set(q_tokens)
    set_d = set(d_tokens)
    if not set_q or not set_d:
        return 0
    return len(set_q & set_d) / len(set_q | set_d)

# --- FULL SEARCH FUNCTION (TF-IDF + Jaccard + Combined) ---
def search_full(query, mode="combined", top_k=10):

    # TF-IDF vector untuk query
    q_vec = VECTORIZER.transform([query])
    tfidf_scores = (X_TFIDF @ q_vec.T).toarray().ravel()

    # Token query
    q_tokens = query.lower().split()

    results = []
    for i, doc in enumerate(DOCS):
        d_tokens = doc["tokens"]  # dari preprocessed_dataset.json
        jaccard_score = jaccard_similarity(q_tokens, d_tokens)
        tfidf_score = float(tfidf_scores[i])

        # combined
        combined_score = 0.7 * tfidf_score + 0.3 * jaccard_score

        results.append({
            "document": doc,
            "tfidf_score": tfidf_score,
            "jaccard_score": jaccard_score,
            "combined_score": combined_score
        })

    # Sorting berdasarkan mode
    if mode == "tfidf":
        results.sort(key=lambda x: x["tfidf_score"], reverse=True)
    elif mode == "jaccard":
        results.sort(key=lambda x: x["jaccard_score"], reverse=True)
    else:  # default combined
        results.sort(key=lambda x: x["combined_score"], reverse=True)

    return results[:top_k]

# --- ROUTES ---
@app.get("/")
def home():
    return {"status": "OK", "message": "Search API running"}

@app.get("/search")
def search_api(q: str, mode: str = "combined", top_k: int = 10):
    results = search_full(q, mode, top_k)
    return {"query": q, "mode": mode, "results": results}

@app.get("/evaluate")
def evaluate_api(q: str, top_k: int = 10):
    result = evaluate(q, top_k)
    return result