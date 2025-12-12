import pandas as pd
import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR  # raw files are stored in the same `fix` folder in this workspace
CLEAN_DIR = BASE_DIR / "data_clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

def load_and_combine():
    print("🔄 Menggabungkan dataset...")

    # Load CSV
    def read_csv_tolerant(p):
        p = str(p)
        try:
            return pd.read_csv(p, encoding="utf-8", engine="python", on_bad_lines='skip')
        except Exception:
            cleaned = p + ".cleaned.csv"
            with open(p, "r", encoding="utf-8", errors="replace") as rf, open(cleaned, "w", encoding="utf-8") as wf:
                buf = ""
                for line in rf:
                    buf += line
                    if buf.count('"') % 2 == 0:
                        wf.write(buf)
                        buf = ""
                if buf:
                    wf.write(buf)
            return pd.read_csv(cleaned, encoding="utf-8", engine="python", on_bad_lines='skip')

    alat = read_csv_tolerant(RAW_DIR / "alat_musik_tradisional_indonesia.csv")
    pakaian = read_csv_tolerant(RAW_DIR / "pakaian_tradisional_indonesia.csv")
    tari = read_csv_tolerant(RAW_DIR / "tarian_tradisional_indonesia.csv")

    # Tambah kategori
    alat["kategori"] = "alat_musik"
    pakaian["kategori"] = "pakaian"
    tari["kategori"] = "tarian"

    # Canonical columns required in the final CSV
    canonical_cols = ["no", "judul", "deskripsi", "asal_daerah", "link", "gambar"]

    # Tambahkan kolom yang hilang (pastikan semua dataframe memiliki kolom yang dibutuhkan)
    for df_ in [alat, pakaian, tari]:
        if "cara_main" not in df_.columns:
            df_["cara_main"] = ""
        for c in ["no", "judul", "deskripsi", "asal_daerah", "link", "gambar"]:
            if c not in df_.columns:
                df_[c] = ""

    # Select/normalize to canonical columns for each dataframe
    def to_canonical(df):
        # prefer these candidate names for mapping
        mapping = {}
        cols = list(df.columns)
        lowermap = {c.lower(): c for c in cols}

        def pick(names):
            for n in names:
                if n in cols:
                    return n
                if n.lower() in lowermap:
                    return lowermap[n.lower()]
            return None

        mapping['judul'] = pick(['judul', 'title', 'nama'])
        mapping['deskripsi'] = pick(['deskripsi', 'konten_lengkap', 'konten', 'isi'])
        mapping['asal_daerah'] = pick(['asal_daerah', 'asal', 'daerah'])
        mapping['link'] = pick(['link', 'url', 'source'])
        mapping['gambar'] = pick(['gambar', 'image', 'img', 'foto'])

        out = pd.DataFrame()
        for col in canonical_cols:
            if col == 'no':
                # fill with empty for now; we'll renumber later
                out['no'] = ''
                continue
            src = mapping.get(col)
            if src:
                out[col] = df[src].astype(str).fillna("")
            else:
                out[col] = ""
        return out[canonical_cols]

    alat = to_canonical(alat)
    pakaian = to_canonical(pakaian)
    tari = to_canonical(tari)

    # Gabungkan
    df = pd.concat([alat, pakaian, tari], ignore_index=True)

    # Re-enumerate 'no' sequentially to follow row order
    if 'no' in df.columns:
        df = df.drop(columns=['no'])
    df.insert(0, 'no', range(1, len(df) + 1))

    # Simpan ke CSV dan JSON
    df = df.where(pd.notnull(df), None)
    combined_csv = CLEAN_DIR / "combined_dataset.csv"
    combined_json = CLEAN_DIR / "combined_dataset.json"

    df.to_csv(combined_csv, index=False)
    with open(combined_json, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset gabungan disimpan ke:\n - {combined_csv}\n - {combined_json}")
    return df

if __name__ == "__main__":
    load_and_combine()