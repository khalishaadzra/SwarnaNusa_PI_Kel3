// src/components/SearchSection.tsx
import React, { useState, useEffect } from "react";
import {
  Search,
  Sparkles,
  Layers,
  Calculator,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  X,
  Activity,
  Timer,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { SearchResult } from "../types";
import { mockDatabase } from "../data/mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const algoTabs = [
  { id: "all", label: "Semua", icon: Layers },
  { id: "tfidf", label: "TF-IDF", icon: BarChart3 },
  { id: "jaccard", label: "Jaccard", icon: Calculator },
];

const ITEMS_PER_PAGE = 4;

// --- TIPE DATA EVALUASI ---
interface EvalMetrics {
  precision: number;
  recall: number;
  f1: number;
}

interface EvalResult {
  query: string;
  runtime: {
    tfidf: number;
    jaccard: number;
    hybrid: number;
  };
  tfidf: EvalMetrics;
  jaccard: EvalMetrics;
  hybrid: EvalMetrics;
  counts: {
    relevant_count: number;
  };
}

const SearchSection: React.FC = () => {
  const navigate = useNavigate();

  // --- STATE ---
  const shouldRestore = sessionStorage.getItem("restore_search") === "true";

  const [query, setQuery] = useState<string>(() => {
    return shouldRestore ? sessionStorage.getItem("swarna_query") || "" : "";
  });

  const [results, setResults] = useState<SearchResult[]>(() => {
    if (!shouldRestore) return [];
    const saved = sessionStorage.getItem("swarna_results");
    return saved ? JSON.parse(saved) : [];
  });

  const [hasSearched, setHasSearched] = useState<boolean>(() => {
    if (!shouldRestore) return false;
    return sessionStorage.getItem("swarna_hasSearched") === "true";
  });

  const [activeAlgoTab, setActiveAlgoTab] = useState<string>(() => {
    if (!shouldRestore) return "all";
    return sessionStorage.getItem("swarna_tab") || "all";
  });

  const [pageIndex, setPageIndex] = useState<number>(() => {
    if (!shouldRestore) return 0;
    const page = sessionStorage.getItem("swarna_page");
    return page ? parseInt(page) : 0;
  });

  const [isSearching, setIsSearching] = useState<boolean>(false);

  // --- STATE EVALUASI ---
  const [showEvalModal, setShowEvalModal] = useState<boolean>(false);
  const [evalData, setEvalData] = useState<EvalResult | null>(null);
  const [isEvalLoading, setIsEvalLoading] = useState<boolean>(false);

  // --- EFFECT ---
  useEffect(() => {
    sessionStorage.removeItem("restore_search");
  }, []);

  useEffect(() => {
    sessionStorage.setItem("swarna_query", query);
    sessionStorage.setItem("swarna_results", JSON.stringify(results));
    sessionStorage.setItem("swarna_hasSearched", String(hasSearched));
    sessionStorage.setItem("swarna_tab", activeAlgoTab);
    sessionStorage.setItem("swarna_page", String(pageIndex));
  }, [query, results, hasSearched, activeAlgoTab, pageIndex]);

  // --- CORE SEARCH LOGIC (DIPISAH SUPAYA BISA DIPANGGIL TAB) ---
  const executeSearch = async (searchQuery: string, algoMode: string) => {
    if (!searchQuery) return;

    setIsSearching(true);
    setPageIndex(0);

    try {
      let modeParam = algoMode;
      if (modeParam === "all") modeParam = "combined";

      const response = await fetch(
        `${API_BASE_URL}/search?q=${encodeURIComponent(
          searchQuery
        )}&mode=${modeParam}`
      );

      const data = await response.json();

      const mappedResults = data.results.map((item: any) => ({
        id: item.document.no,
        judul: item.document.judul,
        deskripsi: item.document.deskripsi,
        gambar: item.document.gambar,
        kategori: item.document.kategori,
        asal_daerah: item.document.asal_daerah,
        cara_main: item.document.cara_main,
        link: item.document.link,
        score_tfidf: item.tfidf_score,
        score_jaccard: item.jaccard_score,
      }));

      setResults(mappedResults);
      setHasSearched(true);
    } catch (error) {
      console.error("Error fetching:", error);
      // Fallback
      const allMatches = mockDatabase.filter(
        (item) =>
          (item.judul || item.title || "")
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          (item.deskripsi || item.snippet || "")
            .toLowerCase()
            .includes(searchQuery.toLowerCase())
      );
      setResults(allMatches);
      setHasSearched(true);
    } finally {
      setIsSearching(false);
    }
  };

  // --- EVENT HANDLERS ---
  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(query, activeAlgoTab);
  };

  const handleTabClick = (tabId: string) => {
    setActiveAlgoTab(tabId);
    // Jika sudah ada query, langsung search ulang agar urutan data berubah
    if (query) {
      executeSearch(query, tabId);
    }
  };

  const handleEvaluate = async () => {
    if (!query) return;
    setShowEvalModal(true);
    setIsEvalLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/evaluate?q=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      setEvalData(data);
    } catch (error) {
      console.error("Error evaluating:", error);
    } finally {
      setIsEvalLoading(false);
    }
  };

  // Logic Pagination
  const totalPages = Math.ceil(results.length / ITEMS_PER_PAGE);
  const currentResults = results.slice(
    pageIndex * ITEMS_PER_PAGE,
    (pageIndex + 1) * ITEMS_PER_PAGE
  );

  const nextPage = () => {
    if (pageIndex < totalPages - 1) setPageIndex((prev) => prev + 1);
  };

  const prevPage = () => {
    if (pageIndex > 0) setPageIndex((prev) => prev - 1);
  };

  const handleCardClick = (item: SearchResult) => {
    sessionStorage.setItem("restore_search", "true");
    navigate(`/detail/${item.id}`, { state: item });
  };

  return (
    <section
      id="search"
      className="min-h-screen bg-swarna-primary relative overflow-hidden flex flex-col"
    >
      <div
        className="absolute inset-0 pointer-events-none mix-blend-overlay animate-move-batik"
        style={{
          backgroundImage: "url('/batik-awan.png')",
          backgroundSize: "600px",
          backgroundRepeat: "repeat",
        }}
      ></div>

      <div className="container mx-auto px-6 max-w-7xl relative z-10 flex-grow pt-28">
        {/* Header */}
        <div
          className={`text-center transition-all duration-700 ${
            hasSearched ? "mb-6" : "mb-10"
          }`}
        >
          <div className="inline-flex items-center gap-2 mt-5 mb-3 px-4 py-1.5 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-gold text-xs font-medium animate-fade-in-up">
            <Sparkles className="w-3 h-3" />
            <span>Mesin Pencari Budaya</span>
          </div>
          <h2
            className="font-serif text-5xl md:text-4xl font-bold text-swarna-light mb-4 drop-shadow-md animate-fade-in-up"
            style={{ animationDelay: "0.1s" }}
          >
            Telusuri Jejak Budaya
          </h2>
          <p
            className="text-swarna-light/80 text-base md:text-m max-w-2xl mx-auto animate-fade-in-up"
            style={{ animationDelay: "0.2s" }}
          >
            Temukan makna di balik setiap gerak, nada, dan corak Nusantara.
          </p>
        </div>

        {/* Search Box */}
        <div
          className={`bg-swarna-light/10 backdrop-blur-md border border-swarna-light/30 p-1.5 rounded-[1.5rem] shadow-xl transition-all duration-500 mx-auto ${
            hasSearched ? "max-w-2xl" : "max-w-2xl"
          }`}
        >
          <form onSubmit={handleFormSubmit} className="flex gap-2">
            <div className="relative flex-grow group">
              <div className="absolute left-5 top-1/2 -translate-y-1/2 text-swarna-dark/50 group-focus-within:text-swarna-primary transition-colors">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="Cari budaya... (misal: Angklung, Tarian Aceh, Batik)"
                className="w-full pl-12 pr-4 h-8 md:h-10 rounded-[1.2rem] bg-swarna-light text-swarna-dark text-base font-medium shadow-inner focus:outline-none focus:ring-4 focus:ring-swarna-gold/30 transition-all placeholder:text-swarna-dark/40"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="h-12 md:h-10 px-6 md:px-8 bg-swarna-gold hover:bg-white hover:text-swarna-primary text-swarna-dark rounded-[1.2rem] font-bold text-base transition-all shadow-lg hover:shadow-swarna-gold/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSearching ? "..." : "Cari"}
            </button>
          </form>
        </div>

        {/* Loading */}
        {isSearching && (
          <div className="mt-12 text-center">
            <div className="inline-block w-8 h-8 border-4 border-swarna-gold border-t-transparent rounded-full animate-spin"></div>
            <p className="text-swarna-light/70 mt-2 text-sm animate-pulse">
              Sedang menelusuri korpus...
            </p>
          </div>
        )}

        {/* Hasil Pencarian */}
        {hasSearched && !isSearching && (
          <div className="mt-10 animate-fade-in-up pb-20">
            {/* Controls */}
            <div className="flex justify-center items-center gap-4 mb-8">
              {/* TABS ALGORITMA: KLIK MEMICU SEARCH ULANG */}
              <div className="inline-flex bg-black/20 backdrop-blur-sm p-1 rounded-full border border-white/10 shadow-inner">
                {algoTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabClick(tab.id)}
                    className={`relative px-5 py-2 rounded-full text-xs md:text-sm font-bold transition-all duration-300 flex items-center gap-2 ${
                      activeAlgoTab === tab.id
                        ? "bg-swarna-light text-swarna-dark shadow-md scale-105"
                        : "text-swarna-light/70 hover:text-swarna-light hover:bg-white/10"
                    }`}
                  >
                    <tab.icon
                      className={`w-3 h-3 ${
                        activeAlgoTab === tab.id ? "text-swarna-primary" : ""
                      }`}
                    />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tombol Evaluasi */}
              <button
                onClick={handleEvaluate}
                title="Lihat Evaluasi Model"
                className="p-3 rounded-full bg-black/20 border border-white/10 text-swarna-gold hover:bg-swarna-gold hover:text-swarna-dark transition-all duration-300 shadow-lg hover:shadow-swarna-gold/50 active:scale-95 group"
              >
                <AlertCircle className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              </button>
            </div>

            {results.length === 0 ? (
              <div className="text-center py-8 bg-black/10 rounded-2xl border border-white/5">
                <p className="text-swarna-light/60 text-base">
                  Tidak ada hasil ditemukan untuk "{query}".
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-6 px-2">
                  <p className="text-swarna-light/60 text-sm">
                    Menampilkan{" "}
                    <span className="text-swarna-gold font-bold">
                      {results.length}
                    </span>{" "}
                    hasil
                  </p>

                  <div className="flex items-center gap-3">
                    <span className="text-swarna-light/50 text-xs uppercase tracking-widest mr-2 hidden sm:inline-block">
                      Hal {pageIndex + 1} / {totalPages}
                    </span>
                    <button
                      onClick={prevPage}
                      disabled={pageIndex === 0}
                      className="p-2 rounded-full bg-swarna-light/10 hover:bg-swarna-gold hover:text-swarna-dark text-swarna-light disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    <button
                      onClick={nextPage}
                      disabled={pageIndex === totalPages - 1}
                      className="p-2 rounded-full bg-swarna-light/10 hover:bg-swarna-gold hover:text-swarna-dark text-swarna-light disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {currentResults.map((item, index) => (
                    <div
                      key={item.id}
                      onClick={() => handleCardClick(item)}
                      className="bg-swarna-light rounded-2xl overflow-hidden shadow-lg hover:shadow-xl hover:shadow-swarna-gold/20 transition-all duration-300 hover:-translate-y-2 group flex flex-col h-full border border-swarna-light/50 cursor-pointer"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="aspect-video w-full overflow-hidden relative bg-gray-100">
                        <img
                          src={item.gambar || item.image}
                          alt={item.judul || item.title}
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                        />
                        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur px-2 py-0.5 rounded-full text-[10px] font-bold text-swarna-primary uppercase tracking-wider shadow-sm">
                          {(item.kategori || item.category || "").replace(
                            /_/g,
                            " "
                          )}
                        </div>
                      </div>

                      <div className="p-5 flex flex-col flex-grow">
                        <h3 className="font-serif text-lg font-bold text-swarna-dark mb-2 group-hover:text-swarna-primary transition-colors line-clamp-1">
                          {item.judul || item.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-4 line-clamp-3 leading-relaxed flex-grow">
                          {item.deskripsi || item.snippet}
                        </p>

                        <div className="bg-swarna-primary/5 rounded-xl p-3 space-y-2 mt-auto">
                          {(activeAlgoTab === "all" ||
                            activeAlgoTab === "tfidf") && (
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-swarna-dark/50 w-10">
                                TF-IDF
                              </span>
                              <div className="flex-grow h-1.5 bg-swarna-dark/10 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-swarna-primary rounded-full"
                                  style={{
                                    width: `${Math.min(
                                      item.score_tfidf * 100,
                                      100
                                    )}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-[10px] font-mono text-swarna-primary font-bold">
                                {Math.round(item.score_tfidf * 100)}%
                              </span>
                            </div>
                          )}

                          {(activeAlgoTab === "all" ||
                            activeAlgoTab === "jaccard") && (
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-swarna-dark/50 w-10">
                                Jaccard
                              </span>
                              <div className="flex-grow h-1.5 bg-swarna-dark/10 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-swarna-accent rounded-full"
                                  style={{
                                    width: `${Math.min(
                                      item.score_jaccard * 100,
                                      100
                                    )}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-[10px] font-mono text-swarna-accent font-bold">
                                {Math.round(item.score_jaccard * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* --- POPUP MODAL EVALUASI (Warna Transparan & 8 Digit) --- */}
      {showEvalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in-up">
          <div className="bg-swarna-dark/95 backdrop-blur-xl border border-swarna-gold/30 w-full max-w-4xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Header Modal */}
            <div className="flex justify-between items-center p-6 border-b border-swarna-gold/20 bg-black/10">
              <div className="flex items-center gap-3">
                <Activity className="w-6 h-6 text-swarna-gold" />
                <h3 className="font-serif text-2xl font-bold text-swarna-light">
                  Evaluasi Pencarian
                </h3>
              </div>
              <button
                onClick={() => setShowEvalModal(false)}
                className="p-2 rounded-full hover:bg-white/10 text-swarna-light/50 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content Modal */}
            <div className="p-6 md:p-8 overflow-y-auto">
              {isEvalLoading ? (
                <div className="flex flex-col items-center justify-center py-12 text-swarna-light/60">
                  <div className="w-10 h-10 border-4 border-swarna-gold border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p>Menghitung metrik evaluasi...</p>
                </div>
              ) : evalData ? (
                <div className="space-y-8">
                  {/* Info Query */}
                  <div className="flex items-center justify-between text-sm text-swarna-light/70 bg-black/20 p-4 rounded-xl border border-swarna-gold/20">
                    <span>
                      Query:{" "}
                      <strong className="text-swarna-gold text-lg ml-2">
                        "{evalData.query}"
                      </strong>
                    </span>
                    {/* Relevant Docs Dihapus */}
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <EvalCard
                      title="TF-IDF"
                      data={evalData.tfidf}
                      runtime={evalData.runtime.tfidf}
                      color="border-swarna-primary"
                    />
                    <EvalCard
                      title="Jaccard"
                      data={evalData.jaccard}
                      runtime={evalData.runtime.jaccard}
                      color="border-swarna-accent"
                    />
                    <EvalCard
                      title="Kombinasi"
                      data={evalData.hybrid}
                      runtime={evalData.runtime.hybrid}
                      color="border-swarna-gold"
                      highlight
                    />
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-swarna-light/50">
                  Gagal memuat data evaluasi.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

// Komponen Kartu Evaluasi (8 Digit Desimal)
const EvalCard = ({
  title,
  data,
  runtime,
  color,
  highlight = false,
}: {
  title: string;
  data: EvalMetrics;
  runtime: number;
  color: string;
  highlight?: boolean;
}) => (
  <div
    className={`bg-white/5 rounded-2xl p-6 border-t-4 ${color} ${
      highlight ? "bg-white/10 ring-1 ring-swarna-gold/30" : ""
    } flex flex-col justify-between h-full`}
  >
    <div>
      <h4 className="font-serif text-xl font-bold text-swarna-light mb-6 text-center tracking-wide">
        {title}
      </h4>

      <div className="space-y-4 mb-6">
        <div className="flex justify-between items-center text-sm">
          <span className="text-swarna-light/60 font-medium">Precision</span>
          <span className="font-mono font-bold text-lg text-swarna-gold">
            {data.precision.toFixed(8)}
          </span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-swarna-light/60 font-medium">Recall</span>
          <span className="font-mono font-bold text-lg text-swarna-gold">
            {data.recall.toFixed(8)}
          </span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-swarna-light/60 font-medium">F1-Score</span>
          <span className="font-mono font-bold text-lg text-swarna-gold">
            {data.f1.toFixed(8)}
          </span>
        </div>
      </div>
    </div>

    <div className="pt-4 border-t border-white/10 flex items-center justify-center gap-2 text-xs text-swarna-light/50">
      <Timer className="w-4 h-4" />
      <span className="font-mono">{runtime.toFixed(4)} sec</span>
    </div>
  </div>
);

export default SearchSection;
