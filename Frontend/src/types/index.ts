// src/types/index.ts
import type { LucideIcon } from 'lucide-react';

export interface SearchResult {
  id: number | string; // Bisa angka atau string
  // Support format lama & baru
  title?: string;
  judul?: string;
  
  snippet?: string;
  deskripsi?: string;
  
  image?: string;
  gambar?: string;
  
  category: string; 
  kategori?: string;

  score_tfidf: number;
  score_jaccard: number;
  
  // Data tambahan kamu
  asal_daerah?: string;
  cara_main?: string;
  link?: string;
}

export interface CategoryOption {
  id: string;
  label: string;
  icon: LucideIcon;
}