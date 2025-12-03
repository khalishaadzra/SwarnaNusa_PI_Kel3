import pandas as pd
import json

csv_file = "combined_dataset1.csv"
json_file = "combined_dataset.json"

# Baca CSV apa adanya
df = pd.read_csv(csv_file, dtype=str)

# Ganti NaN menjadi string kosong
df = df.fillna("")

# Konversi ke list of dicts
records = df.to_dict(orient="records")

# Simpan JSON TANPA escape slash
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("Done! JSON berhasil dibuat.")
