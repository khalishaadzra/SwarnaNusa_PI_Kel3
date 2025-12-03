"""
Web Scraper Alat Musik Tradisional Indonesia
Sumber: Wikipedia Indonesia (via API)
Output: CSV dengan kolom no, judul, deskripsi, asal_daerah, cara_main, link, gambar
"""

import requests
import pandas as pd
import time
import re
import warnings
warnings.filterwarnings('ignore')

# Session
session = requests.Session()
session.headers.update({
    'User-Agent': 'AlatMusikIndonesiaScraper/1.0 (Educational Purpose)'
})

WIKI_API = "https://id.wikipedia.org/w/api.php"

# Daftar 150+ alat musik tradisional Indonesia
DAFTAR_ALAT_MUSIK = [
    # Alat Musik Pukul / Perkusi
    "Gamelan", "Gong", "Bonang", "Saron", "Gender_(alat_musik)", "Slenthem",
    "Gambang", "Kendang", "Ketipung", "Bedug", "Gendang", "Rebana",
    "Tifa", "Kolintang", "Talempong", "Aramba", "Gordang_Sambilan",
    "Taganing", "Garantung", "Kulcapi", "Gendang_Beleq", "Gendang_Karo",
    "Tambua", "Tambo", "Rapai", "Geundrang", "Celempong", "Canang",
    "Ketuk", "Kenong", "Kempul", "Engkromong", "Jidor", "Terbang",
    "Kompang", "Marwas", "Dol_(alat_musik)", "Rindik", "Ceng-ceng",
    "Kecrek", "Angklung", "Calung", "Karawitan",
    
    # Alat Musik Petik
    "Kecapi", "Sasando", "Sampek", "Siter", "Celempung", "Gambus",
    "Hasapi", "Kucapi", "Jungga", "Popondi", "Talindo", "Jentreng",
    "Tarawangsa", "Panting", "Dambus",
    
    # Alat Musik Gesek
    "Rebab", "Tehyan", "Arbab", "Ohyan",
    
    # Alat Musik Tiup
    "Suling", "Saluang", "Serunai", "Serune_Kalee", "Bansi", "Pupuik",
    "Salung", "Nafiri", "Tarompet", "Selompret", "Pere", "Foy_Doa",
    "Triton_(alat_musik)", "Pupuik_Batang_Padi", "Ole-ole", "Sulim",
    "Seruling_Lembang", "Tulali", "Fu", "Puwi-puwi", "Tongali",
    
    # Per Daerah - Aceh
    "Serune_Kale", "Bangsi_Alas", "Taktok_Trieng", "Berenguh",
    
    # Sumatera Utara
    "Sarune_Bolon", "Sarune_Bulu", "Oloan", "Panggora", "Doal",
    "Hesek", "Odap", "Ogung", "Saga-saga", "Sordam",
    
    # Sumatera Barat
    "Rabab", "Gandang_Tabuik", "Aguang", "Adok", "Talempong_Pacik",
    
    # Riau & Kepri
    "Gambus_Melayu", "Kompang_Melayu", "Gendang_Panjang", "Akordeon",
    
    # Jambi
    "Kelintang", "Serangko",
    
    # Sumatera Selatan
    "Gendang_Sriwijaya", "Akordeon_Melayu",
    
    # Bengkulu
    "Dol_Bengkulu", "Kulintang_Bengkulu",
    
    # Lampung
    "Gamolan", "Kulintang_Lampung", "Cetik", "Talo_Balak",
    
    # DKI Jakarta (Betawi)
    "Tanjidor", "Tehyan", "Kecrek", "Ningnong", "Gambang_Kromong",
    
    # Jawa Barat (Sunda)
    "Angklung", "Calung", "Kacapi_Suling", "Karinding", "Suling_Sunda",
    "Degung", "Jengglong", "Goong", "Arumba", "Tarawangsa",
    
    # Banten
    "Rampak_Bedug", "Angklung_Buhun",
    
    # Jawa Tengah & Yogyakarta
    "Gamelan_Jawa", "Saron", "Demung", "Peking_(alat_musik)", "Bonang_Barung",
    "Bonang_Panerus", "Kethuk", "Kenong", "Kempyang", "Gong_Ageng",
    "Suwukan", "Kemanak", "Rebab_Jawa", "Siter", "Clempung",
    "Gender_Barung", "Gender_Panerus", "Gambang_Kayu", "Slenthem",
    
    # Jawa Timur
    "Gamelan_Jawa_Timuran", "Kendhang_Ciblon", "Angklung_Reog",
    
    # Bali
    "Gamelan_Bali", "Rindik", "Ceng-ceng", "Suling_Bali", "Genggong",
    "Pereret", "Gong_Kebyar", "Gender_Wayang", "Trompong", "Gangsa",
    "Jublag", "Jegogan", "Kantilan", "Pemade", "Kempli", "Kajar",
    
    # NTB
    "Gendang_Beleq", "Serunai_Sasak", "Preret",
    
    # NTT
    "Sasando", "Foy_Doa", "Tambur", "Gong_NTT", "Lamba",
    
    # Kalimantan
    "Sampek", "Sape", "Jatung_Utang", "Tuma", "Garantung_Dayak",
    "Keledi", "Kedire", "Rebab_Dayak", "Suling_Dayak", "Kangkanung",
    "Katambung", "Panting", "Babun", "Agung", "Tawak-tawak",
    "Hadrah", "Kuriding", "Gandang_Dayak",
    
    # Sulawesi
    "Kolintang", "Arumba", "Suling_Minahasa", "Gong_Sulawesi", "Salude",
    "Popondi", "Kecapi_Bugis", "Talindo", "Suling_Lembang", "Pui-pui",
    "Gambus_Makassar", "Alosu", "Gendang_Bugis",
    
    # Maluku
    "Tifa_Maluku", "Tahuri", "Suling_Bambu", "Totobuang", "Gong_Maluku",
    "Ukulele_Maluku", "Sulepe", "Nafiri_Maluku",
    
    # Papua
    "Tifa_Papua", "Pikon", "Atowo", "Guoto", "Suling_Papua", "Fu_Papua",
    "Triton", "Tambur_Papua",
]

def search_alat_musik():
    """Cari alat musik tambahan dari Wikipedia"""
    found = set()
    
    search_terms = [
        "alat musik tradisional Indonesia",
        "alat musik daerah",
        "alat musik Jawa",
        "alat musik Bali",
        "alat musik Sumatera",
        "alat musik Kalimantan",
        "alat musik Sulawesi",
        "alat musik Papua",
        "gamelan Indonesia",
        "alat musik tiup tradisional",
        "alat musik pukul tradisional",
        "alat musik petik tradisional"
    ]
    
    for term in search_terms:
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': term,
            'srlimit': 50,
            'format': 'json'
        }
        try:
            r = session.get(WIKI_API, params=params, timeout=15)
            data = r.json()
            for item in data.get('query', {}).get('search', []):
                title = item.get('title', '')
                # Filter hanya yang relevan
                keywords = ['musik', 'gamelan', 'gong', 'suling', 'kendang', 
                           'gendang', 'rebab', 'kecapi', 'angklung', 'tifa']
                if any(kw in title.lower() for kw in keywords):
                    found.add(title)
        except:
            continue
        time.sleep(0.2)
    
    # Dari kategori
    categories = [
        "Alat_musik_Indonesia",
        "Alat_musik_tradisional_Indonesia",
        "Gamelan",
        "Alat_musik_Jawa",
        "Alat_musik_Bali"
    ]
    
    for cat in categories:
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Kategori:{cat}',
            'cmlimit': 100,
            'cmtype': 'page',
            'format': 'json'
        }
        try:
            r = session.get(WIKI_API, params=params, timeout=15)
            data = r.json()
            for m in data.get('query', {}).get('categorymembers', []):
                title = m.get('title', '')
                if title and ':' not in title:
                    found.add(title)
        except:
            continue
        time.sleep(0.2)
    
    return list(found)

def get_page_data(title):
    """Ambil data dari Wikipedia API"""
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'extracts|pageimages|info',
        'exintro': True,
        'explaintext': True,
        'piprop': 'original|thumbnail',
        'pithumbsize': 600,
        'inprop': 'url',
        'format': 'json',
        'redirects': 1
    }
    
    try:
        r = session.get(WIKI_API, params=params, timeout=15)
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        
        for page_id, page in pages.items():
            if page_id == '-1':
                return None
            
            extract = page.get('extract', '')
            if not extract or len(extract) < 80:
                return None
            
            # Gambar
            img = ''
            if 'original' in page:
                img = page['original'].get('source', '')
            elif 'thumbnail' in page:
                img = page['thumbnail'].get('source', '')
                img = re.sub(r'/\d+px-', '/600px-', img)
            
            return {
                'title': page.get('title', title),
                'extract': extract,
                'url': page.get('fullurl', ''),
                'image': img
            }
    except:
        pass
    return None

def detect_region(text, title):
    """Deteksi asal daerah"""
    mapping = {
        'Aceh': ['aceh', 'gayo', 'alas', 'pidie'],
        'Sumatera Utara': ['batak', 'karo', 'toba', 'mandailing', 'nias', 'sumatera utara', 'tapanuli', 'simalungun'],
        'Sumatera Barat': ['minangkabau', 'minang', 'sumatera barat', 'padang'],
        'Riau': ['riau', 'melayu riau', 'pekanbaru'],
        'Jambi': ['jambi'],
        'Sumatera Selatan': ['palembang', 'sumatera selatan', 'sriwijaya'],
        'Bengkulu': ['bengkulu'],
        'Lampung': ['lampung'],
        'DKI Jakarta': ['jakarta', 'betawi'],
        'Jawa Barat': ['sunda', 'jawa barat', 'bandung', 'priangan', 'cirebon'],
        'Banten': ['banten'],
        'Jawa Tengah': ['jawa tengah', 'surakarta', 'solo', 'semarang', 'banyumas'],
        'DI Yogyakarta': ['yogyakarta', 'jogja', 'keraton'],
        'Jawa Timur': ['jawa timur', 'surabaya', 'ponorogo', 'banyuwangi', 'madura'],
        'Jawa': ['jawa', 'gamelan jawa'],
        'Bali': ['bali', 'balinese'],
        'Nusa Tenggara Barat': ['ntb', 'lombok', 'sumbawa', 'sasak'],
        'Nusa Tenggara Timur': ['ntt', 'flores', 'rote', 'sumba', 'timor', 'kupang'],
        'Kalimantan Barat': ['kalimantan barat', 'pontianak'],
        'Kalimantan Tengah': ['kalimantan tengah', 'dayak ngaju'],
        'Kalimantan Selatan': ['kalimantan selatan', 'banjar'],
        'Kalimantan Timur': ['kalimantan timur', 'kutai', 'dayak'],
        'Sulawesi Utara': ['sulawesi utara', 'minahasa', 'manado'],
        'Sulawesi Selatan': ['sulawesi selatan', 'makassar', 'bugis', 'toraja'],
        'Sulawesi Tengah': ['sulawesi tengah', 'palu'],
        'Maluku': ['maluku', 'ambon'],
        'Papua': ['papua', 'irian', 'jayapura', 'asmat'],
    }
    
    combined = f"{title} {text}".lower()
    for region, keywords in mapping.items():
        for kw in keywords:
            if kw in combined:
                return region
    return "Indonesia"

def detect_cara_main(text):
    """Deteksi cara memainkan alat musik"""
    text_lower = text.lower()
    
    if any(x in text_lower for x in ['dipukul', 'ditabuh', 'pukul', 'tabuh', 'memukul']):
        return "Dipukul"
    elif any(x in text_lower for x in ['dipetik', 'petik', 'memetik', 'dawai']):
        return "Dipetik"
    elif any(x in text_lower for x in ['ditiup', 'tiup', 'meniup', 'hembusan']):
        return "Ditiup"
    elif any(x in text_lower for x in ['digesek', 'gesek', 'menggesek']):
        return "Digesek"
    elif any(x in text_lower for x in ['digoyangkan', 'goyang', 'dikocok', 'digetarkan']):
        return "Digoyangkan"
    else:
        return "Lainnya"

def main():
    print("=" * 70)
    print("   SCRAPER ALAT MUSIK TRADISIONAL INDONESIA")
    print("   Sumber: Wikipedia Indonesia (via API)")
    print("=" * 70)
    
    # Kumpulkan daftar
    print("\n[1/4] Mencari artikel alat musik di Wikipedia...")
    searched = search_alat_musik()
    
    # Gabung dengan daftar manual (bersihkan underscore untuk API)
    manual_clean = [x.replace('_', ' ') for x in DAFTAR_ALAT_MUSIK]
    all_items = list(set(manual_clean + searched))
    print(f"      Ditemukan: {len(all_items)} artikel potensial")
    
    # Scrape
    print("\n[2/4] Mengambil data dari setiap artikel...")
    results = []
    
    for i, title in enumerate(all_items, 1):
        data = get_page_data(title)
        
        if data:
            desc = re.sub(r'\s+', ' ', data['extract']).strip()
            
            results.append({
                'judul': data['title'],
                'deskripsi': desc[:2000],
                'asal_daerah': detect_region(desc, data['title']),
                'cara_main': detect_cara_main(desc),
                'link': data['url'],
                'gambar': data['image']
            })
        
        if i % 25 == 0 or i == len(all_items):
            print(f"      [{i}/{len(all_items)}] Berhasil: {len(results)}")
        
        time.sleep(0.25)
    
    print(f"\n[3/4] Hasil scraping:")
    print(f"      ✓ Berhasil: {len(results)}")
    print(f"      ✗ Gagal   : {len(all_items) - len(results)}")
    
    # Simpan CSV
    print("\n[4/4] Menyimpan ke CSV...")
    
    if len(results) > 0:
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['judul'])
        df = df.sort_values('judul').reset_index(drop=True)
        df.insert(0, 'no', range(1, len(df) + 1))
        
        filename = 'alat_musik_tradisional_indonesia.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        with_img = len(df[df['gambar'] != ''])
        
        print("\n" + "=" * 70)
        print("   ✅ SCRAPING SELESAI!")
        print("=" * 70)
        print(f"   📁 File         : {filename}")
        print(f"   📊 Total        : {len(df)} alat musik")
        print(f"   🖼️  Dengan Gambar: {with_img} ({with_img*100//len(df)}%)")
        print("=" * 70)
        
        # Per daerah
        print("\n   📍 Distribusi per Daerah (Top 10):")
        print("   " + "-" * 50)
        for region, cnt in df['asal_daerah'].value_counts().head(10).items():
            bar = "█" * min(cnt, 20)
            print(f"   {region:25} {bar} {cnt}")
        
        # Per cara main
        print("\n   🎵 Berdasarkan Cara Memainkan:")
        print("   " + "-" * 50)
        for cara, cnt in df['cara_main'].value_counts().items():
            print(f"   {cara:20} : {cnt}")
        
        # Sample
        print("\n   📋 Sample Data:")
        print("   " + "-" * 50)
        for _, r in df.sample(min(5, len(df))).iterrows():
            print(f"   • {r['judul']} ({r['asal_daerah']}) - {r['cara_main']}")
            print(f"     {r['deskripsi'][:70]}...")
            print(f"     Gambar: {'✓' if r['gambar'] else '✗'}")
        
        return df
    else:
        print("\n   ❌ Gagal! Tidak ada data yang berhasil di-scrape.")
        return None

if __name__ == "__main__":
    df = main()