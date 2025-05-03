import requests
from typing import Dict, List, Optional, Any
from Config.Config_manager import ConfigManager


class FilmService:
    """
    Kelas untuk mengelola data film dan jadwal.
    Mengimplementasikan Code Reuse dengan memanfaatkan ConfigManager.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Inisialisasi FilmService dengan ConfigManager

        Args:
            config_manager: Instance dari ConfigManager yang telah dimuat
        """
        self.config_manager = config_manager
        self.films = []
        self.load_film_data()

    def load_film_data(self) -> List[Dict[str, Any]]:
        """
        Memuat data film dari konfigurasi.
        Menggunakan Code Reuse dengan memanfaatkan ConfigManager.

        Returns:
            List data film yang telah dimuat
        """
        # Menggunakan config_manager untuk mendapatkan data film
        self.films = self.config_manager.config.get("film", [])
        return self.films

    def get_film_info(self, film_title: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan informasi lengkap tentang film berdasarkan judul.

        Args:
            film_title: Judul film yang ingin dicari

        Returns:
            Dictionary berisi informasi film, atau None jika tidak ditemukan
        """
        # Mencari film berdasarkan judul
        for film in self.films:
            if film.get("judul", "").lower() == film_title.lower():
                return film
        return None

    def get_film_schedule(self, film_title: str) -> List[str]:
        """
        Mendapatkan jadwal tayang untuk film tertentu.

        Args:
            film_title: Judul film yang ingin dicari jadwalnya

        Returns:
            List jadwal tayang film, atau list kosong jika film tidak ditemukan
        """
        film_info = self.get_film_info(film_title)
        if film_info:
            return film_info.get("jadwal", [])
        return []

    def get_all_films(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar semua film yang tersedia.

        Returns:
            List semua data film
        """
        return self.films

    def get_film_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar film berdasarkan genre.

        Args:
            genre: Genre film yang ingin dicari

        Returns:
            List film yang memiliki genre yang dicari
        """
        result = []
        for film in self.films:
            film_genres = film.get("genre", "").lower()
            if genre.lower() in film_genres:
                result.append(film)
        return result

    def get_film_price(self, film_title: str) -> int:
        """
        Mendapatkan harga tiket untuk film tertentu.

        Args:
            film_title: Judul film

        Returns:
            Harga tiket film, atau 0 jika film tidak ditemukan
        """
        film_info = self.get_film_info(film_title)
        if film_info:
            return film_info.get("harga_tiket", 0)
        return 0

    def get_film_teater(self, film_title: str) -> str:
        """
        Mendapatkan teater untuk film tertentu.

        Args:
            film_title: Judul film

        Returns:
            Nama teater, atau string kosong jika film tidak ditemukan
        """
        film_info = self.get_film_info(film_title)
        if film_info:
            return film_info.get("teater", "")
        return ""

    def get_films_by_teater(self, teater_name: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar film yang diputar di teater tertentu.

        Args:
            teater_name: Nama teater

        Returns:
            List film yang diputar di teater tersebut
        """
        result = []
        for film in self.films:
            if film.get("teater", "") == teater_name:
                result.append(film)
        return result

    def is_film_available_at_time(self, film_title: str, time: str) -> bool:
        """
        Mengecek apakah film tersedia pada waktu tertentu.

        Args:
            film_title: Judul film
            time: Waktu yang ingin dicek (format: "HH:MM")

        Returns:
            True jika film tersedia pada waktu tersebut, False jika tidak
        """
        schedule = self.get_film_schedule(film_title)
        return time in schedule


# Contoh penggunaan mandiri
if __name__ == '__main__':
    config = ConfigManager()
    config.load_config()
    film_service = FilmService(config)

    # Menampilkan semua film
    print("Daftar Film:")
    for film in film_service.get_all_films():
        print(f"- {film.get('judul')}")

    # Mencari informasi film tertentu
    film_title = "Avengers: Endgame"
    film_info = film_service.get_film_info(film_title)
    if film_info:
        print(f"\nInformasi Film {film_title}:")
        print(f"Genre: {film_info.get('genre')}")
        print(f"Durasi: {film_info.get('durasi')}")
        print(f"Rating: {film_info.get('rating')}")
        print(f"Teater: {film_info.get('teater')}")
        print(f"Harga: Rp {film_info.get('harga_tiket')}")

        # Menampilkan jadwal film
        print(f"\nJadwal Film {film_title}:")
        for jadwal in film_service.get_film_schedule(film_title):
            print(f"- {jadwal}")