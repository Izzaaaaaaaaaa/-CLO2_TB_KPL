from typing import Dict, Any
from config.config_manager import ConfigManager


class PriceCalculator:
    """
    Kelas untuk menghitung harga tiket berdasarkan berbagai parameter.
    Mengimplementasikan table-driven construction untuk perhitungan harga.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Inisialisasi PriceCalculator dengan ConfigManager untuk mendapatkan konfigurasi harga

        Args:
            config_manager: Instance dari ConfigManager yang telah dimuat
        """
        self.config_manager = config_manager

        # Memuat konfigurasi diskon dari config
        self.diskon_libur = config_manager.get_diskon_libur()
        self.diskon_member = config_manager.get_diskon_member()
        self.waktu_diskon = config_manager.get_waktu_diskon()
        self.biaya_admin = config_manager.get_biaya_admin()

        # Membuat tabel harga film (table-driven construction)
        self.film_prices = self._build_film_price_table()

    def _build_film_price_table(self) -> Dict[str, int]:
        film_prices = {}
        films = self.config_manager.config.get("film", [])

        for film in films:
            judul = film.get("judul", "")
            harga = film.get("harga_tiket", 0)
            film_prices[judul] = harga

        return film_prices

    def get_base_price(self, film_title: str) -> int:

        return self.film_prices.get(film_title, 0)

    def get_price(self, film_title: str, jam_tayang: str, is_holiday: bool = False, is_member: bool = False,jumlah_tiket: int = 1) -> Dict[
        str, Any]:
        """
        Menghitung harga tiket berdasarkan berbagai parameter

        Args:
            film_title: Judul film
            jam_tayang: Jam tayang
            is_holiday: Apakah hari libur
            is_member: Apakah member

        Returns:
            Dictionary berisi informasi harga
        """
        # Mendapatkan harga dasar
        base_price = self.get_base_price(film_title)


        waktu_diskon_persen = self.config_manager.get_diskon_by_jam(jam_tayang)
        waktu_diskon_nominal = (base_price * waktu_diskon_persen) // 100

        # Menghitung diskon hari libur
        holiday_diskon = (base_price * self.diskon_libur) // 100 if is_holiday else 0

        # Menghitung diskon member
        member_diskon = (base_price * self.diskon_member) // 100 if is_member else 0

        # Menghitung total diskon
        total_diskon = waktu_diskon_nominal + holiday_diskon + member_diskon

        # Menghitung harga setelah diskon
        price_after_discount = base_price - total_diskon

        price_per_ticket = price_after_discount + self.biaya_admin

        # Menghitung total harga dengan biaya admin
        total_price = price_per_ticket * jumlah_tiket

        # Menyusun hasil perhitungan dalam bentuk dictionary
        result = {
            "film": film_title,
            "jam_tayang": jam_tayang,
            "harga_dasar": base_price,
            "diskon_waktu": {
                "persen": waktu_diskon_persen,
                "nominal": waktu_diskon_nominal
            },
            "diskon_libur": {
                "persen": self.diskon_libur if is_holiday else 0,
                "nominal": holiday_diskon
            },
            "diskon_member": {
                "persen": self.diskon_member if is_member else 0,
                "nominal": member_diskon
            },
            "total_diskon": total_diskon,
            "harga_setelah_diskon": price_after_discount,
            "biaya_admin": self.biaya_admin,
            "harga_per_tiket": price_per_ticket,
            "jumlah_tiket": jumlah_tiket,
            "total_harga": total_price,
            # Tambahkan kunci "total" untuk kompatibilitas dengan API
            "total": total_price
        }

        return result
