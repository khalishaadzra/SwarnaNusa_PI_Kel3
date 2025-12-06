// src/components/Footer.tsx
import React from "react";
import { Facebook, Instagram, Twitter } from "lucide-react";

const Footer: React.FC = () => {
  return (
    // Gunakan warna custom yang sangat gelap agar mirip gambar (#2C1E16)
    <footer className="bg-[#2C1E16] text-[#FFFCF9] pt-16 pb-8 border-t border-[#AD6042]/30">
      <div className="container mx-auto px-6 md:px-12">
        {/* --- GRID 3 KOLOM --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12">
          {/* KOLOM 1: LOGO & SOCIALS (Rata Tengah) */}
          <div className="flex flex-col items-center text-center">
            {/* Logo Image */}
            <div className="w-16 h-16 mb-3">
              <img
                src="/logo.png"
                alt="SwarnaNusa Logo"
                className="w-full h-full object-contain brightness-0 invert" // brightness-0 invert membuat logo jadi putih polos (opsional)
                onError={(e) =>
                  ((e.target as HTMLImageElement).style.display = "none")
                }
              />
            </div>

            <h3 className="font-serif text-lg font-bold tracking-wider mb-2">
              SwarnaNusa
            </h3>
            <p className="text-xs text-gray-400 max-w-[200px] mb-6 leading-relaxed">
              Menjaga Gerak, Nada, dan Warna Budaya Indonesia
            </p>

            {/* Social Icons */}
            <div className="flex gap-4">
              <SocialIcon icon={Facebook} />
              <SocialIcon icon={Instagram} />
              <SocialIcon icon={Twitter} />
            </div>
          </div>

          {/* KOLOM 2: SUPPORT (Rata Kiri) */}
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <h3 className="font-serif text-lg font-bold mb-6 text-[#DFAD54]">
              Kontak Kami
            </h3>
            <div className="space-y-3 text-sm text-gray-300 font-light tracking-wide">
              <p>
                Darussalam, Kec. Syiah Kuala,
                <br />
                Kota Banda Aceh, Aceh 23111
              </p>
              <p className="hover:text-[#DFAD54] transition-colors cursor-pointer">
                SwarnaNusa@gmail.com
              </p>
              <p>+ 62 811 6708 2711</p>
            </div>
          </div>

          {/* KOLOM 3: KATEGORI (Rata Kiri) */}
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <h3 className="font-serif text-lg font-bold mb-6 text-[#DFAD54]">
              Kategori
            </h3>
            <ul className="space-y-3 text-sm text-gray-300 font-light tracking-wide">
              <li>
                <a
                  href="#search"
                  className="hover:text-[#DFAD54] transition-colors"
                >
                  Tarian Tradisional
                </a>
              </li>
              <li>
                <a
                  href="#search"
                  className="hover:text-[#DFAD54] transition-colors"
                >
                  Alat Musik Tradisional
                </a>
              </li>
              <li>
                <a
                  href="#search"
                  className="hover:text-[#DFAD54] transition-colors"
                >
                  Pakaian Tradisional
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* --- COPYRIGHT --- */}
        <div className="border-t border-gray-700/50 pt-8 text-center">
          <p className="text-[10px] md:text-xs text-gray-500 tracking-wider">
            &copy; 2025 SwarnaNusa. Seluruh hak dilindungi.
          </p>
        </div>
      </div>
    </footer>
  );
};

// Komponen Kecil untuk Icon Bulat
const SocialIcon = ({ icon: Icon }: { icon: any }) => (
  <a
    href="#"
    className="w-8 h-8 rounded-full border border-gray-500 flex items-center justify-center text-gray-400 hover:bg-[#DFAD54] hover:border-[#DFAD54] hover:text-[#2C1E16] transition-all duration-300"
  >
    <Icon className="w-4 h-4" />
  </a>
);

export default Footer;
