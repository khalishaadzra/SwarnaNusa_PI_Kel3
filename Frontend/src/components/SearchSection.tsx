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
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { SearchResult } from "../types";
import { mockDatabase } from "../data/mockData";

const algoTabs = [
  { id: "all", label: "Kombinasi", icon: Layers },
  { id: "tfidf", label: "TF-IDF", icon: BarChart3 },
  { id: "jaccard", label: "Jaccard", icon: Calculator },
];

const ITEMS_PER_PAGE = 4;

const SearchSection: React.FC = () => {
  const navigate = useNavigate();

  // --- LOGIKA RESTORE DATA ---
  const shouldRestore = sessionStorage.getItem("restore_search") === "true";

  // --- STATE ---
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

  // --- HANDLE SEARCH ---
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setIsSearching(true);
    setHasSearched(true); // Langsung set true biar animasi naik mulai jalan
    setPageIndex(0);

    try {
      let algo = activeAlgoTab;
      if (algo === "all") algo = "combined";

      const response = await fetch(
        `http://127.0.0.1:8000/search?q=${encodeURIComponent(
          query
        )}&mode=${algo}`
      );

      if (!response.ok) throw new Error("API Error");

      const data = await response.json();

      const mappedResults = data.results.map((item: any) => ({
        id: item.document.no || Math.random().toString(),
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
    } catch (error) {
      console.error("Error:", error);
      // Fallback Dummy
      const allMatches = mockDatabase.filter(
        (item) =>
          (item.judul || item.title || "")
            .toLowerCase()
            .includes(query.toLowerCase()) ||
          (item.deskripsi || item.snippet || "")
            .toLowerCase()
            .includes(query.toLowerCase())
      );
      setResults(allMatches);
    } finally {
      setIsSearching(false);
    }
  };

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

      {/* 
          INI BAGIAN UTAMA YANG DIUBAH 
          Logic: Jika belum search (hasSearched false) -> pt-[35vh] (Tengah)
                 Jika sudah search (hasSearched true) -> pt-24 (Atas)
      */}
      <div
        className={`
          container mx-auto px-6 max-w-7xl relative z-10 flex flex-col 
          transition-all duration-1000 ease-in-out
          ${hasSearched ? "pt-24" : "pt-[35vh]"}
        `}
      >
        <div
          className={`text-center transition-all duration-700 ${
            hasSearched ? "mb-6" : "mb-8"
          }`}
        >
          <div className="inline-flex items-center gap-2 mt-5 mb-3 px-4 py-1.5 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-gold text-xs font-medium animate-fade-in-up">
            <Sparkles className="w-3 h-3" />
            <span>Mesin Pencari Budaya</span>
          </div>
          <h2
            className="font-serif text-5xl md:text-6xl font-bold text-swarna-light mb-4 drop-shadow-md animate-fade-in-up"
            style={{ animationDelay: "0.1s" }}
          >
            Telusuri Jejak Budaya
          </h2>
          <p
            className="text-swarna-light/80 text-base md:text-lg max-w-2xl mx-auto animate-fade-in-up"
            style={{ animationDelay: "0.2s" }}
          >
            Temukan makna di balik setiap gerak, nada, dan corak Nusantara.
          </p>
        </div>

        <div
          className={`bg-swarna-light/10 backdrop-blur-md border border-swarna-light/30 p-1.5 rounded-[1.5rem] shadow-xl transition-all duration-500 mx-auto w-full ${
            hasSearched ? "max-w-2xl" : "max-w-3xl scale-110" // Sedikit lebih besar pas di tengah
          }`}
        >
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-grow group">
              <div className="absolute left-5 top-1/2 -translate-y-1/2 text-swarna-dark/50 group-focus-within:text-swarna-primary transition-colors">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="Cari budaya... (misal: Adok, Bedaya, Batik)"
                className="w-full pl-12 pr-4 h-12 rounded-[1.2rem] bg-swarna-light text-swarna-dark text-base font-medium shadow-inner focus:outline-none focus:ring-4 focus:ring-swarna-gold/30 transition-all placeholder:text-swarna-dark/40"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="h-12 px-8 bg-swarna-gold hover:bg-white hover:text-swarna-primary text-swarna-dark rounded-[1.2rem] font-bold text-base transition-all shadow-lg hover:shadow-swarna-gold/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSearching ? "..." : "Cari"}
            </button>
          </form>
        </div>

        {/* LOADING & HASIL PENCARIAN AKAN MUNCUL DI BAWAHNYA SETELAH NAIK */}

        {isSearching && (
          <div className="mt-12 text-center animate-fade-in-up">
            <div className="inline-block w-8 h-8 border-4 border-swarna-gold border-t-transparent rounded-full animate-spin"></div>
            <p className="text-swarna-light/70 mt-2 text-sm animate-pulse">
              Sedang menelusuri korpus...
            </p>
          </div>
        )}

        {hasSearched && !isSearching && (
          <div className="mt-10 animate-fade-in-up pb-20">
            {/* Tabs Algoritma */}
            <div className="flex justify-center mb-8">
              <div className="inline-flex bg-black/20 backdrop-blur-sm p-1 rounded-full border border-white/10 shadow-inner">
                {algoTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveAlgoTab(tab.id)}
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
    </section>
  );
};

export default SearchSection;
