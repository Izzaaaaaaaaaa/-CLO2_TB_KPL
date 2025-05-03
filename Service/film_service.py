# ======================================
# AutoTicket CLI Project
# ======================================
# File: film_service.py

import requests
from typing import Dict, List, Optional, Any
from Config.Config_manager import ConfigManager


class FilmService:
    """
    Kelas untuk mengelola data film dan jadwal.
    Mengimplementasikan Code Reuse dengan memanfaatkan ConfigManager.
    """

    def _init_(self, config_manager: ConfigManager):
        """
        Inisialisasi FilmService dengan ConfigManager

        Args:
            config_manager: Instance dari ConfigManager yang telah dimuat
        """
        self.config_manager = config_manager
        self.films = []
        self.load_film_data()

    def load_film_data(self) -> None:
        """
        Memuat data film dari konfigurasi
        """
        self.films = self.config_manager.config.get("film", [])

    def get_all_films(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar semua film yang tersedia

        Returns:
            List berisi informasi semua film
        """
        film_list = []
        for film in self.films:
            film_list.append({
                "judul": film.get("judul", ""),
                "genre": film.get("genre", ""),
                "durasi": film.get("durasi", 0),
                "sinopsis": film.get("sinopsis", ""),
                "teater": film.get("teater", "")
            })
        return film_list

    def get_film_info(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan informasi detail tentang film berdasarkan judul

        Args:
            title: Judul film yang dicari

        Returns:
            Dictionary berisi informasi film, atau None jika tidak ditemukan
        """
        for film in self.films:
            if film.get("judul", "").lower() == title.lower():
                return {
                    "judul": film.get("judul", ""),
                    "genre": film.get("genre", ""),
                    "durasi": film.get("durasi", 0),
                    "sinopsis": film.get("sinopsis", ""),
                    "teater": film.get("teater", ""),
                    "harga_tiket": film.get("harga_tiket", 0),
                    "jadwal": film.get("jadwal", [])
                }
        return None

    def get_film_showtimes(self, title: str) -> List[str]:
        """
        Mendapatkan jadwal tayang untuk film tertentu

        Args:
            title: Judul film

        Returns:
            List berisi jadwal tayang film
        """
        film_info = self.get_film_info(title)
        if film_info:
            return film_info.get("jadwal", [])
        return []

    def get_film_teater(self, title: str) -> Optional[str]:
        """
        Mendapatkan teater untuk film tertentu

        Args:
            title: Judul film

        Returns:
            Nama teater, atau None jika film tidak ditemukan
        """
        film_info = self.get_film_info(title)
        if film_info:
            return film_info.get("teater", "")
        return None

    def get_film_price(self, title: str) -> int:
        """
        Mendapatkan harga dasar tiket untuk film tertentu

        Args:
            title: Judul film

        Returns:
            Harga dasar tiket film
        """
        film_info = self.get_film_info(title)
        if film_info:
            return film_info.get("harga_tiket", 0)
        return 0


# Contoh penggunaan mandiri
if _name_ == '_main_':
    config = ConfigManager()
    config.load_config()
    film_service = FilmService(config)

    # Mendapatkan semua film
    all_films = film_service.get_all_films()
    print("Daftar Film:")
    for film in all_films:
        print(f"- {film['judul']} ({film['genre']}, {film['durasi']} menit)")

    # Mendapatkan info film tertentu
    film_info = film_service.get_film_info("Avengers: Endgame")
    if film_info:
        print(f"\nDetail Film: {film_info['judul']}")
        print(f"Genre: {film_info['genre']}")
        print(f"Durasi: {film_info['durasi']} menit")
        print(f"Sinopsis: {film_info['sinopsis']}")
        print(f"Teater: {film_info['teater']}")
        print(f"Harga: Rp {film_info['harga_tiket']}")
        print(f"Jadwal: {', '.join(film_info['jadwal'])}")