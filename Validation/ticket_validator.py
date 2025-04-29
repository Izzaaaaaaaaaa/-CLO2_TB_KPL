# ======================================
# AutoTicket CLI Project
# ======================================
# File: validation/ticket_validator.py

from typing import Dict, List, Optional
from config.config_manager import ConfigManager


class TicketValidator:
    """
    Kelas untuk melakukan validasi terhadap tiket dan input pengguna.
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.loaded_config = config_manager.load_config()
        self.film_data = self.loaded_config.get("film", [])
        self.teater_data = self.config_manager.get_teater_info().get("tipe_teater", {})

    def is_valid_film(self, film_title: str) -> bool:
        """
        Mengecek apakah judul film valid dan tersedia.

        Args:
            film_title (str): Judul film

        Returns:
            bool: True jika valid, False jika tidak
        """
        return any(film.get("judul", "").lower() == film_title.lower() for film in self.film_data)

    def get_valid_showtimes(self, film_title: str) -> Optional[List[str]]:
        """
        Mengambil daftar jam tayang yang valid untuk film tertentu.

        Args:
            film_title (str): Judul film

        Returns:
            List[str] | None: List jam tayang jika ditemukan, None jika tidak valid
        """
        for film in self.film_data:
            if film.get("judul", "").lower() == film_title.lower():
                return film.get("jadwal", [])
        return None

    def is_valid_showtime(self, film_title: str, selected_time: str) -> bool:
        """
        Mengecek apakah jam tayang valid untuk film yang dipilih.

        Args:
            film_title (str): Judul film
            selected_time (str): Jam tayang

        Returns:
            bool: True jika jam tayang tersedia untuk film tersebut
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
                return film.get("teater", None)
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
        jam_tayang: str,
        jumlah_tiket: int
    ) -> Dict[str, any]:
        """
        Validasi permintaan tiket dari user.

        Args:
            film_title (str): Judul film
            jam_tayang (str): Jam tayang
            jumlah_tiket (int): Jumlah tiket yang diminta

        Returns:
            Dict[str, any]: Status validasi dan pesan.
        """
        if not self.is_valid_film(film_title):
            return {"valid": False, "message": f"❌ Film '{film_title}' tidak ditemukan."}

        if not self.is_valid_showtime(film_title, jam_tayang):
            return {"valid": False, "message": f"❌ Jam tayang '{jam_tayang}' tidak tersedia untuk film '{film_title}'."}

        teater = self.get_teater_by_film(film_title)
        if not self.is_valid_teater(teater):
            return {"valid": False, "message": f"❌ Teater '{teater}' tidak valid atau belum terdaftar."}

        if jumlah_tiket < 1 or jumlah_tiket > self.config_manager.get_max_kursi():
            return {"valid": False, "message": f"❌ Jumlah tiket harus antara 1 dan {self.config_manager.get_max_kursi()}."}

        return {"valid": True, "message": "✅ Tiket valid untuk diproses.", "teater": teater}


# Contoh Penggunaan Mandiri
if __name__ == "__main__":
    config = ConfigManager()
    validator = TicketValidator(config)

    film = "Avengers: Endgame"
    jam = "13:00"
    jumlah = 2

    hasil = validator.validate_ticket_request(film, jam, jumlah)
    print(hasil["message"])
    if hasil["valid"]:
        print(f"🎟️ Film: {film} | Jam: {jam} | Teater: {hasil['teater']} | Jumlah: {jumlah}")
