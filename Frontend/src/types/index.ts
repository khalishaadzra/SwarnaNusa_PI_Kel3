// src/types/index.ts
import type { LucideIcon } from "lucide-react";

export interface SearchResult {
  id: number;
  title: string;
  snippet: string;
  category: "tarian" | "alat_musik" | "pakaian" | "lainnya"; // Updated category
  score_tfidf: number;
  score_jaccard: number;
  image: string;
}

export interface CategoryOption {
  id: string;
  label: string;
  icon: LucideIcon;
}
