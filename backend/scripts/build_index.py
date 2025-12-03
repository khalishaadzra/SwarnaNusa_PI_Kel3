# scripts/build_index.py
import json
import math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CLEAN = BASE_DIR / "data_clean"
TOKENS_DIR = DATA_CLEAN / "tokens"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

PREPROCESSED_FILE = DATA_CLEAN / "preprocessed_dataset.json"
INVERTED_FILE = DATA_CLEAN / "inverted_index.json"
TFIDF_VOCAB_FILE = MODELS_DIR / "tfidf_vocab.json"
TFIDF_MATRIX_NPZ = MODELS_DIR / "tfidf_matrix.npz"
TFIDF_MODEL_PKL = MODELS_DIR / "tfidf_vectorizer.pkl"

def load_docs():
    docs = json.load(open(PREPROCESSED_FILE, encoding="utf-8"))
    return docs

def build_inverted_index(docs):
    inverted = defaultdict(list)
    for doc in docs:
        doc_id = int(doc.get("no", doc.get("id", docs.index(doc))))
        tokens = doc.get("tokens", [])
        seen = set()
        for t in tokens:
            if t not in seen:
                inverted[t].append(doc_id)
                seen.add(t)
    # convert defaultdict->dict for JSON
    inverted = {k: v for k, v in inverted.items()}
    with open(INVERTED_FILE, "w", encoding="utf-8") as f:
        json.dump(inverted, f, ensure_ascii=False, indent=2)
    print(f"Saved inverted index → {INVERTED_FILE}")
    return inverted

def build_tfidf(docs):
    # use clean_text field as input for TF-IDF
    texts = [doc.get("clean_text", "") for doc in docs]
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), min_df=1)
    X = vectorizer.fit_transform(texts)  # sparse matrix
    # save vocab
    vocab = {k: int(v) for k, v in vectorizer.vocabulary_.items()}
    with open(TFIDF_VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
    # save sparse matrix (.npz)
    sparse.save_npz(TFIDF_MATRIX_NPZ, X)
    # save vectorizer (pickle) for future direct transform of query
    import pickle
    with open(TFIDF_MODEL_PKL, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Saved TF-IDF vocab → {TFIDF_VOCAB_FILE}")
    print(f"Saved TF-IDF matrix (.npz) → {TFIDF_MATRIX_NPZ}")
    print(f"Saved TF-IDF vectorizer (.pkl) → {TFIDF_MODEL_PKL}")
    return vectorizer, X

def main():
    print("Loading docs...")
    docs = load_docs()
    print(f"{len(docs)} docs loaded.")
    print("Building inverted index...")
    inverted = build_inverted_index(docs)
    print("Building TF-IDF...")
    vectorizer, X = build_tfidf(docs)
    print("Index and TF-IDF build finished.")

if __name__ == "__main__":
    main()