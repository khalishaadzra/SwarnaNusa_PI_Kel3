import json
import math
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import re, string

# Sastrawi
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"
MODELS_DIR = BASE_DIR / "models"
PREPROCESSED_FILE = DATA_CLEAN / "preprocessed_dataset.json"
INVERTED_FILE = DATA_CLEAN / "inverted_index.json"
TFIDF_MODEL_PKL = MODELS_DIR / "tfidf_vectorizer.pkl"
TFIDF_MATRIX_NPZ = MODELS_DIR / "tfidf_matrix.npz"

# Lazy loaded
_docs = None
_vectorizer = None
_tfidf_matrix = None
_inverted = None

# Preprocess
_stop_sastrawi = set(StopWordRemoverFactory().get_stop_words())
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


# ---------------------------------------------------
# LOAD
# ---------------------------------------------------
def _ensure_loaded():
    global _docs, _vectorizer, _tfidf_matrix, _inverted
    if _docs is None:
        _docs = json.load(open(PREPROCESSED_FILE, encoding="utf-8"))
    if _inverted is None and INVERTED_FILE.exists():
        _inverted = json.load(open(INVERTED_FILE, encoding="utf-8"))
    if _vectorizer is None:
        import pickle
        try:
            _vectorizer = pickle.load(open(TFIDF_MODEL_PKL, "rb"))
        except Exception:
            # fallback: construct vectorizer from saved vocab if pkl missing
            vocab_path = MODELS_DIR / "tfidf_vocab.json"
            if vocab_path.exists():
                from sklearn.feature_extraction.text import TfidfVectorizer
                vocab = json.load(open(vocab_path, encoding="utf-8"))
                _vectorizer = TfidfVectorizer(vocabulary=vocab)
            else:
                raise
    if _tfidf_matrix is None:
        _tfidf_matrix = sparse.load_npz(TFIDF_MATRIX_NPZ)


# ---------------------------------------------------
# CLEANING
# ---------------------------------------------------
def clean_text_for_query(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------
# PREPROCESS + BIGRAM
# ---------------------------------------------------
def preprocess_query(text: str):
    text = clean_text_for_query(text)
    tokens = text.split()

    tokens = [t for t in tokens if t not in _stopwords]
    tokens = [_stemmer.stem(t) for t in tokens]

    # BIGRAMS
    bigrams = []
    for i in range(len(tokens) - 1):
        bigram = tokens[i] + " " + tokens[i+1]
        bigrams.append(bigram)

    all_tokens = tokens + bigrams
    return " ".join(all_tokens), all_tokens


# ---------------------------------------------------
# HELPER: AND LOGIC - ensure doc contains all query UNIGRAMS (not bigrams)
# ---------------------------------------------------
def _doc_contains_all_tokens(doc_tokens: List[str], query_tokens: List[str]) -> bool:
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


# ---------------------------------------------------
# TF-IDF SEARCH
# ---------------------------------------------------
def search_tfidf(query: str, top_k: Optional[int] = None):
    _ensure_loaded()
    q_clean, q_tokens = preprocess_query(query)
    
    # Return empty if no query tokens
    if not q_tokens:
        return []
    
    q_vec = _vectorizer.transform([q_clean])

    sims = cosine_similarity(q_vec, _tfidf_matrix).flatten()

    # NORMALIZE 0–100
    if sims.max() > 0:
        sims_norm = (sims / sims.max()) * 100
    else:
        sims_norm = sims

    # CATEGORY BOOSTING
    ql = query.lower()

    for i, doc in enumerate(_docs):
        kat = doc.get("kategori", "").lower()

        if "pakaian" in ql and kat == "pakaian":
            sims_norm[i] += 20
        if ("tarian" in ql or "tari" in ql) and kat == "tarian":
            sims_norm[i] += 20
        if ("musik" in ql or "alat musik" in ql) and kat == "alat musik":
            sims_norm[i] += 20

    # AND LOGIC: keep only documents containing ALL query tokens AND score >= 5
    results = []
    for i, doc in enumerate(_docs):
        if sims_norm[i] >= 5 and _doc_contains_all_tokens(doc.get("tokens", []), q_tokens):
            results.append((i, sims_norm[i]))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    if top_k is not None:
        results = results[:top_k]

    # Format output
    formatted = []
    for i, score in results:
        doc = _docs[i]
        formatted.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul", ""),
            "kategori": doc.get("kategori", ""),
            "asal_daerah": doc.get("asal_daerah", ""),
            "link": doc.get("link", ""),
            "gambar": doc.get("gambar", ""),
            "score_tfidf": float(score)
        })
    return formatted


# ---------------------------------------------------
# JACCARD
# ---------------------------------------------------
def _jaccard_score(qa: List[str], db: List[str]):
    s1 = set(qa)
    s2 = set(db)
    if not s1 and not s2:
        return 0
    return len(s1 & s2) / len(s1 | s2)


def search_jaccard(query: str, top_k: Optional[int] = None):
    _ensure_loaded()
    _, q_tokens = preprocess_query(query)

    # Return empty if no query tokens
    if not q_tokens:
        return []

    scores = []
    for i, doc in enumerate(_docs):
        tok = doc.get("tokens", [])
        
        # AND LOGIC: only compute score if doc contains ALL tokens
        if _doc_contains_all_tokens(tok, q_tokens):
            sc = _jaccard_score(q_tokens, tok)
            scores.append((i, sc))

    # If no docs match AND logic, return empty
    if not scores:
        return []

    # CATEGORY BOOSTING
    ql = query.lower()
    boosted_scores = []
    
    for idx_doc, sc in scores:
        doc = _docs[idx_doc]
        kat = doc.get("kategori", "").lower()

        if "pakaian" in ql and kat == "pakaian":
            sc += 0.2
        if ("tarian" in ql or "tari" in ql) and kat == "tarian":
            sc += 0.2
        if ("musik" in ql or "alat musik" in ql) and kat == "alat musik":
            sc += 0.2

        # Filter by minimum threshold
        if sc >= 0.1:
            boosted_scores.append((idx_doc, sc))

    if not boosted_scores:
        return []

    boosted_scores.sort(key=lambda x: x[1], reverse=True)
    max_j = boosted_scores[0][1]

    if top_k is not None:
        boosted_scores = boosted_scores[:top_k]

    results = []
    for i, sc in boosted_scores:
        doc = _docs[i]
        sc_norm = (sc / max_j) * 100 if max_j > 0 else sc
        results.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul", ""),
            "kategori": doc.get("kategori", ""),
            "asal_daerah": doc.get("asal_daerah", ""),
            "link": doc.get("link", ""),
            "gambar": doc.get("gambar", ""),
            "score_jaccard": float(sc_norm)
        })
    return results


def search_hybrid(query: str, top_k: Optional[int] = None, w_tfidf=0.5, w_jaccard=0.5):
    _ensure_loaded()

    q_clean, q_tokens = preprocess_query(query)
    
    # Return empty if no query tokens
    if not q_tokens:
        return []

    q_vec = _vectorizer.transform([q_clean])

    # TF-IDF sims
    sims = cosine_similarity(q_vec, _tfidf_matrix).flatten()
    sims_norm = (sims / sims.max()) if sims.max() > 0 else sims

    # Jaccard sims
    j_scores = np.array([_jaccard_score(q_tokens, d.get("tokens", [])) for d in _docs])
    j_norm = (j_scores / j_scores.max()) if j_scores.max() > 0 else j_scores

    # HYBRID (only for docs with AND logic match)
    final = np.zeros_like(sims_norm)
    for i, doc in enumerate(_docs):
        if _doc_contains_all_tokens(doc.get("tokens", []), q_tokens):
            final[i] = (w_tfidf * sims_norm[i]) + (w_jaccard * j_norm[i])

    # CATEGORY BOOSTING – BOOST BEFORE NORMALIZATION
    ql = query.lower()
    for i, doc in enumerate(_docs):
        if final[i] > 0:  # only boost docs that passed AND logic
            kat = doc.get("kategori", "").lower()

            if "pakaian" in ql and kat == "pakaian":
                final[i] += 0.3
            if ("tarian" in ql or "tari" in ql) and kat == "tarian":
                final[i] += 0.3
            if ("musik" in ql or "alat musik" in ql) and kat == "alat musik":
                final[i] += 0.3

    # NORMALIZE HYBRID 0–100 (only for positive scores)
    pos_idx = np.where(final > 0)[0]
    if pos_idx.size == 0:
        return []

    final_norm = np.zeros_like(final)
    if final[pos_idx].max() > 0:
        final_norm[pos_idx] = (final[pos_idx] / final[pos_idx].max()) * 100

    # Filter by minimum threshold and sort
    results_list = []
    for i in pos_idx:
        if final_norm[i] >= 5:
            results_list.append((i, final_norm[i]))

    results_list.sort(key=lambda x: x[1], reverse=True)

    if top_k is not None:
        results_list = results_list[:top_k]

    if not results_list:
        return []

    results = []
    for i, final_score in results_list:
        doc = _docs[i]
        results.append({
            "no": doc.get("no", i),
            "judul": doc.get("judul", ""),
            "kategori": doc.get("kategori", ""),
            "asal_daerah": doc.get("asal_daerah", ""),
            "link": doc.get("link", ""),
            "gambar": doc.get("gambar", ""),
            "score_tfidf": float(sims_norm[i] * 100),
            "score_jaccard": float(j_norm[i] * 100),
            "score_final": float(final_score)
        })

    return results