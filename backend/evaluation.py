# evaluation.py
import time
import re
from typing import List, Dict
from search_engine import search_tfidf, search_jaccard, search_hybrid, preprocess_query
import json

def _normalize_text(s: str):
    if not s: return ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return s

def _determine_relevant_docs(query: str, docs):
    # naive automatic relevant set: any doc whose title/category/asal_daerah contains any query token
    q_clean, q_tokens = preprocess_query(query)
    relevant = set()
    for doc in docs:
        text = " ".join([
            str(doc.get("judul","")),
            str(doc.get("kategori","")),
            str(doc.get("asal_daerah",""))
        ]).lower()
        for t in q_tokens:
            if t in text:
                relevant.add(doc.get("no"))
                break
    return relevant

def precision_recall_f1(relevant:set, retrieved:List[int]):
    retrieved_set = set(retrieved)
    tp = len(retrieved_set & relevant)
    fp = len(retrieved_set - relevant)
    fn = len(relevant - retrieved_set)
    precision = tp / (tp + fp) if (tp+fp)>0 else 0.0
    recall = tp / (tp + fn) if (tp+fn)>0 else 0.0
    f1 = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0.0
    return precision, recall, f1

# main evaluate function
def evaluate(query: str, top_k: int = 10):
    # load docs to compute relevant set (read preprocessed file)
    import json, pathlib
    BASE = pathlib.Path(__file__).resolve().parent
    DATA_CLEAN = BASE / "data_clean"
    docs = json.load(open(DATA_CLEAN / "preprocessed_dataset.json", encoding="utf-8"))

    relevant = _determine_relevant_docs(query, docs)

    t0 = time.time()
    tfidf_res = search_tfidf(query, top_k=top_k)
    t1 = time.time()
    jacc_res = search_jaccard(query, top_k=top_k)
    t2 = time.time()
    hybrid_res = search_hybrid(query, top_k=top_k)
    t3 = time.time()

    tfidf_ids = [r["no"] for r in tfidf_res]
    jacc_ids = [r["no"] for r in jacc_res]
    hybrid_ids = [r["no"] for r in hybrid_res]

    p_t, r_t, f1_t = precision_recall_f1(relevant, tfidf_ids)
    p_j, r_j, f1_j = precision_recall_f1(relevant, jacc_ids)
    p_h, r_h, f1_h = precision_recall_f1(relevant, hybrid_ids)

    result = {
        "query": query,
        "top_k": top_k,
        "runtime": {
            "tfidf": t1 - t0,
            "jaccard": t2 - t1,
            "hybrid": t3 - t2
        },
        "tfidf": {"precision": p_t, "recall": r_t, "f1": f1_t},
        "jaccard": {"precision": p_j, "recall": r_j, "f1": f1_j},
        "hybrid": {"precision": p_h, "recall": r_h, "f1": f1_h},
        "counts": {
            "relevant_count": len(relevant)
        }
    }
    return result