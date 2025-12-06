import React, { useState, useEffect } from "react";
import { Home, Search, Info } from "lucide-react"; // Import icon biar makin manis

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {

      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-6 px-4">
      <nav
        className={`
          flex items-center justify-between px-6 py-3 rounded-full border 
          transition-all duration-500 ease-in-out
          ${
            isScrolled
              ? "bg-swarna-dark/40 border-swarna-gold/30 shadow-2xl backdrop-blur-xl w-[90%] md:w-[70%] lg:w-[50%]"
              : "bg-swarna-dark/30 border-white/10 backdrop-blur-sm w-[95%] md:w-[80%] lg:w-[60%]"
          }
        `}
      >
        {/* --- LOGO AREA --- */}
        <a
          href="#hero"
          className="flex items-center gap-2 group cursor-pointer"
        >
          <div className="w-10 h-8 bg-white/10 rounded-full flex items-center justify-center border border-white/10 group-hover:bg-swarna-gold group-hover:border-swarna-gold transition-all duration-300">
            {/* Logo Image */}
            <img
              src="/logo.png"
              alt="Logo"
              className="h-6 w-auto object-contain brightness-0 invert group-hover:brightness-100 group-hover:invert-0 transition-all"
              onError={(e) =>
                ((e.target as HTMLImageElement).style.display = "none")
              }
            />
          </div>
          <span className="font-serif text-lg font-bold text-swarna-light tracking-wide group-hover:text-swarna-gold transition-colors hidden sm:block">
            SwarnaNusa
          </span>
        </a>

        {/* --- MENU LINKS --- */}
        <div className="flex items-center gap-1 sm:gap-6">
          <NavLink href="#hero" label="Beranda" icon={Home} />
          <NavLink href="#search" label="Cari" icon={Search} />
          <NavLink href="#about" label="Tentang" icon={Info} />
        </div>
      </nav>
    </div>
  );
};

// Komponen Kecil untuk Link agar kodenya rapi
const NavLink = ({
  href,
  label,
  icon: Icon,
}: {
  href: string;
  label: string;
  icon: any;
}) => (
  <a
    href={href}
    className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium text-swarna-light/80 hover:text-swarna-dark hover:bg-swarna-gold transition-all duration-300 group"
  >
    <Icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
    <span className="hidden md:block">{label}</span>
  </a>
);

export default Navbar;
