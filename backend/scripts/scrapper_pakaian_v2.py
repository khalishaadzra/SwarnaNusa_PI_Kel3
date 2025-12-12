"""
Web Scraper Pakaian Tradisional Indonesia v3
- Crawling fokus HANYA pakaian/busana tradisional
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

class PakaianScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PakaianIndonesiaScraper/3.0 (Educational Purpose)'
        })
    
    def search_clothes(self) -> List[str]:
        """Cari HANYA artikel pakaian/busana tradisional dari Wikipedia"""
        all_titles: Set[str] = set()
        
        # FOKUS: Kata kunci spesifik untuk pakaian tradisional
        search_terms = [
            "Pakaian tradisional Indonesia",
            "Pakaian adat Indonesia",
            "Busana tradisional Indonesia",
            "Baju adat Indonesia",
            "Kain tradisional Indonesia"
        ]
        
        print("   🔍 Mencari artikel pakaian tradisional...")
        for term in search_terms:
            titles = self._search_by_term(term, max_results=100)
            all_titles.update(titles)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print(f"   ✓ Dari pencarian: {len(all_titles)} artikel")
        
        # FOKUS: Kategori khusus pakaian tradisional
        print("   📂 Mencari dari kategori pakaian...")
        categories = [
            "Pakaian_tradisional_Indonesia",
            "Pakaian_Indonesia",
            "Pakaian_adat",
            "Pakaian_Jawa",
            "Pakaian_Bali",
            "Pakaian_Sumatra",
            "Pakaian_Kalimantan",
            "Pakaian_Sulawesi",
            "Pakaian_Nusa_Tenggara",
            "Pakaian_Maluku",
            "Pakaian_Papua",
            "Kain_Indonesia",
            "Tekstil_Indonesia"
        ]
        
        for cat in categories:
            titles = self._get_category_members(cat)
            filtered_titles = {t for t in titles if self._is_traditional_clothing(t)}
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
                if self._is_traditional_clothing(title):
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
    
    def _is_traditional_clothing(self, title: str) -> bool:
        """
        Filter KETAT: Cek apakah artikel benar-benar tentang pakaian tradisional
        Exclude: desainer, toko, merek, perusahaan, dll
        """
        title_lower = title.lower()
        
        # Kata kunci POSITIF (harus ada salah satu)
        clothing_keywords = [
            'pakaian', 'baju', 'busana', 'kain', 'kebaya', 'sarung', 'songket',
            'batik', 'ulos', 'tenun', 'ikat', 'beskap', 'blangkon', 'surjan',
            'udeng', 'kampuh', 'dodot', 'jarik', 'endek', 'gringsing',
            'sapei sapaq', 'koteka', 'teluk belanga', 'bundo kanduang',
            'baju kurung', 'baju bodo', 'ulee balang', 'limpapeh',
            'jumputan', 'sasirangan', 'lurik', 'troso', 'prada', 'songket',
            'tapis', 'saput', 'destar', 'ikat kepala', 'selendang',
            'rok rumbai', 'baju pokko', 'baju cele', 'lipa saqbe'
        ]
        
        has_clothing_keyword = any(kw in title_lower for kw in clothing_keywords)
        
        if not has_clothing_keyword:
            return False
        
        # Kata kunci NEGATIF (exclude jika ada)
        exclude_keywords = [
            'desainer', 'perancang', 'fashion designer', 'merek', 'brand',
            'toko', 'butik', 'perusahaan', 'industri', 'pabrik',
            'kategori:', 'daftar', 'museum', 'pameran', 'festival',
            'kompetisi', 'lomba', 'kontes', 'komunitas', 'organisasi',
            'sekolah', 'akademi', 'institut', 'universitas',
            'model', 'peragawan', 'fotografer', 'stylist'
        ]
        
        has_exclude = any(kw in title_lower for kw in exclude_keywords)
        
        return has_clothing_keyword and not has_exclude
    
    def get_full_page_content(self, title: str) -> Optional[Dict]:
        """
        Ambil SELURUH konten Wikipedia (bukan hanya intro)
        Termasuk: sejarah, jenis, bahan, cara pembuatan, penggunaan, dll
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
            'Aceh': ['aceh', 'gayo', 'alas', 'ulee balang', 'seuke barat'],
            'Sumatera Utara': ['batak', 'karo', 'toba', 'mandailing', 'nias', 
                               'sumatera utara', 'tapanuli', 'ulos', 'ragi hotang'],
            'Sumatera Barat': ['minangkabau', 'minang', 'sumatera barat', 
                               'padang', 'bundo kanduang', 'limpapeh', 'tanduak'],
            'Riau': ['riau', 'melayu riau', 'teluk belanga', 'cekak musang'],
            'Kepulauan Riau': ['kepulauan riau', 'kepri'],
            'Jambi': ['jambi', 'kurung tanggung'],
            'Sumatera Selatan': ['palembang', 'sumatera selatan', 'sriwijaya', 
                                 'songket palembang', 'aesan gede'],
            'Bengkulu': ['bengkulu', 'rejang'],
            'Lampung': ['lampung', 'tapis', 'pepadun', 'saibatin'],
            'Bangka Belitung': ['bangka', 'belitung', 'paksian'],
            'DKI Jakarta': ['jakarta', 'betawi', 'sadariah', 'abang none'],
            'Jawa Barat': ['sunda', 'jawa barat', 'cirebon', 'bandung', 
                           'priangan', 'kebaya sunda', 'pangsi'],
            'Banten': ['banten', 'pengantin banten'],
            'Jawa Tengah': ['jawa tengah', 'surakarta', 'solo', 'semarang', 
                            'beskap', 'surjan', 'kebaya jawa', 'jarik'],
            'DI Yogyakarta': ['yogyakarta', 'jogja', 'jogjakarta', 'keraton yogya',
                              'dodot', 'kampuh', 'ageng'],
            'Jawa Timur': ['jawa timur', 'surabaya', 'ponorogo', 'banyuwangi', 
                           'madura', 'malang', 'pesa\'an'],
            'Bali': ['bali', 'balinese', 'udeng', 'kebaya bali', 'endek', 
                     'gringsing', 'kamen', 'sabuk prade'],
            'Nusa Tenggara Barat': ['ntb', 'lombok', 'sumbawa', 'bima', 'sasak',
                                    'pegon', 'songket lombok'],
            'Nusa Tenggara Timur': ['ntt', 'flores', 'sumba', 'timor', 'manggarai', 
                                    'ende', 'sikka', 'tenun ikat', 'tenun ntt'],
            'Kalimantan Barat': ['kalimantan barat', 'kalbar', 'pontianak',
                                 'king baba', 'king bibinge'],
            'Kalimantan Tengah': ['kalimantan tengah', 'kalteng', 'palangkaraya', 
                                  'dayak ngaju', 'sangkarut'],
            'Kalimantan Selatan': ['kalimantan selatan', 'kalsel', 'banjar', 
                                   'banjarmasin', 'bagajah gamuling'],
            'Kalimantan Timur': ['kalimantan timur', 'kaltim', 'kutai', 
                                 'samarinda', 'dayak', 'ta\'a', 'sapei sapaq'],
            'Kalimantan Utara': ['kalimantan utara', 'kaltara', 'bulang burai'],
            'Sulawesi Utara': ['sulawesi utara', 'minahasa', 'manado', 'laku tepu'],
            'Gorontalo': ['gorontalo', 'biliu', 'mukuta'],
            'Sulawesi Tengah': ['sulawesi tengah', 'sulteng', 'palu', 'nggembe'],
            'Sulawesi Barat': ['sulawesi barat', 'sulbar', 'mamuju', 'mandar'],
            'Sulawesi Selatan': ['sulawesi selatan', 'sulsel', 'makassar', 
                                 'bugis', 'toraja', 'gowa', 'baju bodo', 
                                 'baju pokko', 'lipa saqbe'],
            'Sulawesi Tenggara': ['sulawesi tenggara', 'sultra', 'kendari', 
                                  'buton', 'tolaki'],
            'Maluku': ['maluku', 'ambon', 'cele', 'manteren lamo'],
            'Maluku Utara': ['maluku utara', 'ternate', 'tidore', 'baju koje'],
            'Papua Barat': ['papua barat', 'manokwari', 'ewer'],
            'Papua': ['papua', 'irian', 'jayapura', 'asmat', 'dani', 'sentani',
                      'koteka', 'rok rumbai', 'sali', 'holim'],
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
    
    def detect_type(self, text: str, title: str) -> str:
        """Deteksi jenis pakaian"""
        combined = f"{title} {text}".lower()
        
        type_keywords = {
            'Baju/Atasan': ['baju', 'kebaya', 'blus', 'kemeja', 'beskap', 'bundo kanduang'],
            'Kain/Bawahan': ['kain', 'sarung', 'jarik', 'kampuh', 'dodot', 'tapis'],
            'Tenun': ['tenun', 'songket', 'ulos', 'endek', 'gringsing', 'ikat'],
            'Batik': ['batik', 'jumputan', 'sasirangan', 'tritik'],
            'Aksesori': ['udeng', 'blangkon', 'destar', 'ikat kepala', 'selendang', 'sabuk'],
            'Pakaian Lengkap': ['pakaian adat', 'busana adat', 'pakaian tradisional'],
        }
        
        for cloth_type, keywords in type_keywords.items():
            if any(kw in combined for kw in keywords):
                return cloth_type
        
        return "Pakaian Tradisional"
    
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
                    'deskripsi': full_content,
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
    
    def save_to_csv(self, results: List[Dict], filename: str = 'pakaian_tradisional_full.csv'):
        """Simpan hasil ke CSV - satu dokumen per baris"""
        if not results:
            print("\n   ❌ Tidak ada data untuk disimpan!")
            return None
        
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['judul'])
        df = df.sort_values(['asal_daerah', 'judul']).reset_index(drop=True)
        df.insert(0, 'no', range(1, len(df) + 1))
        
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
        print(f"   📁 File          : {filename}")
        print(f"   📊 Total Pakaian : {len(df)} buah")
        print(f"   🖼️  Gambar       : {with_img} ({img_pct}%)")
        print(f"   📝 Rata-rata     : {avg_length:,.0f} karakter/pakaian")
        print(f"   💾 Total Konten  : {total_chars:,.0f} karakter")
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
    print("   SCRAPER PAKAIAN TRADISIONAL INDONESIA v3")
    print("   ✓ Crawling: HANYA pakaian tradisional")
    print("   ✓ Scraping: FULL content Wikipedia")
    print("   ✓ Format  : Satu dokumen = satu baris CSV")
    print("=" * 70)
    
    # Daftar manual pakaian populer
    MANUAL_LIST = [
        "Ulee Balang", "Baju Kurung", "Ulos", "Baju Adat Batak",
        "Bundo Kanduang", "Limpapeh Rumah Nan Gadang", "Songket",
        "Teluk Belanga", "Baju Kebaya", "Kebaya Encim", "Baju Bodo",
        "Pakaian adat Betawi", "Kebaya Betawi", "Batik", "Batik Jawa",
        "Beskap", "Blangkon", "Surjan", "Jarik", "Kebaya Jawa",
        "Pakaian adat Sunda", "Kebaya Sunda", "Dodot", "Kampuh",
        "Pakaian adat Bali", "Udeng", "Kebaya Bali", "Kain Endek",
        "Kain Gringsing", "Sapei Sapaq", "Pakaian adat Dayak",
        "Ta'a", "King Baba", "Pakaian adat Toraja", "Baju Pokko",
        "Baju Cele", "Pakaian adat Bugis", "Lipa Saqbe", 
        "Pakaian adat Makassar", "Baju Nggembe", "Koteka", "Rok Rumbai",
        "Pakaian adat Papua", "Ewer", "Pakaian adat Maluku",
        "Pakaian adat Aceh", "Pakaian adat Lampung", "Tapis",
        "Pakaian adat Jambi", "Pakaian adat Bengkulu", "Pakaian adat Riau",
        "Pakaian adat Sumatera Selatan", "Aesan Gede",
        "Pakaian adat NTT", "Pakaian adat NTB", "Tenun Ikat",
        "Tenun NTT", "Kain Timor", "Sasirangan", "Jumputan",
    ]
    
    scraper = PakaianScraper()
    
    # Step 1: Crawling - fokus pakaian tradisional
    print("\n[1/4] 🔍 Crawling artikel pakaian tradisional...")
    searched_titles = scraper.search_clothes()
    
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
    filename = 'pakaian_tradisional_full.csv'
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