// src/App.tsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import SearchSection from "./components/SearchSection";
import About from "./components/About";
import Footer from "./components/Footer";
import DetailHasil from "./components/DetailHasil"; 

// Kita buat komponen LandingPage di sini aja (atau file terpisah)
// Isinya adalah halaman utama yang lama
const LandingPage = () => (
  <>
    <Navbar />
    <Hero />
    <SearchSection />
    <About />
    <Footer />
  </>
);

const App: React.FC = () => {
  return (
    <Router>
      <div className="bg-swarna-light font-sans selection:bg-swarna-gold selection:text-swarna-dark scroll-smooth">
        <Routes>
          {/* Rute Utama (Halaman Depan) */}
          <Route path="/" element={<LandingPage />} />

          {/* Rute Detail (Halaman Baru) */}
          <Route path="/detail/:id" element={<DetailHasil />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
