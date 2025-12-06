import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  MapPin,
  Music,
  Shirt,
  Feather,
  PlayCircle,
  BarChart3,
  Sparkles,
} from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

const DetailHasil: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const data = location.state;

  if (!data) {
    return (
      <div className="min-h-screen bg-swarna-primary flex items-center justify-center text-swarna-light">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4 font-serif">
            Data tidak ditemukan
          </h2>
          <button
            onClick={() => navigate("/")}
            className="px-6 py-2 bg-swarna-gold text-swarna-dark rounded-full font-bold hover:bg-white transition-all"
          >
            Kembali ke Beranda
          </button>
        </div>
      </div>
    );
  }

  const getCategoryIcon = (cat: string) => {
    switch (cat?.toLowerCase()) {
      case "alat_musik":
        return <Music className="w-4 h-4" />;
      case "pakaian":
        return <Shirt className="w-4 h-4" />;
      case "tarian":
        return <Feather className="w-4 h-4" />;
      default:
        return <Sparkles className="w-4 h-4" />;
    }
  };

  const formatCategory = (cat: string) => {
    return cat ? cat.replace(/_/g, " ").toUpperCase() : "";
  };

  return (
    <div className="min-h-screen bg-swarna-primary font-sans selection:bg-swarna-gold selection:text-swarna-dark flex flex-col">
      <Navbar />

      <main className="flex-grow pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-4xl animate-fade-in-up">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-swarna-light/70 hover:text-swarna-gold transition-colors mb-8 text-sm font-medium tracking-wide group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            KEMBALI KE PENCARIAN
          </button>

          <div className="text-center mb-10">
            <h1 className="font-serif text-4xl md:text-5xl font-bold text-swarna-light mb-6 leading-tight">
              {data.judul || data.title}
            </h1>

            <div className="flex flex-wrap justify-center gap-3">
              <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-gold text-xs font-bold tracking-wider uppercase">
                {getCategoryIcon(data.kategori || data.category)}
                <span>{formatCategory(data.kategori || data.category)}</span>
              </div>

              {data.asal_daerah && (
                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-light text-xs font-medium tracking-wide">
                  <MapPin className="w-3.5 h-3.5" />
                  <span>{data.asal_daerah}</span>
                </div>
              )}

              {(data.kategori === "alat_musik" ||
                data.category === "alat_musik") &&
                data.cara_main && (
                  <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-light text-xs font-medium tracking-wide">
                    <PlayCircle className="w-3.5 h-3.5" />
                    <span>{data.cara_main}</span>
                  </div>
                )}
            </div>
          </div>

          <div className="mb-12 flex justify-center">
            <img
              src={data.gambar || data.image}
              alt={data.judul || data.title}
              className="w-auto h-auto max-h-[500px] object-contain rounded-2xl drop-shadow-2xl"
            />
          </div>

          {/* Konten diperlebar ke max-w-4xl */}
          <div className="max-w-4xl mx-auto">
            <div className="mb-10">
              <h3 className="font-serif text-2xl text-swarna-gold mb-6 border-b border-swarna-light/10 pb-2 inline-block">
                Deskripsi Lengkap
              </h3>

              <div className="text-swarna-light/90 text-base md:text-lg leading-relaxed text-justify font-light whitespace-pre-line">
                {data.deskripsi || data.snippet}
              </div>
            </div>

            {data.score_tfidf !== undefined && (
              <div className="bg-black/20 p-6 rounded-2xl border border-white/5 mb-8">
                <h4 className="text-swarna-light/70 font-bold mb-4 flex items-center gap-2 text-sm uppercase tracking-widest">
                  <BarChart3 className="w-4 h-4" /> Relevansi Pencarian
                </h4>

                <div className="space-y-4">
                  <ScoreBar
                    label="TF-IDF"
                    score={data.score_tfidf}
                    color="bg-swarna-primary"
                  />
                  <ScoreBar
                    label="Jaccard"
                    score={data.score_jaccard}
                    color="bg-swarna-accent"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

// Komponen ScoreBar yang telah diperlebar
const ScoreBar = ({
  label,
  score,
  color,
}: {
  label: string;
  score: number;
  color: string;
}) => (
  <div className="flex items-center gap-6 w-full">
    <span className="text-xs font-bold text-swarna-light/50 w-20">{label}</span>

    <div className="flex-grow h-3 bg-white/10 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} rounded-full`}
        style={{ width: `${score * 100}%` }}
      ></div>
    </div>

    <span className="text-xs font-mono text-swarna-light font-bold w-24 text-right">
      {score.toFixed(6)}
    </span>
  </div>
);

export default DetailHasil;
