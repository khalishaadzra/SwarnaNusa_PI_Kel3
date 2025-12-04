// src/components/Hero.tsx
import React from "react";

const Hero: React.FC = () => {
  return (
    <header id="hero" className="relative w-full h-screen bg-swarna-primary overflow-hidden flex flex-col items-center justify-center">
      {/* === LAYER 1: BACKGROUND ANIMASI AWAN */}
      <div className="absolute top-0 left-0 w-[200%] h-full z-0 flex animate-moving-clouds pointer-events-none">
        <img
          src="/awan1.png"
          alt="Awan Latar 1"
          className="w-1/3 h-full object-cover object-bottom opacity-50"
        />
        <img
          src="/awan2.png"
          alt="Awan Latar 2"
          className="w-1/3 h-full object-cover object-bottom opacity-50"
        />
        <img
          src="/awan3.png"
          alt="Awan Latar 2"
          className="w-1/3 h-full object-cover object-bottom opacity-50"
        />
      </div>

      <div className="absolute inset-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-20 left-10 w-2 h-2 bg-swarna-gold/40 rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-20 w-3 h-3 bg-swarna-light/20 rounded-full animate-float delay-700"></div>
        <div className="absolute top-10 left-1/2 w-1.5 h-1.5 bg-swarna-gold/30 rounded-full animate-float delay-500"></div>
      </div>

      {/* === LAYER 2 === */}
      <div className="relative z-20 text-center px-4 -mt-20 md:-mt-32">
        <h1 className="font-serif text-6xl md:text-8xl lg:text-8xl font-bold text-swarna-light drop-shadow-lg mb-4 opacity-0 animate-fade-in-up tracking-tight">
          Swarna Nusa
        </h1>

        {/* Garis Emas */}
        <div
          className="w-24 h-1 bg-swarna-gold mx-auto mb-6 rounded-full opacity-0 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        ></div>

        <p
          className="font-sans text-lg md:text-xl text-swarna-light/90 font-light tracking-widest opacity-0 animate-fade-in-up"
          style={{ animationDelay: "0.4s" }}
        >
          Menjaga Gerak, Nada, dan Warna Budaya Indonesia
        </p>
      </div>

      {/* Tombol Scroll Indicator */}
      <div
        className="absolute bottom-1/3 z-20 flex flex-col items-center opacity-0 animate-fade-in-up"
        style={{ animationDelay: "0.8s" }}
      >
        <span className="text-swarna-light/60 text-xs tracking-widest mb-2 uppercase">
          Mulai Menelusuri
        </span>
        <a
          href="#search"
          className="w-8 h-9 border-2 border-swarna-light/30 rounded-full flex justify-center p-3 hover:border-swarna-gold transition-colors cursor-pointer"
        >
          <div className="w-1 h-2 bg-swarna-gold rounded-full animate-bounce"></div>
        </a>
      </div>

      {/* === LAYER 3: GAMBAR ORANG === */}
      <div className="absolute bottom-0 left-0 w-full z-10 pointer-events-none">
        <div className="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-swarna-primary to-transparent z-20"></div>

        <img
          src="/bg-budaya.png"
          alt="Ilustrasi Budaya Nusantara"
          className="w-full h-auto object-cover object-bottom md:max-h-[60vh] lg:max-h-[100vh] align-bottom"
        />
      </div>
    </header>
  );
};

export default Hero;
