// src/components/SearchSection.tsx
import React, { useState } from "react";
import { Search, Sparkles, Layers, Calculator, BarChart3 } from "lucide-react";
import type { SearchResult } from "../types";
import { mockDatabase } from "../data/mockData";

const algoTabs = [
  { id: "all", label: "Semua", icon: Layers },
  { id: "tfidf", label: "TF-IDF", icon: BarChart3 },
  { id: "jaccard", label: "Jaccard", icon: Calculator },
];

const SearchSection: React.FC = () => {
  const [query, setQuery] = useState<string>("");
  const [activeAlgoTab, setActiveAlgoTab] = useState<string>("all");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setIsSearching(true);
    setHasSearched(false);

    setTimeout(() => {
      const allMatches = mockDatabase.filter(
        (item) =>
          item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.snippet.toLowerCase().includes(query.toLowerCase())
      );

      setResults(allMatches);
      setHasSearched(true);
      setIsSearching(false);
      setActiveAlgoTab("all");
    }, 800);
  };

  return (
    <section
      id="search"
      className="min-h-screen bg-swarna-primary relative overflow-hidden flex flex-col"
    >
      {/* --- BACKGROUND PATTERN --- */}
      <div
        className="absolute inset-0 pointer-events-none mix-blend-overlay animate-move-batik"
        style={{
          backgroundImage: "url('/batik-awan.png')",
          backgroundSize: "600px",
          backgroundRepeat: "repeat",
        }}
      ></div>

      {/* --- KONTEN UTAMA --- */}
      <div className="container mx-auto px-6 max-w-6xl relative z-10 flex-grow pt-28">
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

        {/* --- SEARCH BOX AREA --- */}
        <div
          className={`bg-swarna-light/10 backdrop-blur-md border border-swarna-light/30 p-1.5 rounded-[1.5rem] shadow-xl transition-all duration-500 mx-auto ${
            hasSearched ? "max-w-2xl" : "max-w-2xl"
          }`}
        >
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-grow group">
              <div className="absolute left-5 top-1/2 -translate-y-1/2 text-swarna-dark/50 group-focus-within:text-swarna-primary transition-colors">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="Cari budaya... (misal: Tari Kecak, Batik)"
                className="w-full pl-12 pr-4 h-8 md:h-10 rounded-[1.2rem] bg-swarna-light text-swarna-dark text-base font-medium shadow-inner focus:outline-none focus:ring-4 focus:ring-swarna-gold/30 transition-all placeholder:text-swarna-dark/40"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={isSearching}
              className="h-12 md:h-10 px-6 md:px-8 bg-swarna-gold hover:bg-white hover:text-swarna-primary text-swarna-dark rounded-[1.2rem] font-bold text-base transition-all shadow-lg hover:shadow-swarna-gold/50 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSearching ? "..." : "Cari"}
            </button>
          </form>
        </div>

        {/* --- LOADING INDICATOR --- */}
        {isSearching && (
          <div className="mt-12 text-center">
            <div className="inline-block w-8 h-8 border-4 border-swarna-gold border-t-transparent rounded-full animate-spin"></div>
            <p className="text-swarna-light/70 mt-2 text-sm animate-pulse">
              Sedang menelusuri korpus...
            </p>
          </div>
        )}

        {/* --- HASIL PENCARIAN & TABS --- */}
        {hasSearched && !isSearching && (
          <div className="mt-10 animate-fade-in-up pb-20">
            {/* TABS ALGORITMA */}
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

            {/* INFO HASIL */}
            {results.length === 0 ? (
              <div className="text-center py-8 bg-black/10 rounded-2xl border border-white/5">
                <p className="text-swarna-light/60 text-base">
                  Tidak ada hasil ditemukan.
                </p>
              </div>
            ) : (
              <>
                <p className="text-swarna-light/60 text-center mb-6 text-sm">
                  Menampilkan{" "}
                  <span className="text-swarna-gold font-bold">
                    {results.length}
                  </span>{" "}
                  hasil
                </p>

                {/* GRID HASIL */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.map((item, index) => (
                    <div
                      key={item.id}
                      className="bg-swarna-light rounded-2xl overflow-hidden shadow-lg hover:shadow-xl hover:shadow-swarna-gold/20 transition-all duration-500 hover:-translate-y-1 group flex flex-col h-full border border-swarna-light/50"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="aspect-video w-full overflow-hidden relative bg-gray-100">
                        <img
                          src={item.image}
                          alt={item.title}
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                        />
                        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur px-2 py-0.5 rounded-full text-[10px] font-bold text-swarna-primary uppercase tracking-wider shadow-sm">
                          {item.category.replace("_", " ")}
                        </div>
                      </div>

                      {/* Content Area */}
                      <div className="p-5 flex flex-col flex-grow">
                        <h3 className="font-serif text-xl font-bold text-swarna-dark mb-2 group-hover:text-swarna-primary transition-colors">
                          {item.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-4 line-clamp-3 leading-relaxed flex-grow">
                          {item.snippet}
                        </p>

                        {/* Score Visualization */}
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
                                    width: `${item.score_tfidf * 100}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-[10px] font-mono text-swarna-primary font-bold">
                                {item.score_tfidf}
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
                                    width: `${item.score_jaccard * 100}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-[10px] font-mono text-swarna-accent font-bold">
                                {item.score_jaccard}
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
