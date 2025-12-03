import json
import math
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import re, string

# Sastrawi for query preprocessing (same as preprocessing pipeline)
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"
MODELS_DIR = BASE_DIR / "models"
PREPROCESSED_FILE = DATA_CLEAN / "preprocessed_dataset.json"
INVERTED_FILE = DATA_CLEAN / "inverted_index.json"
TFIDF_VOCAB_FILE = MODELS_DIR / "tfidf_vocab.json"
TFIDF_MATRIX_NPZ = MODELS_DIR / "tfidf_matrix.npz"
TFIDF_MODEL_PKL = MODELS_DIR / "tfidf_vectorizer.pkl"

# Load artifacts (lazy load)
_docs = None
_inverted = None
_vectorizer = None
_tfidf_matrix = None

# Preprocess resources
_factory_stop = StopWordRemoverFactory()
_stop_sastrawi = set(_factory_stop.get_stop_words())
_stop_custom = set([
    "yang","dan","di","ke","dari","dalam","adalah","atau","untuk","dengan",
    "pada","juga","bahwa","sebagai","oleh","karena","itu","ini","antara",
    "agar","setelah","serta","lebih","tidak","ada","merupakan","hingga",
    "ketika","para","saat","namun","bagi","yaitu","yakni","kita","kami",
    "mereka","ia","dia","sudah","belum","masih","jadi","pun","tanpa",
    "tersebut","suatu","sebuah","digunakan","berasal","daerah","tradisional"
])
_stopwords = _stop_sastrawi.union(_stop_custom)
_stemmer = StemmerFactory().create_stemmer()

def _ensure_loaded():
    global _docs, _inverted, _vectorizer, _tfidf_matrix
    if _docs is None:
        _docs = json.load(open(PREPROCESSED_FILE, encoding="utf-8"))
    if _inverted is None and INVERTED_FILE.exists():
        _inverted = json.load(open(INVERTED_FILE, encoding="utf-8"))
    if _vectorizer is None:
        import pickle
        _vectorizer = pickle.load(open(TFIDF_MODEL_PKL, "rb"))
    if _tfidf_matrix is None:
        _tfidf_matrix = sparse.load_npz(TFIDF_MATRIX_NPZ)

def clean_text_for_query(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"&\w+;", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_query(text: str):
    text = clean_text_for_query(text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in _stopwords]
    tokens = [_stemmer.stem(t) for t in tokens]
    return " ".join(tokens), tokens

# ---------------- TF-IDF SEARCH ----------------
def search_tfidf(query: str, top_k: int = 10):
    _ensure_loaded()
    q_clean, _ = preprocess_query(query)
    q_vec = _vectorizer.transform([q_clean])
    sims = cosine_similarity(q_vec, _tfidf_matrix).flatten()
    idx = sims.argsort()[::-1][:top_k]
    results = []
    for i in idx:
        doc = _docs[i]
        results.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul"),
            "kategori": doc.get("kategori"),
            "asal_daerah": doc.get("asal_daerah"),
            "link": doc.get("link"),
            "gambar": doc.get("gambar"),
            "score_tfidf": float(sims[i])
        })
    return results

# ---------------- JACCARD SEARCH ----------------
def _jaccard_score(token_query: List[str], token_doc: List[str]):
    set_q = set(token_query)
    set_d = set(token_doc)
    if not set_q and not set_d: return 0.0
    return len(set_q & set_d) / len(set_q | set_d)

def search_jaccard(query: str, top_k: int = 10):
    _ensure_loaded()
    _, q_tokens = preprocess_query(query)
    scores = []
    for i, doc in enumerate(_docs):
        doc_tokens = doc.get("tokens", [])
        sc = _jaccard_score(q_tokens, doc_tokens)
        scores.append((i, sc))
    scores.sort(key=lambda x: x[1], reverse=True)
    results = []
    for i, sc in scores[:top_k]:
        doc = _docs[i]
        results.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul"),
            "kategori": doc.get("kategori"),
            "asal_daerah": doc.get("asal_daerah"),
            "link": doc.get("link"),
            "gambar": doc.get("gambar"),
            "score_jaccard": float(sc)
        })
    return results

# ---------------- HYBRID ----------------
def search_hybrid(query: str, top_k: int = 10, w_tfidf: float = 0.5, w_jaccard: float = 0.5):
    _ensure_loaded()
    # compute both (we'll compute vectorized sims and per-doc jaccard)
    q_clean, q_tokens = preprocess_query(query)
    q_vec = _vectorizer.transform([q_clean])
    sims = cosine_similarity(q_vec, _tfidf_matrix).flatten()
    # normalize tfidf to 0..1
    if sims.max() > 0:
        sims_norm = sims / sims.max()
    else:
        sims_norm = sims
    # jaccard scores
    j_scores = np.zeros(len(_docs))
    for i, doc in enumerate(_docs):
        j_scores[i] = _jaccard_score(q_tokens, doc.get("tokens", []))
    if j_scores.max() > 0:
        j_norm = j_scores / j_scores.max()
    else:
        j_norm = j_scores
    final = (w_tfidf * sims_norm) + (w_jaccard * j_norm)
    idx = np.argsort(final)[::-1][:top_k]
    results = []
    for i in idx:
        doc = _docs[i]
        results.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul"),
            "kategori": doc.get("kategori"),
            "asal_daerah": doc.get("asal_daerah"),
            "link": doc.get("link"),
            "gambar": doc.get("gambar"),
            "score_tfidf": float(sims_norm[i]),
            "score_jaccard": float(j_norm[i]),
            "score_final": float(final[i])
        })
    return results