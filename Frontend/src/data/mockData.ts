// src/data/mockData.ts
import type { SearchResult } from "../types";

export const mockDatabase: SearchResult[] = [
  // --- DATA KAMU (SAYA UBAH SEDIKIT BIAR SESUAI TIPE) ---
  {
    id: "1",
    judul: "Adok",
    deskripsi:
      "RODIYA merupakan sastra lisan Minangkabau berbentuk pendendangan pantun-pantun diiringi tabuhan rodiya dan tarian...",
    asal_daerah: "Sumatera Barat",
    cara_main: "Dipukul",
    link: "https://id.wikipedia.org/wiki/Adok",
    gambar:
      "https://pdbifiles.nos.jkt-1.neo.id/files/2019/01/04/roro_GendangTabuik.png",
    kategori: "alat_musik", // pastikan lowercase & pake underscore sprti di filter
    category: "alat_musik", // duplicate biar aman
    score_tfidf: 0.91,
    score_jaccard: 0.85,
  },
  {
    id: "2",
    judul: "Akordeon",
    deskripsi:
      "Akordeon adalah sebuah alat musik tuts sejenis organ. Akordeon ini relatif kecil dan dimainkan dengan cara digantungkan di badan...",
    asal_daerah: "Indonesia",
    cara_main: "Lainnya",
    link: "https://id.wikipedia.org/wiki/Akordeon",
    gambar: "https://upload.wikimedia.org/wikipedia/commons/7/78/Spirk.ogv", // Note: ini video, mungkin ganti jpg kalau error
    kategori: "alat_musik",
    category: "alat_musik",
    score_tfidf: 0.88,
    score_jaccard: 0.72,
  },
  {
    id: "3",
    judul: "Aesan Gede",
    deskripsi:
      "Aesan gede adalah salah satu Busana tradisional Melayu Palembang, berasal dari Sumatra Selatan...",
    asal_daerah: "Sumatera Selatan",
    link: "https://id.wikipedia.org/wiki/Aesan_gede",
    gambar:
      "https://upload.wikimedia.org/wikipedia/commons/5/5c/Aesan_Gede_Songket_Palembang.jpg",
    kategori: "pakaian",
    category: "pakaian",
    score_tfidf: 0.95,
    score_jaccard: 0.89,
  },
  {
    id: "4",
    judul: "Bedaya",
    deskripsi:
      "Bedaya adalah bentuk tarian klasik Jawa yang dikembangkan di kalangan istana atau keraton-keraton pewaris takhta Mataram...",
    asal_daerah: "Jawa / Bangka Belitung",
    link: "https://id.wikipedia.org/wiki/Bedaya",
    gambar:
      "https://upload.wikimedia.org/wikipedia/commons/7/79/Young_dancers_at_the_kraton_%28royal_palace%29_of_Yogyakarta%2C_Java%2C_Indonesia.jpg",
    kategori: "tarian",
    category: "tarian",
    score_tfidf: 0.82,
    score_jaccard: 0.65,
  },
  {
    id: "5",
    judul: "Beksan Trunajaya",
    deskripsi:
      "Beksan Trunajaya adalah trilogi tarian klasik gaya Yogyakarta. Ketiga tarian ini diciptakan oleh Hamengkubuwana I...",
    asal_daerah: "Yogyakarta",
    link: "https://id.wikipedia.org/wiki/Beksan_Trunajaya",
    gambar:
      "https://upload.wikimedia.org/wikipedia/commons/a/a5/Beksan_Lawung_Ageng_Tingalan_Taun_Dalem_HB_X_2025_2.jpg",
    kategori: "tarian",
    category: "tarian",
    score_tfidf: 0.88,
    score_jaccard: 0.76,
  },
  // Tambahkan data lainnya di sini...
];
