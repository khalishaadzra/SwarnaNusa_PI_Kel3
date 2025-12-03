import pandas as pd
import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data_raw"
CLEAN_DIR = BASE_DIR / "data_clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

def load_and_combine():
    print("🔄 Menggabungkan dataset...")

    # Load CSV
    alat = pd.read_csv(RAW_DIR / "alat_musik_tradisional_indonesia.csv")
    pakaian = pd.read_csv(RAW_DIR / "pakaian_tradisional_indonesia.csv")
    tari = pd.read_csv(RAW_DIR / "tarian_tradisional_indonesia.csv")

    # Tambah kategori
    alat["kategori"] = "alat_musik"
    pakaian["kategori"] = "pakaian"
    tari["kategori"] = "tarian"

    # Kolom wajib (disamakan)
    kolom_target = [
        "no",
        "judul",
        "deskripsi",
        "asal_daerah",
        "cara_main",
        "link",
        "gambar",
        "kategori"
    ]

    # Tambahkan kolom yang hilang
    for df_ in [pakaian, tari]:
        if "cara_main" not in df_.columns:
            df_["cara_main"] = ""

    # Pastikan semua kolom ada dan urutannya sama
    alat = alat[kolom_target]
    pakaian = pakaian[kolom_target]
    tari = tari[kolom_target]

    # Gabungkan
    df = pd.concat([alat, pakaian, tari], ignore_index=True)

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