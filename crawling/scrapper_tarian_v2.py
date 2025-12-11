"""
Web Scraper Tarian Tradisional Indonesia v3
- Crawling fokus HANYA tarian tradisional
- Scraping mengambil SELURUH konten Wikipedia (bukan hanya intro)
- Satu dokumen = satu baris CSV
"""

import requests
import pandas as pd
import time
import re
import warnings
from typing import Dict, List, Optional, Set
warnings.filterwarnings('ignore')

# Konfigurasi
WIKI_API = "https://id.wikipedia.org/w/api.php"
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_REQUESTS = 0.4

class TarianScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TarianIndonesiaScraper/3.0 (Educational Purpose)'
        })
    
    def search_dances(self) -> List[str]:
        """Cari HANYA artikel tarian tradisional dari Wikipedia"""
        all_titles: Set[str] = set()
        
        # FOKUS: Kata kunci spesifik untuk tarian tradisional
        search_terms = [
            "Tari tradisional Indonesia",
            "Tari daerah Indonesia", 
            "Tarian nusantara",
            "Tari adat"
        ]
        
        print("   🔍 Mencari artikel tarian tradisional...")
        for term in search_terms:
            titles = self._search_by_term(term, max_results=100)
            all_titles.update(titles)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"   ✓ Dari pencarian: {len(all_titles)} artikel")
        
        # FOKUS: Kategori khusus tarian tradisional
        print("   📂 Mencari dari kategori tarian...")
        categories = [
            "Tari_tradisional_Indonesia",
            "Tari_Indonesia",
            "Tari_Jawa",
            "Tari_Bali", 
            "Tari_Sunda",
            "Tari_Sumatra",
            "Tari_Kalimantan",
            "Tari_Sulawesi",
            "Tari_Nusa_Tenggara",
            "Tari_Maluku",
            "Tari_Papua"
        ]
        
        for cat in categories:
            titles = self._get_category_members(cat)
            filtered_titles = {t for t in titles if self._is_traditional_dance(t)}
            all_titles.update(filtered_titles)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"   ✓ Dari kategori: {len(all_titles)} artikel total")
        
        return list(all_titles)
    
    def _search_by_term(self, term: str, max_results: int = 50) -> Set[str]:
        """Cari artikel berdasarkan kata kunci"""
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': term,
            'srlimit': max_results,
            'format': 'json'
        }
        
        try:
            response = self.session.get(WIKI_API, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            titles = set()
            for item in data.get('query', {}).get('search', []):
                title = item.get('title', '')
                # Filter KETAT: hanya yang benar-benar tarian tradisional
                if self._is_traditional_dance(title):
                    titles.add(title)
            
            return titles
        except Exception as e:
            print(f"   ⚠️  Error pencarian '{term}': {str(e)}")
            return set()
    
    def _get_category_members(self, category: str) -> Set[str]:
        """Ambil semua artikel dari kategori"""
        all_members = set()
        cmcontinue = None
        
        while True:
            params = {
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': f'Kategori:{category}',
                'cmlimit': 500,
                'cmtype': 'page',
                'format': 'json'
            }
            
            if cmcontinue:
                params['cmcontinue'] = cmcontinue
            
            try:
                response = self.session.get(WIKI_API, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                for member in data.get('query', {}).get('categorymembers', []):
                    title = member.get('title', '')
                    if title:
                        all_members.add(title)
                
                # Check untuk continuation
                cmcontinue = data.get('continue', {}).get('cmcontinue')
                if not cmcontinue:
                    break
                    
            except Exception as e:
                print(f"   ⚠️  Error kategori '{category}': {str(e)}")
                break
        
        return all_members
    
    def _is_traditional_dance(self, title: str) -> bool:
        """
        Filter KETAT: Cek apakah artikel benar-benar tentang tarian tradisional
        Exclude: penari, sanggar, festival, dll
        """
        title_lower = title.lower()
        
        # Kata kunci POSITIF (harus ada salah satu)
        dance_keywords = [
            'tari ', 'tarian', 'reog', 'randai', 'joged', 'bedhaya',
            'jaipongan', 'poco-poco', 'tor-tor', 'ondel', 'jaran kepang',
            'kuda lumping', 'cakalele', 'saman', 'pendet', 'kecak',
            'legong', 'barong', 'remo', 'gandrung', 'gambyong', 'serimpi',
            'jaranan', 'ludruk', 'gambuh', 'rejang', 'baris', 'sanghyang'
        ]
        
        has_dance_keyword = any(kw in title_lower for kw in dance_keywords)
        
        if not has_dance_keyword:
            return False
        
        # Kata kunci NEGATIF (exclude jika ada)
        exclude_keywords = [
            'penari', 'koreografer', 'sanggar', 'festival', 'kompetisi',
            'grup', 'komunitas', 'organisasi', 'kategori:', 'daftar',
            'seniman', 'pelaku', 'maestro', 'tokoh', 'pencipta',
            'sekolah', 'akademi', 'institut', 'universitas', 'studio'
        ]
        
        has_exclude = any(kw in title_lower for kw in exclude_keywords)
        
        return has_dance_keyword and not has_exclude
    
    def get_full_page_content(self, title: str) -> Optional[Dict]:
        """
        Ambil SELURUH konten Wikipedia (bukan hanya intro)
        Termasuk: sejarah, karakteristik, gerakan, musik, kostum, dll
        """
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|pageimages|info|categories|revisions',
            'explaintext': True,  # Ambil semua teks, bukan hanya intro
            'exsectionformat': 'plain',  # Format section
            'piprop': 'original|thumbnail',
            'pithumbsize': 800,
            'inprop': 'url',
            'cllimit': 20,
            'rvprop': 'content',  # Ambil full content
            'format': 'json',
            'redirects': 1
        }
        
        try:
            response = self.session.get(WIKI_API, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page in pages.items():
                if page_id == '-1':
                    return None
                
                # Ambil FULL extract (bukan intro saja)
                full_text = page.get('extract', '')
                
                # Validasi: harus punya konten substansial
                if not full_text or len(full_text) < 200:
                    return None
                
                # Ambil URL gambar resolusi tinggi
                img_url = self._get_image_url(page)
                
                # Ambil kategori
                categories = []
                for cat in page.get('categories', []):
                    cat_title = cat.get('title', '').replace('Kategori:', '')
                    categories.append(cat_title)
                
                return {
                    'title': page.get('title', title),
                    'full_content': full_text,  # FULL CONTENT
                    'url': page.get('fullurl', ''),
                    'image': img_url,
                    'categories': ', '.join(categories),
                    'length': len(full_text)
                }
        
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout: {title}")
            return None
        except Exception as e:
            print(f"   ⚠️  Error: {title} - {str(e)}")
            return None
        
        return None
    
    def _get_image_url(self, page: Dict) -> str:
        """Ekstrak URL gambar resolusi tertinggi"""
        img_url = ''
        
        if 'original' in page:
            img_url = page['original'].get('source', '')
        elif 'thumbnail' in page:
            img_url = page['thumbnail'].get('source', '')
            # Tingkatkan resolusi ke 800px
            img_url = re.sub(r'/\d+px-', '/800px-', img_url)
        
        return img_url
    
    def detect_region(self, text: str, title: str) -> str:
        """Deteksi asal daerah dengan keyword yang lebih lengkap"""
        mapping = {
            'Aceh': ['aceh', 'gayo', 'alas', 'seudati', 'saman', 'ranup lampuan', 'likok pulo'],
            'Sumatera Utara': ['batak', 'karo', 'toba', 'mandailing', 'nias', 
                               'sumatera utara', 'tapanuli', 'tor-tor', 'sigale', 'serampang'],
            'Sumatera Barat': ['minangkabau', 'minang', 'sumatera barat', 
                               'padang', 'piring', 'payung', 'pasambahan', 'randai', 'indang'],
            'Riau': ['riau', 'melayu riau', 'zapin', 'joget', 'mak inang'],
            'Kepulauan Riau': ['kepulauan riau', 'kepri'],
            'Jambi': ['jambi', 'sekapur sirih', 'batanghari'],
            'Sumatera Selatan': ['palembang', 'sumatera selatan', 'sriwijaya', 
                                 'gending sriwijaya', 'tanggai', 'tenun songket'],
            'Bengkulu': ['bengkulu', 'rejang', 'andun'],
            'Lampung': ['lampung', 'bedana', 'melinting', 'sigeh', 'pengunten'],
            'Bangka Belitung': ['bangka', 'belitung'],
            'DKI Jakarta': ['jakarta', 'betawi', 'yapong', 'topeng betawi', 
                            'ondel', 'cokek'],
            'Jawa Barat': ['sunda', 'jawa barat', 'cirebon', 'bandung', 
                           'priangan', 'jaipongan', 'merak', 'ketuk tilu', 
                           'sintren', 'ronggeng', 'topeng cirebon'],
            'Banten': ['banten', 'rampak bedug', 'saman gaya banten'],
            'Jawa Tengah': ['jawa tengah', 'surakarta', 'solo', 'semarang', 
                            'banyumas', 'wonosobo', 'purworejo', 'dolalak', 
                            'lengger', 'angguk', 'topeng ireng'],
            'DI Yogyakarta': ['yogyakarta', 'jogja', 'jogjakarta', 'keraton yogya',
                              'serimpi', 'gambyong', 'bedhaya', 'bondan', 'golek'],
            'Jawa Timur': ['jawa timur', 'surabaya', 'ponorogo', 'banyuwangi', 
                           'madura', 'malang', 'kediri', 'reog', 'gandrung', 
                           'remo', 'ludruk', 'jaranan', 'jaran kepang'],
            'Bali': ['bali', 'balinese', 'pendet', 'kecak', 'legong', 'barong', 
                     'sanghyang', 'baris', 'janger', 'rejang', 'gambuh', 'joged bumbung'],
            'Nusa Tenggara Barat': ['ntb', 'lombok', 'sumbawa', 'bima', 'sasak', 
                                    'gendang beleq', 'gandrung lombok'],
            'Nusa Tenggara Timur': ['ntt', 'flores', 'sumba', 'timor', 'manggarai', 
                                    'ende', 'sikka', 'caci', 'likurai', 'lego-lego'],
            'Kalimantan Barat': ['kalimantan barat', 'kalbar', 'pontianak', 
                                 'monong', 'zapin melayu', 'rodat'],
            'Kalimantan Tengah': ['kalimantan tengah', 'kalteng', 'palangkaraya', 
                                  'dayak ngaju', 'tambun', 'balean dadas'],
            'Kalimantan Selatan': ['kalimantan selatan', 'kalsel', 'banjar', 
                                   'banjarmasin', 'baksa kembang', 'radap rahayu'],
            'Kalimantan Timur': ['kalimantan timur', 'kaltim', 'kutai', 
                                 'samarinda', 'dayak', 'hudoq', 'kancet', 
                                 'gong', 'enggang', 'belian'],
            'Kalimantan Utara': ['kalimantan utara', 'kaltara', 'jepen', 'tidung'],
            'Sulawesi Utara': ['sulawesi utara', 'minahasa', 'manado', 
                               'maengket', 'kabasaran', 'polo palo'],
            'Gorontalo': ['gorontalo', 'saronde', 'tidi'],
            'Sulawesi Tengah': ['sulawesi tengah', 'sulteng', 'palu', 'dero', 
                                'lulo', 'lumense', 'pamonte'],
            'Sulawesi Barat': ['sulawesi barat', 'sulbar', 'mamuju', 'patuddu'],
            'Sulawesi Selatan': ['sulawesi selatan', 'sulsel', 'makassar', 
                                 'bugis', 'toraja', 'gowa', 'pakarena', 
                                 'bosara', 'pajoge', 'kipas'],
            'Sulawesi Tenggara': ['sulawesi tenggara', 'sultra', 'kendari', 
                                  'buton', 'lulo', 'dinggu'],
            'Maluku': ['maluku', 'ambon', 'cakalele', 'lenso', 'bambu gila'],
            'Maluku Utara': ['maluku utara', 'ternate', 'tidore', 'saureka'],
            'Papua Barat': ['papua barat', 'manokwari', 'fak-fak'],
            'Papua': ['papua', 'irian', 'jayapura', 'asmat', 'dani', 'sentani',
                      'yospan', 'sajojo', 'perang', 'musyoh'],
        }
        
        combined = f"{title} {text}".lower()
        
        # Scoring system
        matches = []
        for region, keywords in mapping.items():
            score = sum(combined.count(kw) for kw in keywords)
            if score > 0:
                matches.append((region, score))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        return "Indonesia"
    
    def scrape_all(self, titles: List[str]) -> List[Dict]:
        """Scrape FULL content dari semua artikel"""
        print(f"\n   🔄 Memproses {len(titles)} artikel...")
        results = []
        failed = 0
        
        for i, title in enumerate(titles, 1):
            data = self.get_full_page_content(title)
            
            if data:
                # Clean text tapi jangan potong
                full_content = re.sub(r'\s+', ' ', data['full_content']).strip()
                
                results.append({
                    'judul': data['title'],
                    'deskripsi': full_content,  # FULL CONTENT dalam satu cell
                    'asal_daerah': self.detect_region(full_content, data['title']),
                    'link': data['url'],
                    'gambar': data['image']
                })
                
                print(f"   ✓ [{i}/{len(titles)}] {data['title'][:50]}... ({data['length']:,} char)")
            else:
                failed += 1
                print(f"   ✗ [{i}/{len(titles)}] Gagal")
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"\n   📊 Berhasil: {len(results)} | Gagal: {failed}")
        return results
    
    def save_to_csv(self, results: List[Dict], filename: str = 'tarian_tradisional_full.csv'):
        """Simpan hasil ke CSV - satu dokumen per baris"""
        if not results:
            print("\n   ❌ Tidak ada data untuk disimpan!")
            return None
        
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['judul'])
        df = df.sort_values(['asal_daerah', 'judul']).reset_index(drop=True)
        df.insert(0, 'no', range(1, len(df) + 1))
        
        # Simpan dengan encoding yang support karakter Indonesia
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return df
    
    def print_statistics(self, df: pd.DataFrame, filename: str):
        """Cetak statistik hasil scraping"""
        with_img = len(df[df['gambar'] != ''])
        img_pct = (with_img * 100 // len(df)) if len(df) > 0 else 0
        avg_length = df['deskripsi'].str.len().mean()
        total_chars = df['deskripsi'].str.len().sum()
        
        print("\n" + "=" * 70)
        print("   ✅ SCRAPING SELESAI!")
        print("=" * 70)
        print(f"   📁 File         : {filename}")
        print(f"   📊 Total Tarian : {len(df)} buah")
        print(f"   🖼️  Gambar      : {with_img} ({img_pct}%)")
        print(f"   📝 Rata-rata    : {avg_length:,.0f} karakter/tarian")
        print(f"   💾 Total Konten : {total_chars:,.0f} karakter")
        print("=" * 70)
        
        # Distribusi per daerah
        print("\n   📍 Distribusi per Daerah (Top 15):")
        print("   " + "-" * 66)
        for region, cnt in df['asal_daerah'].value_counts().head(15).items():
            bar_len = min(cnt, 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pct = (cnt * 100 / len(df))
            print(f"   {region:28} {bar} {cnt:3} ({pct:5.1f}%)")
        
        # Info panjang konten
        print("\n   📏 Statistik Panjang Konten:")
        print("   " + "-" * 66)
        min_idx = df['deskripsi'].str.len().idxmin()
        max_idx = df['deskripsi'].str.len().idxmax()
        print(f"   Terpendek : {df['deskripsi'].str.len().min():>8,} karakter - {df.loc[min_idx, 'judul']}")
        print(f"   Terpanjang: {df['deskripsi'].str.len().max():>8,} karakter - {df.loc[max_idx, 'judul']}")
        print(f"   Median    : {df['deskripsi'].str.len().median():>8,.0f} karakter")
        
        # Sample
        print("\n   📋 Sample Data (3 random):")
        print("   " + "-" * 66)
        for _, row in df.sample(min(3, len(df))).iterrows():
            print(f"\n   • {row['judul']}")
            print(f"     📍 {row['asal_daerah']} | 📝 {len(row['deskripsi']):,} karakter")
            preview = row['deskripsi'][:150].replace('\n', ' ')
            print(f"     {preview}...")


def main():
    """Fungsi utama"""
    print("=" * 70)
    print("   SCRAPER TARIAN TRADISIONAL INDONESIA v3")
    print("   ✓ Crawling: HANYA tarian tradisional")
    print("   ✓ Scraping: FULL content Wikipedia")
    print("   ✓ Format  : Satu dokumen = satu baris CSV")
    print("=" * 70)
    
    # Daftar manual tarian populer
    MANUAL_LIST = [
        "Tari Saman", "Tari Seudati", "Tari Ranup Lampuan", 
        "Tor-Tor", "Tari Sigale-gale", "Tari Piso Surit", "Tari Serampang Dua Belas",
        "Tari Piring", "Tari Payung", "Tari Pasambahan", "Randai",
        "Tari Zapin", "Tari Mak Inang", "Tari Sekapur Sirih", "Tari Tanggai", 
        "Tari Gending Sriwijaya", "Tari Andun", "Tari Bedana", "Tari Melinting",
        "Tari Yapong", "Tari Topeng Betawi", "Ondel-ondel", "Tari Cokek",
        "Jaipongan", "Tari Topeng Cirebon", "Tari Merak", "Tari Ketuk Tilu",
        "Tari Sintren", "Tari Ronggeng", "Tari Serimpi", "Tari Gambyong", 
        "Bedhaya", "Tari Bondan", "Tari Tayub", "Tari Dolalak", "Tari Lengger",
        "Reog Ponorogo", "Tari Gandrung", "Tari Remo", "Tari Pendet", 
        "Tari Kecak", "Tari Legong", "Tari Barong", "Tari Sanghyang", "Tari Baris",
        "Tari Rejang", "Joged Bumbung", "Gambuh", "Gendang Beleq", 
        "Caci (tarian)", "Tari Likurai", "Tari Hudoq", "Tari Kancet Ledo",
        "Tari Gong", "Tari Enggang", "Tari Maengket", "Tari Kabasaran",
        "Poco-poco", "Tari Pakarena", "Tari Bosara", "Tari Cakalele",
        "Tari Lenso", "Tari Yospan", "Tari Sajojo",
    ]
    
    scraper = TarianScraper()
    
    # Step 1: Crawling - fokus tarian tradisional
    print("\n[1/4] 🔍 Crawling artikel tarian tradisional...")
    searched_titles = scraper.search_dances()
    
    all_titles = list(set(MANUAL_LIST + searched_titles))
    print(f"\n   ✓ Total artikel ditemukan: {len(all_titles)}")
    
    # Step 2: Scraping - ambil full content
    print("\n[2/4] 📥 Scraping FULL content dari Wikipedia...")
    results = scraper.scrape_all(all_titles)
    
    # Step 3: Summary
    print(f"\n[3/4] 📊 Hasil:")
    print(f"      ✓ Berhasil: {len(results)}")
    print(f"      ✗ Gagal   : {len(all_titles) - len(results)}")
    
    # Step 4: Save
    print("\n[4/4] 💾 Menyimpan ke CSV...")
    filename = 'tarian_tradisional_full.csv'
    df = scraper.save_to_csv(results, filename)
    
    if df is not None:
        scraper.print_statistics(df, filename)
        print(f"\n   🎉 Selesai! File tersimpan di: {filename}")
        print(f"   💡 Tip: Buka dengan Excel atau pandas untuk melihat full content")
        return df
    else:
        print("\n   ❌ Gagal! Tidak ada data yang berhasil di-scrape.")
        return None


if __name__ == "__main__":
    df = main()