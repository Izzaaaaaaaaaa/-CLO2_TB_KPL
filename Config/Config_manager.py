# ======================================
# AutoTicket CLI Project 
# ======================================
# File: config_manager.py

import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = 'config.json'):
        """
        Inisialisasi ConfigManager dengan path default ke config.json
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """
        Memuat konfigurasi dari file JSON eksternal.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file tidak ditemukan: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as file:
            try:
                self.config = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Format config.json tidak valid: {e}")

        return self.config

    # ===================== AKSES UMUM =====================

    def get_bioskop_info(self) -> Dict[str, Any]:
        return self.config.get("bioskop", {})

    def get_teater_info(self) -> Dict[str, Any]:
        return self.config.get("teater", {})

    def get_tiket_config(self) -> Dict[str, Any]:
        return self.config.get("tiket", {})

    def get_kontak_info(self) -> Dict[str, Any]:
        return self.config.get("kontak", {})

    # ===================== AKSES NILAI SPESIFIK =====================

    def get_max_kursi(self) -> int:
        return self.get_teater_info().get("MAX_KURSI", 100)

    def get_diskon_libur(self) -> int:
        return self.get_tiket_config().get("DISKON_LIBUR", 0)

    def get_diskon_member(self) -> int:
        return self.get_tiket_config().get("DISKON_MEMBER", 0)

    def get_waktu_diskon(self) -> Dict[str, int]:
        return self.get_tiket_config().get("WAKTU_DISKON", {})

    def get_diskon_by_jam(self, jam: str) -> int:
        """
        Mengembalikan diskon tambahan berdasarkan waktu (jam tayang film).
        """
        jam_int = int(jam.split(':')[0])
        waktu_diskon = self.get_waktu_diskon()
        if jam_int < 12:
            return waktu_diskon.get("pagi", 0)
        elif 12 <= jam_int < 18:
            return waktu_diskon.get("siang", 0)
        else:
            return waktu_diskon.get("malam", 0)

    def get_biaya_admin(self) -> int:
        return self.get_tiket_config().get("HARGA_ADMIN", 0)


# # Contoh penggunaan mandiri
# if __name__ == '__main__':
#     config = ConfigManager()
#     data = config.load_config()
#     print("📌 Nama Bioskop:", config.get_bioskop_info().get("nama"))
#     print("💺 Max Kursi:", config.get_max_kursi())
#     print("🎉 Diskon Libur:", config.get_diskon_libur(), "%")
#     print("🕒 Diskon Malam:", config.get_diskon_by_jam("20:00"), "%")
#     print("💸 Biaya Admin:", config.get_biaya_admin())
