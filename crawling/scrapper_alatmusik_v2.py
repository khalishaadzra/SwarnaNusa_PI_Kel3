"""
Web Scraper Alat Musik Tradisional Indonesia v3
- Crawling fokus HANYA alat musik tradisional
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

class AlatMusikScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AlatMusikIndonesiaScraper/3.0 (Educational Purpose)'
        })
    
    def search_instruments(self) -> List[str]:
        """Cari HANYA artikel alat musik tradisional dari Wikipedia"""
        all_titles: Set[str] = set()
        
        # FOKUS: Kata kunci spesifik untuk alat musik tradisional
        search_terms = [
            "alat musik tradisional Indonesia",
            "alat musik daerah Indonesia",
            "alat musik nusantara",
            "gamelan Indonesia",
            "alat musik pukul tradisional",
            "alat musik tiup tradisional",
            "alat musik petik tradisional",
            "alat musik gesek tradisional"
        ]
        
        print("   🔍 Mencari artikel alat musik tradisional...")
        for term in search_terms:
            titles = self._search_by_term(term, max_results=100)
            all_titles.update(titles)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"   ✓ Dari pencarian: {len(all_titles)} artikel")
        
        # FOKUS: Kategori khusus alat musik tradisional
        print("   📂 Mencari dari kategori alat musik...")
        categories = [
            "Alat_musik_tradisional_Indonesia",
            "Alat_musik_Indonesia",
            "Gamelan",
            "Alat_musik_Jawa",
            "Alat_musik_Bali",
            "Alat_musik_Sunda",
            "Alat_musik_Sumatra",
            "Alat_musik_Kalimantan",
            "Alat_musik_Sulawesi",
            "Alat_musik_Nusa_Tenggara",
            "Alat_musik_Maluku",
            "Alat_musik_Papua"
        ]
        
        for cat in categories:
            titles = self._get_category_members(cat)
            filtered_titles = {t for t in titles if self._is_traditional_instrument(t)}
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
                if self._is_traditional_instrument(title):
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
                
                cmcontinue = data.get('continue', {}).get('cmcontinue')
                if not cmcontinue:
                    break
                    
            except Exception as e:
                print(f"   ⚠️  Error kategori '{category}': {str(e)}")
                break
        
        return all_members
    
    def _is_traditional_instrument(self, title: str) -> bool:
        """
        Filter KETAT: Cek apakah artikel benar-benar tentang alat musik tradisional
        Exclude: musisi, grup musik, genre musik, festival, dll
        """
        title_lower = title.lower()
        
        # Kata kunci POSITIF (harus ada salah satu)
        instrument_keywords = [
            'gamelan', 'gong', 'bonang', 'saron', 'gender', 'slenthem',
            'gambang', 'kendang', 'ketipung', 'bedug', 'gendang', 'rebana',
            'tifa', 'kolintang', 'talempong', 'aramba', 'gordang',
            'taganing', 'garantung', 'kecapi', 'sasando', 'sampek', 'siter',
            'celempung', 'gambus', 'hasapi', 'rebab', 'suling', 'saluang',
            'serunai', 'angklung', 'calung', 'tarompet', 'serune', 'bansi',
            'pupuik', 'nafiri', 'triton', 'tehyan', 'arbab', 'tarawangsa',
            'rindik', 'ceng-ceng', 'kulcapi', 'jentreng', 'panting',
            'jatung utang', 'tuma', 'popondi', 'talindo', 'genggong',
            'karinding', 'ketuk', 'kenong', 'kempul', 'totobuang',
            'pikon', 'atowo', 'guoto', 'fu', 'tambur', 'kompang',
            'marwas', 'dol', 'terbang', 'rapai', 'geundrang', 'celempong'
        ]
        
        has_instrument_keyword = any(kw in title_lower for kw in instrument_keywords)
        
        if not has_instrument_keyword:
            return False
        
        # Kata kunci NEGATIF (exclude jika ada)
        exclude_keywords = [
            'musisi', 'pemain', 'pemusik', 'penabuh', 'seniman',
            'grup', 'band', 'orkestra', 'ensemble', 'kelompok musik',
            'festival', 'konser', 'pertunjukan', 'pementasan',
            'kompetisi', 'lomba', 'kategori:', 'daftar',
            'genre', 'aliran', 'gaya musik', 'jenis musik',
            'sejarah musik', 'musik tradisional', 'musik daerah',
            'tokoh', 'maestro', 'seniman', 'budayawan',
            'sanggar', 'komunitas', 'organisasi', 'lembaga'
        ]
        
        has_exclude = any(kw in title_lower for kw in exclude_keywords)
        
        # Exception: "Musik" di judul boleh jika diikuti nama alat musik
        if 'musik' in title_lower and not any(instr in title_lower for instr in instrument_keywords):
            return False
        
        return has_instrument_keyword and not has_exclude
    
    def get_full_page_content(self, title: str) -> Optional[Dict]:
        """
        Ambil SELURUH konten Wikipedia (bukan hanya intro)
        Termasuk: sejarah, jenis, bahan, cara pembuatan, cara bermain, dll
        """
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|pageimages|info|categories|revisions',
            'explaintext': True,
            'exsectionformat': 'plain',
            'piprop': 'original|thumbnail',
            'pithumbsize': 800,
            'inprop': 'url',
            'cllimit': 20,
            'rvprop': 'content',
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
                
                full_text = page.get('extract', '')
                
                if not full_text or len(full_text) < 200:
                    return None
                
                img_url = self._get_image_url(page)
                
                categories = []
                for cat in page.get('categories', []):
                    cat_title = cat.get('title', '').replace('Kategori:', '')
                    categories.append(cat_title)
                
                return {
                    'title': page.get('title', title),
                    'full_content': full_text,
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
            img_url = re.sub(r'/\d+px-', '/800px-', img_url)
        
        return img_url
    
    def detect_region(self, text: str, title: str) -> str:
        """Deteksi asal daerah dengan keyword yang lebih lengkap"""
        mapping = {
            'Aceh': ['aceh', 'gayo', 'alas', 'pidie', 'serune kalee', 'rapai', 'geundrang'],
            'Sumatera Utara': ['batak', 'karo', 'toba', 'mandailing', 'nias', 
                               'sumatera utara', 'tapanuli', 'simalungun', 'gordang sambilan',
                               'taganing', 'garantung', 'sarune bolon', 'hasapi', 'sulim'],
            'Sumatera Barat': ['minangkabau', 'minang', 'sumatera barat', 
                               'padang', 'talempong', 'saluang', 'rabab', 'pupuik',
                               'gandang tabuik', 'aguang'],
            'Riau': ['riau', 'melayu riau', 'gambus melayu', 'kompang melayu', 
                     'akordeon', 'gendang panjang'],
            'Kepulauan Riau': ['kepulauan riau', 'kepri'],
            'Jambi': ['jambi', 'kelintang', 'serangko'],
            'Sumatera Selatan': ['palembang', 'sumatera selatan', 'sriwijaya', 
                                 'gendang sriwijaya', 'akordeon melayu'],
            'Bengkulu': ['bengkulu', 'rejang', 'dol bengkulu', 'kulintang bengkulu'],
            'Lampung': ['lampung', 'gamolan', 'kulintang lampung', 'cetik', 'talo balak'],
            'Bangka Belitung': ['bangka', 'belitung'],
            'DKI Jakarta': ['jakarta', 'betawi', 'tanjidor', 'gambang kromong', 
                            'tehyan', 'kecrek', 'ningnong'],
            'Jawa Barat': ['sunda', 'jawa barat', 'cirebon', 'bandung', 
                           'priangan', 'angklung', 'calung', 'kacapi', 'karinding',
                           'suling sunda', 'degung', 'jengglong', 'arumba', 'tarawangsa'],
            'Banten': ['banten', 'rampak bedug', 'angklung buhun'],
            'Jawa Tengah': ['jawa tengah', 'surakarta', 'solo', 'semarang', 
                            'gamelan jawa', 'saron', 'demung', 'bonang', 'kenong',
                            'kethuk', 'gender', 'slenthem', 'rebab jawa', 'siter'],
            'DI Yogyakarta': ['yogyakarta', 'jogja', 'jogjakarta', 'keraton yogya',
                              'gamelan yogya', 'gong ageng'],
            'Jawa Timur': ['jawa timur', 'surabaya', 'ponorogo', 'banyuwangi', 
                           'madura', 'malang', 'gamelan jawa timuran', 'angklung reog'],
            'Bali': ['bali', 'balinese', 'gamelan bali', 'rindik', 'ceng-ceng', 
                     'suling bali', 'genggong', 'pereret', 'gong kebyar', 'gender wayang',
                     'trompong', 'gangsa', 'jublag', 'jegogan'],
            'Nusa Tenggara Barat': ['ntb', 'lombok', 'sumbawa', 'bima', 'sasak',
                                    'gendang beleq', 'serunai sasak', 'preret'],
            'Nusa Tenggara Timur': ['ntt', 'flores', 'sumba', 'timor', 'rote', 
                                    'manggarai', 'ende', 'sikka', 'sasando', 
                                    'foy doa', 'tambur', 'lamba'],
            'Kalimantan Barat': ['kalimantan barat', 'kalbar', 'pontianak',
                                 'dayak', 'keledi', 'kedire'],
            'Kalimantan Tengah': ['kalimantan tengah', 'kalteng', 'palangkaraya', 
                                  'dayak ngaju', 'garantung dayak', 'gandang dayak'],
            'Kalimantan Selatan': ['kalimantan selatan', 'kalsel', 'banjar', 
                                   'banjarmasin', 'panting', 'hadrah', 'kuriding'],
            'Kalimantan Timur': ['kalimantan timur', 'kaltim', 'kutai', 
                                 'samarinda', 'dayak', 'sampek', 'sape', 
                                 'jatung utang', 'tuma', 'kangkanung'],
            'Kalimantan Utara': ['kalimantan utara', 'kaltara', 'bulungan'],
            'Sulawesi Utara': ['sulawesi utara', 'minahasa', 'manado', 
                               'kolintang', 'suling minahasa', 'salude'],
            'Gorontalo': ['gorontalo', 'popondi'],
            'Sulawesi Tengah': ['sulawesi tengah', 'sulteng', 'palu', 
                                'gong sulawesi', 'pui-pui'],
            'Sulawesi Barat': ['sulawesi barat', 'sulbar', 'mamuju', 'mandar'],
            'Sulawesi Selatan': ['sulawesi selatan', 'sulsel', 'makassar', 
                                 'bugis', 'toraja', 'gowa', 'kecapi bugis',
                                 'talindo', 'gambus makassar', 'gendang bugis'],
            'Sulawesi Tenggara': ['sulawesi tenggara', 'sultra', 'kendari', 
                                  'buton', 'suling lembang'],
            'Maluku': ['maluku', 'ambon', 'tifa maluku', 'tahuri', 
                       'totobuang', 'ukulele maluku', 'sulepe', 'nafiri maluku'],
            'Maluku Utara': ['maluku utara', 'ternate', 'tidore'],
            'Papua Barat': ['papua barat', 'manokwari'],
            'Papua': ['papua', 'irian', 'jayapura', 'asmat', 'dani', 'sentani',
                      'tifa papua', 'pikon', 'atowo', 'guoto', 'suling papua',
                      'fu papua', 'triton', 'tambur papua'],
        }
        
        combined = f"{title} {text}".lower()
        
        matches = []
        for region, keywords in mapping.items():
            score = sum(combined.count(kw) for kw in keywords)
            if score > 0:
                matches.append((region, score))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        return "Indonesia"
    
    def detect_playing_method(self, text: str, title: str) -> str:
        """Deteksi cara memainkan alat musik"""
        combined = f"{title} {text}".lower()
        
        # Multi-label detection (bisa lebih dari satu cara)
        methods = []
        
        if any(kw in combined for kw in ['dipukul', 'ditabuh', 'pukul', 'tabuh', 
                                          'memukul', 'menabuh', 'dipalu', 'diketok']):
            methods.append('Dipukul')
        
        if any(kw in combined for kw in ['dipetik', 'petik', 'memetik', 'dawai', 
                                          'senar', 'string']):
            methods.append('Dipetik')
        
        if any(kw in combined for kw in ['ditiup', 'tiup', 'meniup', 'hembusan', 
                                          'aerofon', 'bamboo flute']):
            methods.append('Ditiup')
        
        if any(kw in combined for kw in ['digesek', 'gesek', 'menggesek', 'bow']):
            methods.append('Digesek')
        
        if any(kw in combined for kw in ['digoyangkan', 'goyang', 'dikocok', 
                                          'digetarkan', 'idiofon']):
            methods.append('Digoyangkan')
        
        if methods:
            return ', '.join(methods)
        
        return 'Lainnya'
    
    def detect_instrument_type(self, text: str, title: str) -> str:
        """Deteksi jenis alat musik"""
        combined = f"{title} {text}".lower()
        
        type_keywords = {
            'Perkusi/Pukul': ['gamelan', 'gong', 'kendang', 'gendang', 'bonang', 
                              'saron', 'gender', 'kolintang', 'talempong', 'tifa',
                              'rebana', 'bedug', 'ketipung', 'aramba'],
            'Petik': ['kecapi', 'sasando', 'sampek', 'siter', 'celempung', 
                      'gambus', 'hasapi', 'sape', 'jentreng'],
            'Gesek': ['rebab', 'tehyan', 'arbab', 'ohyan', 'tarawangsa'],
            'Tiup': ['suling', 'saluang', 'serunai', 'bansi', 'pupuik', 
                     'nafiri', 'tarompet', 'triton', 'sulim'],
            'Idiofon': ['angklung', 'calung', 'karinding', 'genggong', 
                        'rindik', 'ceng-ceng'],
        }
        
        for instr_type, keywords in type_keywords.items():
            if any(kw in combined for kw in keywords):
                return instr_type
        
        return 'Alat Musik Tradisional'
    
    def scrape_all(self, titles: List[str]) -> List[Dict]:
        """Scrape FULL content dari semua artikel"""
        print(f"\n   🔄 Memproses {len(titles)} artikel...")
        results = []
        failed = 0
        
        for i, title in enumerate(titles, 1):
            data = self.get_full_page_content(title)
            
            if data:
                full_content = re.sub(r'\s+', ' ', data['full_content']).strip()
                
                results.append({
                    'judul': data['title'],
                    'konten_lengkap': full_content,
                    'panjang_karakter': data['length'],
                    'jenis_alat_musik': self.detect_instrument_type(full_content, data['title']),
                    'cara_memainkan': self.detect_playing_method(full_content, data['title']),
                    'asal_daerah': self.detect_region(full_content, data['title']),
                    'kategori': data['categories'],
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
    
    def save_to_csv(self, results: List[Dict], filename: str = 'alat_musik_tradisional_full.csv'):
        """Simpan hasil ke CSV - satu dokumen per baris"""
        if not results:
            print("\n   ❌ Tidak ada data untuk disimpan!")
            return None
        
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['judul'])
        df = df.sort_values(['asal_daerah', 'jenis_alat_musik', 'judul']).reset_index(drop=True)
        df.insert(0, 'no', range(1, len(df) + 1))
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return df
    
    def print_statistics(self, df: pd.DataFrame, filename: str):
        """Cetak statistik hasil scraping"""
        with_img = len(df[df['gambar'] != ''])
        img_pct = (with_img * 100 // len(df)) if len(df) > 0 else 0
        avg_length = df['panjang_karakter'].mean()
        total_chars = df['panjang_karakter'].sum()
        
        print("\n" + "=" * 70)
        print("   ✅ SCRAPING SELESAI!")
        print("=" * 70)
        print(f"   📁 File             : {filename}")
        print(f"   📊 Total Alat Musik : {len(df)} buah")
        print(f"   🖼️  Gambar          : {with_img} ({img_pct}%)")
        print(f"   📝 Rata-rata        : {avg_length:,.0f} karakter/alat musik")
        print(f"   💾 Total Konten     : {total_chars:,.0f} karakter")
        print("=" * 70)
        
        # Distribusi per daerah
        print("\n   📍 Distribusi per Daerah (Top 15):")
        print("   " + "-" * 66)
        for region, cnt in df['asal_daerah'].value_counts().head(15).items():
            bar_len = min(cnt, 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pct = (cnt * 100 / len(df))
            print(f"   {region:28} {bar} {cnt:3} ({pct:5.1f}%)")
        
        # Distribusi per jenis
        print("\n   🎵 Distribusi per Jenis Alat Musik:")
        print("   " + "-" * 66)
        for instr_type, cnt in df['jenis_alat_musik'].value_counts().items():
            bar_len = min(cnt, 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pct = (cnt * 100 / len(df))
            print(f"   {instr_type:28} {bar} {cnt:3} ({pct:5.1f}%)")
        
        # Distribusi per cara main
        print("\n   🎼 Distribusi per Cara Memainkan:")
        print("   " + "-" * 66)
        for method, cnt in df['cara_memainkan'].value_counts().head(10).items():
            bar_len = min(cnt // 2, 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pct = (cnt * 100 / len(df))
            print(f"   {method:28} {bar} {cnt:3} ({pct:5.1f}%)")
        
        # Info panjang konten
        print("\n   📏 Statistik Panjang Konten:")
        print("   " + "-" * 66)
        print(f"   Terpendek : {df['panjang_karakter'].min():>8,} karakter - {df.loc[df['panjang_karakter'].idxmin(), 'judul']}")
        print(f"   Terpanjang: {df['panjang_karakter'].max():>8,} karakter - {df.loc[df['panjang_karakter'].idxmax(), 'judul']}")
        print(f"   Median    : {df['panjang_karakter'].median():>8,.0f} karakter")
        
        # Sample
        print("\n   📋 Sample Data (3 random):")
        print("   " + "-" * 66)
        for _, row in df.sample(min(3, len(df))).iterrows():
            print(f"\n   • {row['judul']}")
            print(f"     🎵 {row['jenis_alat_musik']} | 🎼 {row['cara_memainkan']}")
            print(f"     📍 {row['asal_daerah']} | 📝 {row['panjang_karakter']:,} karakter")
            preview = row['konten_lengkap'][:150].replace('\n', ' ')
            print(f"     {preview}...")


def main():
    """Fungsi utama"""
    print("=" * 70)
    print("   SCRAPER ALAT MUSIK TRADISIONAL INDONESIA v3")
    print("   ✓ Crawling: HANYA alat musik tradisional")
    print("   ✓ Scraping: FULL content Wikipedia")
    print("   ✓ Format  : Satu dokumen = satu baris CSV")
    print("=" * 70)
    
    # Daftar manual alat musik populer
    MANUAL_LIST = [
        # Gamelan & Perkusi
        "Gamelan", "Gong", "Bonang", "Saron", "Gender (alat musik)", "Slenthem",
        "Gambang", "Kendang", "Ketipung", "Bedug", "Gendang", "Rebana",
        "Tifa", "Kolintang", "Talempong", "Aramba", "Gordang Sambilan",
        "Taganing", "Garantung", "Gendang Beleq", "Ketuk", "Kenong",
        "Kempul", "Terbang", "Kompang", "Marwas", "Rindik", "Ceng-ceng",
        
        # Petik
        "Kecapi", "Sasando", "Sampek", "Siter", "Celempung", "Gambus",
        "Hasapi", "Kucapi", "Jungga", "Popondi", "Talindo", "Jentreng",
        "Tarawangsa", "Panting", "Sape",
        
        # Gesek
        "Rebab", "Tehyan", "Arbab", "Ohyan",
        
        # Tiup
        "Suling", "Saluang", "Serunai", "Serune Kalee", "Bansi", "Pupuik",
        "Nafiri", "Tarompet", "Selompret", "Triton (alat musik)", 
        "Tulali", "Fu", "Tongali", "Sarune Bolon",
        
        # Idiofon
        "Angklung", "Calung", "Karinding", "Genggong", "Kecrek",
        
        # Per Daerah Spesifik
        "Gambang Kromong", "Tanjidor", "Degung", "Arumba", "Gamelan Bali",
        "Gender Wayang", "Trompong", "Gangsa", "Gong Kebyar",
        "Gendang Sriwijaya", "Rabab", "Gandang Tabuik", "Talempong Pacik",
        "Keledi", "Jatung Utang", "Tuma", "Kangkanung", "Kuriding",
        "Totobuang", "Tahuri", "Ukulele Maluku", "Pikon", "Atowo", "Guoto",
    ]
    
    scraper = AlatMusikScraper()
    
    # Step 1: Crawling - fokus alat musik tradisional
    print("\n[1/4] 🔍 Crawling artikel alat musik tradisional...")
    searched_titles = scraper.search_instruments()
    
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
    filename = 'alat_musik_tradisional_full.csv'
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