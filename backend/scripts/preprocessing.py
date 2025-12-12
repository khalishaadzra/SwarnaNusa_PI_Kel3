import re
import json
import string
import pandas as pd
from tqdm import tqdm
from pathlib import Path

# Sastrawi
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Folder data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CLEAN = BASE_DIR / "data_clean"
TOKENS_DIR = DATA_CLEAN / "tokens"

DATA_CLEAN.mkdir(exist_ok=True)
TOKENS_DIR.mkdir(exist_ok=True)

# ============================================================
# 1. LOAD DATASET GABUNGAN
# ============================================================

def load_dataset():
    file_path = DATA_CLEAN / "combined_dataset.json"
    df = pd.read_json(file_path, orient="records")
    print(f"📌 Loaded combined dataset: {len(df)} records")
    return df

# ============================================================
# 2. STOPWORDS
# ============================================================

factory_stop = StopWordRemoverFactory()
stop_sastrawi = set(factory_stop.get_stop_words())

stop_custom = set([
    "yang","dan","di","ke","dari","dalam","adalah","atau","untuk","dengan",
    "pada","juga","bahwa","sebagai","oleh","karena","itu","ini","antara",
    "agar","setelah","serta","lebih","tidak","ada","merupakan","hingga",
    "ketika","para","saat","namun","bagi","yaitu","yakni","kita","kami",
    "mereka","ia","dia","sudah","belum","masih","jadi","pun","tanpa",
    "tersebut","suatu","sebuah","digunakan","berasal","daerah","tradisional"
])

stopwords = stop_sastrawi.union(stop_custom)

# ============================================================
# 3. STEMMER
# ============================================================

stemmer = StemmerFactory().create_stemmer()

# ============================================================
# 4. CLEANING
# ============================================================

def clean_text(text: str):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"&\w+;", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ============================================================
# 5. TOKENS
# ============================================================

def tokenize(text):
    return text.split()

def remove_stopwords(tokens):
    return [t for t in tokens if t not in stopwords]

def apply_stemming(tokens):
    return [stemmer.stem(t) for t in tokens]

# ============================================================
# 6. PIPELINE UTAMA
# ============================================================

def preprocess_pipeline(text):
    text = clean_text(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = apply_stemming(tokens)
    clean_string = " ".join(tokens)
    return clean_string, tokens

# ============================================================
# 7. BUILD TEKS UNTUK SEARCH
# ============================================================

def build_text_column(df):
    df["teks"] = (
        df["judul"].astype(str) + " " +
        df["deskripsi"].astype(str) + " " +
        df["asal_daerah"].astype(str)
    )
    return df

# ============================================================
# 8. PREPROCESS SELURUH DATASET
# ============================================================

def preprocess_dataset():
    df = load_dataset()
    df = build_text_column(df)

    clean_list = []
    tokens_list = []

    print("\n🔄 Preprocessing dataset...\n")

    for i, t in tqdm(enumerate(df["teks"]), total=len(df), desc="Processing", colour="green"):
        clean_txt, tokens = preprocess_pipeline(t)

        clean_list.append(clean_txt)
        tokens_list.append(tokens)

        # Simpan tokens per dokumen → JSON
        with open(TOKENS_DIR / f"doc_{i}.json", "w", encoding="utf-8") as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)

    df["clean_text"] = clean_list
    df["tokens"] = tokens_list

    # Simpan dataset hasil preprocessing
    out_file = DATA_CLEAN / "preprocessed_dataset.json"
    json_text = df.to_json(orient="records", indent=2, force_ascii=False)
    json_text = json_text.replace("\\/", "/")  # Hapus escaped slash
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json_text)

    print(f"\n✅ Preprocessing selesai! Hasil disimpan di:\n- {out_file}\n- Folder tokens/: {TOKENS_DIR}")

    return df

# ============================================================
# 9. RUN
# ============================================================

if __name__ == "__main__":
    preprocess_dataset() 