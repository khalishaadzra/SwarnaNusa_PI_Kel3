"""
Web Scraper Tarian Tradisional Indonesia v2
Menggunakan Wikipedia API sepenuhnya - lebih stabil dan reliable
Target: 100+ tarian dengan data lengkap
"""

import requests
import pandas as pd
import time
import re
import json
import warnings
warnings.filterwarnings('ignore')

# Session
session = requests.Session()
session.headers.update({
    'User-Agent': 'TarianIndonesiaScraper/1.0 (Educational Purpose)'
})

WIKI_API = "https://id.wikipedia.org/w/api.php"

def search_dances():
    """Cari semua artikel tarian dari Wikipedia"""
    all_titles = set()
    
    # Pencarian dengan berbagai kata kunci
    search_terms = [
        "Tari tradisional", "Tari daerah", "Tarian Indonesia",
        "Tari Jawa", "Tari Bali", "Tari Sunda", "Tari Sumatera",
        "Tari Kalimantan", "Tari Sulawesi", "Tari Papua",
        "Tari Aceh", "Tari Minang", "Tari Betawi"
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
                if 'Tari' in title or 'tari' in title:
                    all_titles.add(title)
        except:
            continue
        time.sleep(0.2)
    
    # Dari kategori
    categories = [
        "Tari_Indonesia", "Tari_tradisional_Indonesia",
        "Tari_Jawa", "Tari_Bali", "Tari_Sunda"
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
                if title:
                    all_titles.add(title)
        except:
            continue
        time.sleep(0.2)
    
    return list(all_titles)

# Daftar manual untuk memastikan tarian populer tercakup
MANUAL_LIST = [
    "Tari Saman", "Tari Seudati", "Tari Ranup Lampuan", "Tari Bines", "Tari Guel",
    "Tor-Tor", "Tari Sigale-gale", "Tari Piso Surit", "Tari Serampang Dua Belas",
    "Tari Piring", "Tari Payung", "Tari Pasambahan", "Randai", "Tari Indang",
    "Tari Zapin", "Tari Joget Lambak", "Tari Mak Inang",
    "Tari Sekapur Sirih", "Tari Tanggai", "Tari Gending Sriwijaya",
    "Tari Andun", "Tari Bedana", "Tari Melinting", "Tari Sigeh Pengunten",
    "Tari Yapong", "Tari Topeng Betawi", "Ondel-ondel", "Tari Cokek",
    "Jaipongan", "Tari Topeng Cirebon", "Tari Merak", "Tari Ketuk Tilu",
    "Tari Sintren", "Tari Ronggeng", "Tari Topeng Priangan",
    "Tari Serimpi", "Tari Gambyong", "Bedhaya", "Tari Bondan",
    "Tari Tayub", "Tari Dolalak", "Tari Lengger", "Tari Kuda Lumping",
    "Tari Angguk", "Jaran Kepang", "Tari Golek Menak", "Golek Ayun-Ayun",
    "Beksan Trunajaya", "Topeng Ireng",
    "Reog Ponorogo", "Tari Gandrung", "Tari Remo", "Ludruk", "Jaranan",
    "Tari Pendet", "Tari Kecak", "Tari Legong", "Tari Barong", "Tari Sanghyang",
    "Tari Baris", "Tari Janger", "Tari Rejang", "Joged Bumbung", "Gambuh",
    "Gendang Beleq", "Caci (tarian)", "Tari Ja'i", "Tari Likurai", "Tari Lego-lego",
    "Tari Hudoq", "Tari Kancet Ledo", "Tari Gong", "Tari Mandau",
    "Tari Baksa Kembang", "Tari Jepen", "Tari Enggang", "Tari Monong",
    "Tari Maengket", "Tari Kabasaran", "Poco-poco", "Tari Pakarena",
    "Tari Kipas Pakarena", "Tari Bosara", "Tari Dero", "Tari Lulo",
    "Tari Cakalele", "Tari Pajoge",
    "Tari Lenso", "Tari Saureka-reka", "Tari Yospan", "Tari Sajojo", "Tari Perang",
]

def get_page_data(title):
    """Ambil data lengkap dari satu halaman"""
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'extracts|pageimages|info|categories',
        'exintro': True,
        'explaintext': True,
        'piprop': 'original|thumbnail',
        'pithumbsize': 600,
        'inprop': 'url',
        'cllimit': 10,
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
            if not extract or len(extract) < 100:
                return None
            
            # Ambil gambar
            img_url = ''
            if 'original' in page:
                img_url = page['original'].get('source', '')
            elif 'thumbnail' in page:
                img_url = page['thumbnail'].get('source', '')
                # Perbesar thumbnail
                img_url = re.sub(r'/\d+px-', '/600px-', img_url)
            
            return {
                'title': page.get('title', title),
                'extract': extract,
                'url': page.get('fullurl', ''),
                'image': img_url
            }
    except Exception as e:
        return None
    
    return None

def detect_region(text, title):
    """Deteksi asal daerah"""
    mapping = {
        'Aceh': ['aceh', 'gayo', 'alas'],
        'Sumatera Utara': ['batak', 'karo', 'toba', 'mandailing', 'nias', 'sumatera utara', 'tapanuli'],
        'Sumatera Barat': ['minangkabau', 'minang', 'sumatera barat', 'padang'],
        'Riau': ['riau', 'melayu riau'],
        'Kepulauan Riau': ['kepulauan riau', 'kepri'],
        'Jambi': ['jambi'],
        'Sumatera Selatan': ['palembang', 'sumatera selatan', 'sriwijaya'],
        'Bengkulu': ['bengkulu', 'rejang'],
        'Lampung': ['lampung'],
        'Bangka Belitung': ['bangka', 'belitung'],
        'DKI Jakarta': ['jakarta', 'betawi'],
        'Jawa Barat': ['sunda', 'jawa barat', 'cirebon', 'bandung', 'priangan'],
        'Banten': ['banten'],
        'Jawa Tengah': ['jawa tengah', 'surakarta', 'solo', 'semarang', 'banyumas', 'wonosobo', 'purworejo'],
        'DI Yogyakarta': ['yogyakarta', 'jogja', 'jogjakarta', 'keraton yogya'],
        'Jawa Timur': ['jawa timur', 'surabaya', 'ponorogo', 'banyuwangi', 'madura', 'malang', 'kediri'],
        'Bali': ['bali', 'balinese'],
        'Nusa Tenggara Barat': ['ntb', 'lombok', 'sumbawa', 'bima', 'sasak'],
        'Nusa Tenggara Timur': ['ntt', 'flores', 'sumba', 'timor', 'manggarai', 'ende', 'sikka'],
        'Kalimantan Barat': ['kalimantan barat', 'kalbar', 'pontianak'],
        'Kalimantan Tengah': ['kalimantan tengah', 'kalteng', 'palangkaraya', 'dayak ngaju'],
        'Kalimantan Selatan': ['kalimantan selatan', 'kalsel', 'banjar', 'banjarmasin'],
        'Kalimantan Timur': ['kalimantan timur', 'kaltim', 'kutai', 'samarinda', 'dayak'],
        'Kalimantan Utara': ['kalimantan utara', 'kaltara'],
        'Sulawesi Utara': ['sulawesi utara', 'minahasa', 'manado'],
        'Gorontalo': ['gorontalo'],
        'Sulawesi Tengah': ['sulawesi tengah', 'sulteng', 'palu'],
        'Sulawesi Barat': ['sulawesi barat', 'sulbar', 'mamuju'],
        'Sulawesi Selatan': ['sulawesi selatan', 'sulsel', 'makassar', 'bugis', 'toraja', 'gowa'],
        'Sulawesi Tenggara': ['sulawesi tenggara', 'sultra', 'kendari', 'buton'],
        'Maluku': ['maluku', 'ambon'],
        'Maluku Utara': ['maluku utara', 'ternate', 'tidore'],
        'Papua Barat': ['papua barat'],
        'Papua': ['papua', 'irian', 'jayapura', 'asmat', 'dani', 'sentani'],
    }
    
    combined = f"{title} {text}".lower()
    
    for region, keywords in mapping.items():
        for kw in keywords:
            if kw in combined:
                return region
    
    return "Indonesia"

def main():
    print("=" * 70)
    print("   SCRAPER TARIAN TRADISIONAL INDONESIA v2")
    print("   Menggunakan Wikipedia API - Lebih Stabil")
    print("=" * 70)
    
    # Kumpulkan judul
    print("\n[1/4] Mencari artikel tarian di Wikipedia...")
    searched = search_dances()
    
    # Gabung dengan daftar manual
    all_titles = list(set(MANUAL_LIST + searched))
    print(f"      Ditemukan: {len(all_titles)} artikel potensial")
    
    # Scrape data
    print("\n[2/4] Mengambil data dari setiap artikel...")
    results = []
    
    for i, title in enumerate(all_titles, 1):
        data = get_page_data(title)
        
        if data:
            # Bersihkan dan format
            desc = re.sub(r'\s+', ' ', data['extract']).strip()
            
            results.append({
                'judul': data['title'],
                'deskripsi': desc[:2000],
                'asal_daerah': detect_region(desc, data['title']),
                'link': data['url'],
                'gambar': data['image']
            })
            status = "✓"
        else:
            status = "✗"
        
        # Progress
        if i % 25 == 0 or i == len(all_titles):
            print(f"      [{i}/{len(all_titles)}] Berhasil: {len(results)}")
        
        time.sleep(0.25)
    
    print(f"\n[3/4] Hasil scraping:")
    print(f"      ✓ Berhasil: {len(results)}")
    print(f"      ✗ Gagal   : {len(all_titles) - len(results)}")
    
    # Simpan CSV
    print("\n[4/4] Menyimpan ke CSV...")
    
    if len(results) > 0:
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['judul'])
        df = df.sort_values('judul').reset_index(drop=True)
        df.insert(0, 'no', range(1, len(df) + 1))
        
        filename = 'tarian_tradisional_indonesia.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        # Statistik
        with_img = len(df[df['gambar'] != ''])
        
        print("\n" + "=" * 70)
        print("   ✅ SCRAPING SELESAI!")
        print("=" * 70)
        print(f"   📁 File      : {filename}")
        print(f"   📊 Total     : {len(df)} tarian")
        print(f"   🖼️  Gambar   : {with_img} ({with_img*100//len(df)}%)")
        print("=" * 70)
        
        # Per daerah
        print("\n   📍 Distribusi per Daerah (Top 15):")
        print("   " + "-" * 50)
        for region, cnt in df['asal_daerah'].value_counts().head(15).items():
            bar = "█" * (cnt // 2) + "░" * (10 - cnt // 2)
            print(f"   {region:28} {bar} {cnt:3}")
        
        # Sample
        print("\n   📋 Sample Data:")
        print("   " + "-" * 50)
        for _, r in df.sample(min(5, len(df))).iterrows():
            print(f"   • {r['judul']} ({r['asal_daerah']})")
            print(f"     {r['deskripsi'][:70]}...")
            print(f"     Gambar: {'✓' if r['gambar'] else '✗'}")
        
        return df
    else:
        print("\n   ❌ Gagal! Tidak ada data yang berhasil di-scrape.")
        print("      Pastikan koneksi internet stabil.")
        return None

if __name__ == "__main__":
    df = main()