import time
import json
import pathlib
from typing import List, Optional

# --- PENTING: Import logika dari search_engine agar sinkron ---
# Kita gunakan fungsi _doc_contains_all_tokens agar cara menilai relevansinya
# sama persis dengan cara search engine mencari data.
from search_engine import search_tfidf, search_jaccard, search_hybrid, preprocess_query, _doc_contains_all_tokens

def _determine_relevant_docs(query: str, docs):
    """
    Menentukan Ground Truth (Kunci Jawaban).
    Dokumen dianggap relevan jika mengandung SEMUA token query (AND Logic),
    persis seperti cara kerja mesin pencari kita.
    """
    # 1. Preprocess query
    q_clean, q_tokens = preprocess_query(query)
    
    # Filter token kosong
    q_tokens = [t for t in q_tokens if t.strip() and ' ' not in t]
    
    if not q_tokens:
        return set()

    relevant = set()
    
    # 2. Cek database
    for doc in docs:
        # Ambil token yang sudah ada di database
        doc_tokens = doc.get("tokens", [])
        
        # Cek kesesuaian menggunakan logika yang sama dengan search engine
        if _doc_contains_all_tokens(doc_tokens, q_tokens):
            relevant.add(doc.get("no"))
            
    return relevant

def precision_recall_f1(relevant: set, retrieved: List[int]):
    retrieved_set = set(retrieved)
    
    # True Positive: Dokumen yang BENAR dan DITEMUKAN
    tp = len(retrieved_set & relevant)
    
    # Hitung metrik (dengan penanganan pembagian nol)
    precision = tp / len(retrieved_set) if len(retrieved_set) > 0 else 0.0
    recall = tp / len(relevant) if len(relevant) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1

def evaluate(query: str, top_k: Optional[int] = None):
    # 1. Load Dataset
    BASE = pathlib.Path(__file__).resolve().parent
    DATA_CLEAN = BASE / "data_clean"
    
    try:
        docs = json.load(open(DATA_CLEAN / "preprocessed_dataset.json", encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}

    # 2. Tentukan Kunci Jawaban (Ground Truth)
    relevant = _determine_relevant_docs(query, docs)

    # 3. Jalankan 3 Algoritma Search
    t0 = time.time()
    tfidf_res = search_tfidf(query, top_k)
    
    t1 = time.time()
    jacc_res = search_jaccard(query, top_k)
    
    t2 = time.time()
    hybrid_res = search_hybrid(query, top_k)
    
    t3 = time.time()

    # 4. Ambil ID Hasil
    tfidf_ids = [r["no"] for r in tfidf_res]
    jacc_ids = [r["no"] for r in jacc_res]
    hybrid_ids = [r["no"] for r in hybrid_res]

    # 5. Hitung Statistik
    p_t, r_t, f1_t = precision_recall_f1(relevant, tfidf_ids)
    p_j, r_j, f1_j = precision_recall_f1(relevant, jacc_ids)
    p_h, r_h, f1_h = precision_recall_f1(relevant, hybrid_ids)

    # 6. Return Hasil
    return {
        "query": query,
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