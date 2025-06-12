# ======================================
# AutoTicket CLI Project
# ======================================
# File: validation/ticket_validator.py

from typing import Dict, List, Optional
from config.config_manager import ConfigManager
from service.film_service import get_film_schedule


class TicketValidator:
    """
    Kelas untuk validasi tiket dan input pengguna.
    """

    @staticmethod
    def validate_ticket(film_title: str, showtime: str) -> bool:
        """
        Validasi apakah jam tayang tersedia dalam jadwal film.

        Args:
            film_title (str): Judul film
            showtime (str): Jam tayang

        Returns:
            bool: True jika jam tayang valid untuk film tersebut
        """
        schedule = get_film_schedule(film_title)
        return showtime in schedule if schedule else False

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.loaded_config = self.config_manager.load_config()
        self.film_data = self.loaded_config.get("film", [])
        self.teater_data = self.config_manager.get_teater_info().get("tipe_teater", {})

    def is_valid_film(self, film_title: str) -> bool:
        """
        Mengecek apakah judul film tersedia dalam konfigurasi.

        Args:
            film_title (str): Judul film

        Returns:
            bool: True jika judul film valid
        """
        return any(
            film.get("judul", "").lower() == film_title.lower()
            for film in self.film_data
        )

    def get_valid_showtimes(self, film_title: str) -> Optional[List[str]]:
        """
        Mengambil daftar jam tayang untuk film tertentu.

        Args:
            film_title (str): Judul film

        Returns:
            List[str] | None: Daftar jam tayang jika tersedia
        """
        for film in self.film_data:
            if film.get("judul", "").lower() == film_title.lower():
                return film.get("jadwal", [])
        return None

    def is_valid_showtime(self, film_title: str, selected_time: str) -> bool:
        """
        Mengecek apakah jam tayang tersedia untuk film.

        Args:
            film_title (str): Judul film
            selected_time (str): Jam tayang

        Returns:
            bool: True jika tersedia
        """
        valid_times = self.get_valid_showtimes(film_title)
        return selected_time in valid_times if valid_times else False

    def get_teater_by_film(self, film_title: str) -> Optional[str]:
        """
        Mengambil nama teater berdasarkan film.

        Args:
            film_title (str): Judul film

        Returns:
            str | None: Nama teater jika ditemukan
        """
        for film in self.film_data:
            if film.get("judul", "").lower() == film_title.lower():
                return film.get("teater")
        return None

    def is_valid_teater(self, teater_name: str) -> bool:
        """
        Mengecek apakah nama teater valid.

        Args:
            teater_name (str): Nama teater

        Returns:
            bool: True jika valid
        """
        return teater_name in self.teater_data

    def validate_ticket_request(
        self,
        film_title: str,
        showtime: str,
        ticket_count: int
    ) -> Dict[str, any]:
        """
        Validasi permintaan tiket pengguna.

        Args:
            film_title (str): Judul film
            showtime (str): Jam tayang
            ticket_count (int): Jumlah tiket

        Returns:
            Dict[str, any]: Hasil validasi dan pesan
        """
        if not self.is_valid_film(film_title):
            return {
                "valid": False,
                "message": f"❌ Film '{film_title}' tidak ditemukan."
            }

        if not self.is_valid_showtime(film_title, showtime):
            return {
                "valid": False,
                "message": f"❌ Jam tayang '{showtime}' tidak tersedia untuk film '{film_title}'."
            }

        teater_name = self.get_teater_by_film(film_title)
        if not self.is_valid_teater(teater_name):
            return {
                "valid": False,
                "message": f"❌ Teater '{teater_name}' tidak valid atau belum terdaftar."
            }

        max_seats = self.config_manager.get_max_kursi()
        if ticket_count < 1 or ticket_count > max_seats:
            return {
                "valid": False,
                "message": f"❌ Jumlah tiket harus antara 1 dan {max_seats}."
            }

        return {
            "valid": True,
            "message": "✅ Tiket valid untuk diproses.",
            "teater": teater_name
        }


# # Contoh penggunaan mandiri (opsional saat testing CLI)
# if __name__ == "__main__":
#     config = ConfigManager()
#     validator = TicketValidator(config)
#     result = validator.validate_ticket_request("Avengers: Endgame", "13:00", 2)
#     print(result["message"])
#     if result["valid"]:
#         print(f"🎟️ Film: Avengers: Endgame | Jam: 13:00 | Teater: {result['teater']} | Jumlah: 2")
