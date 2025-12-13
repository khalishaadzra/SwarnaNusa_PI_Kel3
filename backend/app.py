from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from scipy import sparse
import pickle
from pathlib import Path
from evaluation import evaluate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from search_engine import preprocess_query

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"
MODELS_DIR = BASE_DIR / "models"

# Load docs
DOCS = json.load(open(DATA_CLEAN / "preprocessed_dataset.json", encoding="utf-8"))

# Load TF-IDF vectorizer & matrix
try:
    VECTORIZER = pickle.load(open(MODELS_DIR / "tfidf_vectorizer.pkl", "rb"))
except Exception:
    # fallback: build a vectorizer from saved vocabulary if .pkl missing
    vocab_path = MODELS_DIR / "tfidf_vocab.json"
    if vocab_path.exists():
        vocab = json.load(open(vocab_path, encoding="utf-8"))
        # sklearn expects vocabulary mapping token->feature_index
        VECTORIZER = TfidfVectorizer(vocabulary=vocab)
    else:
        raise

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

# --- HELPER: Check if document contains ALL query unigrams (AND logic, skip bigrams) ---
def _doc_contains_all_tokens(doc_tokens, query_tokens):
    """Check if doc_tokens contain ALL unigram tokens from query_tokens (AND matching).
    Ignores bigrams since documents don't store them as separate tokens."""
    if not query_tokens:
        return True
    doc_set = set(doc_tokens)
    # Only check unigrams (tokens without space), skip bigrams
    unigrams = [t for t in query_tokens if ' ' not in t]
    if not unigrams:
        return True
    return all(token in doc_set for token in unigrams)

# --- FULL SEARCH FUNCTION (TF-IDF + Jaccard + Combined with AND logic) ---
def search_full(query, mode="combined", top_k=None):

    # Use the same preprocessing as the search engine (stopwords, stemmer, bigrams)
    q_clean, q_tokens = preprocess_query(query)

    # Filter out empty queries
    if not q_tokens:
        return []

    # TF-IDF vector untuk query (use cosine similarity for comparable scores)
    q_vec = VECTORIZER.transform([q_clean])
    tfidf_scores = cosine_similarity(q_vec, X_TFIDF).flatten()

    results = []
    for i, doc in enumerate(DOCS):
        d_tokens = doc["tokens"]  # dari preprocessed_dataset.json

        # --- AND LOGIC: Only include docs that contain ALL query tokens ---
        if not _doc_contains_all_tokens(d_tokens, q_tokens):
            continue

        jaccard_score = jaccard_similarity(q_tokens, d_tokens)
        tfidf_score = float(tfidf_scores[i])

        # combined score
        combined_score = 0.5 * tfidf_score + 0.5 * jaccard_score

        # Apply minimum threshold to filter out low-relevance docs
        if combined_score >= 0.05:
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

    # Apply top_k limit only if specified
    if top_k is not None:
        return results[:top_k]
    return results

# --- ROUTES ---
@app.get("/")
def home():
    return {"status": "OK", "message": "Search API running"}

@app.get("/search")
def search_api(q: str, mode: str = "combined", top_k: int | None = None):
    results = search_full(q, mode, top_k)
    return {"query": q, "mode": mode, "results": results}

@app.get("/evaluate")
def evaluate_api(q: str, top_k: int | None = None):
    result = evaluate(q, top_k)
    return result