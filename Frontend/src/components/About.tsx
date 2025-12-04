import React, { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";

// --- DATA DUMMY ---
const culturalHighlights = [
  {
    id: 1,
    title: "Tari Saman",
    desc: "Harmoni seribu tangan dari dataran tinggi Gayo.",
    image: "/tari-saman.jpg",
  },
  {
    id: 2,
    title: "Angklung",
    desc: "Alunan bambu warisan dunia.",
    image: "/angklung.jpg",
  },
  {
    id: 3,
    title: "Kain Ulos",
    desc: "Simbol kehangatan tanah Batak.",
    image: "/ulos.jpg",
  },
];

const teamMembers = [
  {
    id: 1,
    name: "Khalisha Adzraini Arif",
    role: "UI/UX & Web Development",
    image: "/team1.png",
  },
  {
    id: 2,
    name: "Firah Maulida",
    role: "Data Collection & Documentation",
    image: "/team2.png",
  },
  {
    id: 3,
    name: "Nurul Izzati",
    role: "Data Processing & API Development",
    image: "/team3.png",
  },
];

const About: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [memberIndex, setMemberIndex] = useState(0);
  const [isDoorOpen, setIsDoorOpen] = useState(false);

  // Auto-slide Carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % culturalHighlights.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Animasi Pintu
  useEffect(() => {
    const sequence = () => {
      setTimeout(() => setIsDoorOpen(true), 500); // Buka
      setTimeout(() => setIsDoorOpen(false), 4500); // Tutup
      setTimeout(() => {
        setMemberIndex((prev) => (prev + 1) % teamMembers.length); // Ganti Orang
      }, 5500);
    };
    sequence();
    const loop = setInterval(sequence, 6000);
    return () => clearInterval(loop);
  }, []);

  const nextSlide = () =>
    setCurrentSlide((p) => (p + 1) % culturalHighlights.length);
  const prevSlide = () =>
    setCurrentSlide(
      (p) => (p - 1 + culturalHighlights.length) % culturalHighlights.length
    );

  return (
    <section
      id="about"
      className="min-h-screen bg-swarna-primary relative overflow-hidden flex items-start pt-32 pb-20"
    >
      {/* Background Batik */}
      <div
        className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-80 animate-move-batik"
        style={{
          backgroundImage: "url('/batik-awan.png')",
          backgroundSize: "600px",
          backgroundRepeat: "repeat",
        }}
      ></div>

      <div className="container mx-auto px-6 md:px-12 max-w-7xl relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* === KIRI: TEXT & CARD SWIPE === */}
          <div className="flex flex-col gap-8 animate-fade-in-up">
            <div className="text-left">
              <div className="inline-flex items-center gap-2 mb-3 px-3 py-1 rounded-full bg-swarna-light/10 border border-swarna-light/20 text-swarna-gold text-[10px] font-medium tracking-wider uppercase">
                <Sparkles className="w-3 h-3" />
                <span>Tentang Kami</span>
              </div>
              <h2 className="font-serif text-3xl md:text-4xl font-bold text-swarna-light mb-3 leading-tight">
                Mengenal{" "}
                <span className="text-swarna-gold italic">SwarnaNusa</span>
              </h2>
              <p className="text-swarna-light/80 text-sm text-justify font-light leading-relaxed max-w-md">
                SwarnaNusa hadir sebagai jembatan antara warisan leluhur dan
                teknologi masa depan. Melalui implementasi algoritma pencarian
                cerdas, kami merangkai kepingan informasi mengenai tarian, alat
                musik, dan pakaian adat Nusantara. Ini bukan sekadar mesin
                pencari, melainkan sebuah upaya digital untuk menjaga identitas
                bangsa agar tak lekang oleh waktu dan tetap relevan bagi
                generasi mendatang.
              </p>
            </div>

            {/* CARD SWIPE STYLE */}
            <div className="relative w-full max-w-md h-[280px] perspective-1000">
              {culturalHighlights.map((item, idx) => {
                const isCurrent = idx === currentSlide;
                const isNext =
                  idx === (currentSlide + 1) % culturalHighlights.length;
                const isPrev =
                  idx ===
                  (currentSlide - 1 + culturalHighlights.length) %
                    culturalHighlights.length;

                let styleClass = "opacity-0 scale-90 z-0 hidden";

                if (isCurrent) {
                  styleClass =
                    "opacity-100 scale-100 z-20 rotate-0 translate-x-0 shadow-2xl";
                } else if (isNext) {
                  styleClass =
                    "opacity-60 scale-95 z-10 rotate-3 translate-x-4 translate-y-2";
                } else if (isPrev) {
                  styleClass =
                    "opacity-0 scale-90 z-0 -rotate-6 -translate-x-12";
                }

                return (
                  <div
                    key={item.id}
                    className={`absolute inset-0 w-full h-full rounded-2xl overflow-hidden transition-all duration-700 ease-out bg-swarna-dark border border-white/10 ${styleClass}`}
                  >
                    <img
                      src={item.image}
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent"></div>
                    <div className="absolute bottom-0 left-0 p-6 w-full">
                      <h4 className="text-swarna-gold font-serif text-2xl font-bold mb-1">
                        {item.title}
                      </h4>
                      <p className="text-swarna-light/80 text-xs font-light leading-relaxed">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                );
              })}

              {/* <div className="absolute -bottom-16 right-0 flex gap-3 z-30">
                <button
                  onClick={prevSlide}
                  className="group p-3 rounded-full border border-swarna-light/20 text-swarna-light hover:bg-swarna-gold hover:text-swarna-primary transition-all"
                >
                  <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
                </button>
                <button
                  onClick={nextSlide}
                  className="group p-3 rounded-full border border-swarna-light/20 text-swarna-light hover:bg-swarna-gold hover:text-swarna-primary transition-all"
                >
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div> */}
            </div>
          </div>

          {/* === KANAN: PINTU ACEH === */}
          <div className="relative flex justify-center items-end h-[420px] mt-20 lg:mt-20">
            <div className="relative w-[400px] h-full flex items-end justify-center overflow-visible">
              {/* LORONG GELAP */}
              <div className="absolute inset-x-10 bottom-10 top-2 bg-gradient-to-t from-black via-[#2C1E16] to-transparent rounded-t-[200px] opacity-50 blur-md z-0"></div>

              {/* --- ORANG --- */}
              {teamMembers.map((member, idx) => (
                <div
                  key={member.id}
                  className={`absolute bottom-20 w-[300px] transition-all duration-700 flex flex-col items-center z-10 ${
                    idx === memberIndex
                      ? "opacity-100 scale-100"
                      : "opacity-0 scale-95"
                  }`}
                >
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-full h-auto drop-shadow-2xl"
                  />

                  <div
                    className={`absolute bottom-0 bg-swarna-dark/80 backdrop-blur-md border border-swarna-gold/30 px-5 py-4 rounded-full text-center shadow-4xl transform transition-all duration-1000 ${
                      isDoorOpen
                        ? "translate-y-0 opacity-100"
                        : "translate-y-8 opacity-0"
                    }`}
                  >
                    <h4 className="font-bold text-swarna-gold text-md leading-none mb-0.5">
                      {member.name}
                    </h4>
                    <span className="text-[10px] text-swarna-light/70 uppercase tracking-widest">
                      {member.role}
                    </span>
                  </div>
                </div>
              ))}

              {/* --- PINTU KIRI --- */}
              {/* w-[51%] : Biar pas tutup dia rapat (overlap 1% aja di tengah) */}
              {/* translate-x-[90%] : Biar bukanya LEBAR banget hampir hilang */}
              <img
                src="/pintu-kiri.png"
                alt="Pintu Kiri"
                className={`absolute left-0 bottom-0 h-full w-[56%] z-30 transition-transform duration-[1500ms] ease-in-out origin-left ${
                  isDoorOpen
                    ? "-translate-x-[78%] rotate-y-12"
                    : "translate-x-0"
                }`}
                style={{ filter: "drop-shadow(10px 0 20px rgba(0,0,0,0.8))" }}
              />

              {/* --- PINTU KANAN --- */}
              <img
                src="/pintu-kanan.png"
                alt="Pintu Kanan"
                className={`absolute right-0 bottom-0 h-full w-[56%] z-30 transition-transform duration-[1500ms] ease-in-out origin-right ${
                  isDoorOpen
                    ? "translate-x-[70%] -rotate-y-12"
                    : "translate-x-0"
                }`}
                style={{ filter: "drop-shadow(-10px 0 20px rgba(0,0,0,0.8))" }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
