// src/data/mockData.ts
import type { SearchResult } from "../types";

export const mockDatabase: SearchResult[] = [
  {
    id: 1,
    title: "Tari Saman",
    snippet:
      "Tari Saman adalah sebuah tarian Suku Gayo yang biasa ditampilkan untuk merayakan peristiwa-peristiwa penting dalam adat.",
    category: "tarian",
    score_tfidf: 0.89,
    score_jaccard: 0.75,
    image:
      "https://upload.wikimedia.org/wikipedia/commons/2/2f/Saman_Dance_of_Aceh.jpg",
  },
  {
    id: 2,
    title: "Angklung",
    snippet:
      "Angklung adalah alat musik multitonal (bernada ganda) yang secara tradisional berkembang dalam masyarakat Sunda.",
    category: "alat_musik", // Updated
    score_tfidf: 0.92,
    score_jaccard: 0.8,
    image:
      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Angklung_Sunda.jpg/1200px-Angklung_Sunda.jpg",
  },
  {
    id: 3,
    title: "Batik",
    snippet:
      "Batik adalah kain Indonesia bergambar yang pembuatannya secara khusus dengan menuliskan atau menerakan malam pada kain itu.",
    category: "pakaian",
    score_tfidf: 0.95,
    score_jaccard: 0.88,
    image:
      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Batik_Parang_Rusak_Barong.jpg/800px-Batik_Parang_Rusak_Barong.jpg",
  },
  {
    id: 4,
    title: "Tari Kecak",
    snippet:
      "Tari Kecak adalah pertunjukan tarian seni khas Bali yang lebih utama menceritakan mengenai Ramayana.",
    category: "tarian",
    score_tfidf: 0.78,
    score_jaccard: 0.65,
    image:
      "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Kecak_dance_Uluwatu.jpg/1200px-Kecak_dance_Uluwatu.jpg",
  },
  {
    id: 5,
    title: "Sasando",
    snippet:
      "Sasando adalah sebuah alat musik dawai yang dimainkan dengan dipetik. Instumen musik ini berasal dari pulau Rote.",
    category: "alat_musik", // Updated
    score_tfidf: 0.82,
    score_jaccard: 0.7,
    image:
      "https://upload.wikimedia.org/wikipedia/commons/2/23/Sasando_Rote.jpg",
  },
];
