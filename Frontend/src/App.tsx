import React from "react";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import SearchSection from "./components/SearchSection";
import About from "./components/About"; 
import Footer from "./components/Footer";

const App: React.FC = () => {
  return (
    <div className="bg-swarna-light font-sans selection:bg-swarna-gold selection:text-swarna-dark scroll-smooth">
      <Navbar />
      <Hero />
      <SearchSection />
      <About /> 
      <Footer />
    </div>
  );
};

export default App;
