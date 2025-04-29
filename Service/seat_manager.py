from typing import Dict, List, Tuple, Optional
from Config.Config_manager import ConfigManager

class SeatManager:

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.max_kursi = config_manager.get_max_kursi()
        self.teater_info = config_manager.get_teater_info()

        self.seat_status: Dict[str, List[bool]] = {}

        jumlah_teater = self.teater_info.get("jumlah_teater", 0)
        tipe_teater = self.teater_info.get("tipe_teater", {})

        for teater_name in tipe_teater.keys():
            self.seat_status[teater_name] = [True] * self.max_kursi

    def get_seat_status(self, teater_name: str) -> List[bool]:
        return self.seat_status.get(teater_name, [])

    def get_available_seats(self, teater_name: str) -> List[int]:
        seats = self.seat_status.get(teater_name, [])
        return [i for i, available in enumerate(seats) if available]

    def get_total_available_seats(self, teater_name: str) -> int:
        return sum(1 for seat in self.seat_status.get(teater_name, []) if seat)
    
# ===================== PENAMAAN KURSI =====================

    def get_seat_name(self, nomor_kursi: int) -> str:
       # Mengubah nomor kursi menjadi nama baris, seperti A1, B2, dst
        huruf_baris = chr(65 + (nomor_kursi // 10))  # 65 = 'A'
        nomor = (nomor_kursi % 10) + 1
        return f"{huruf_baris}{nomor}"
# ===================== PENEMPATAN KURSI =====================
    def assign_seat(self, teater_name: str, jumlah_kursi: int = 1) -> Optional[List[str]]:

        kursi_tersedia = self.get_available_seats(teater_name)

        if len(kursi_tersedia) < jumlah_kursi:
            return None  # Tidak cukup kursi tersedia

        kursi_yang_dipilih = kursi_tersedia[:jumlah_kursi]

        # Tandai kursi tersebut sebagai tidak tersedia
        for idx in kursi_yang_dipilih:
            self.seat_status[teater_name][idx] = False

        return [self.get_seat_name(idx) for idx in kursi_yang_dipilih]
 # ===================== DISKON TIKET =====================
def apply_discount(
        self,
        harga_awal: int,
        jam_tayang: str,
        is_member: bool = False,
        is_libur: bool = False
    ) -> int:
        total_diskon = 0

        if is_libur:
            total_diskon += self.config_manager.get_diskon_libur()
        if is_member:
            total_diskon += self.config_manager.get_diskon_member()

        total_diskon += self.config_manager.get_diskon_by_jam(jam_tayang)

        harga_setelah_diskon = harga_awal - (harga_awal * total_diskon // 100)
        return max(harga_setelah_diskon, 0)

