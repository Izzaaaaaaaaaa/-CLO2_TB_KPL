# ======================================
# AutoTicket CLI Project
# ======================================
# File: seat_manager.py

from typing import Dict, List, Tuple, Optional
from config.config_manager import ConfigManager


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

        # State untuk automata penempatan kursi
        self.STATES = {
            "INITIAL": 0,  # State awal
            "SEARCHING": 1,  # Sedang mencari kursi
            "CONSECUTIVE": 2,  # Menemukan kursi berurutan
            "SCATTERED": 3,  # Menemukan kursi terpisah
            "FULL": 4,  # Teater penuh
            "COMPLETED": 5  # Penempatan selesai
        }

        # State saat ini
        self.current_state = self.STATES["INITIAL"]

    def get_seat_status(self, teater_name: str) -> List[bool]:
        return self.seat_status.get(teater_name, [])

    def get_available_seats(self, teater_name: str) -> List[int]:
        seats = self.seat_status.get(teater_name, [])
        return [i for i, available in enumerate(seats) if available]

    def get_total_available_seats(self, teater_name: str) -> int:
        return sum(1 for seat in self.seat_status.get(teater_name, []) if seat)

    # ===================== PENAMAAN KURSI =====================

    def get_seat_name(self, nomor_kursi: int) -> str:
        try:
            nomor_kursi = int(nomor_kursi)
        except (ValueError, TypeError):
            return "Invalid"

        huruf_baris = chr(65 + (nomor_kursi // 10))  # 65 = 'A'
        nomor = (nomor_kursi % 10) + 1
        return f"{huruf_baris}{nomor}"

    def get_seat_index(self, seat_name: str) -> int:
        if len(seat_name) < 2:
            return -1

        row_letter = seat_name[0].upper()
        try:
            col = int(seat_name[1:])
        except ValueError:
            return -1

        # Konversi huruf ke baris (A -> 0, B -> 1, dst)
        row = ord(row_letter) - 65  # 65 adalah kode ASCII untuk 'A'

        # Asumsi: 10 kursi per baris
        return row * 10 + (col - 1)  # -1 karena kolom dimulai dari 1

    # ===================== PENEMPATAN KURSI =====================

    def _find_consecutive_seats(self, teater_name: str, jumlah_kursi: int) -> List[int]:
        seats = self.seat_status.get(teater_name, [])
        if not seats:
            return []

        consecutive_count = 0
        start_index = -1

        for i in range(len(seats)):
            if seats[i]:  # Jika kursi tersedia
                if consecutive_count == 0:
                    start_index = i
                consecutive_count += 1

                if consecutive_count == jumlah_kursi:
                    return list(range(start_index, start_index + jumlah_kursi))
            else:
                consecutive_count = 0
                start_index = -1

        return []

    def assign_seat(self, teater_name: str, jumlah_kursi: int = 1, prefer_consecutive: bool = True) -> Optional[
        List[str]]:
        # Reset state
        self.current_state = self.STATES["INITIAL"]

        # Cek teater ada
        if teater_name not in self.seat_status:
            return None

        # Cek jumlah kursi tersedia
        if self.get_total_available_seats(teater_name) < jumlah_kursi:
            self.current_state = self.STATES["FULL"]
            return None

        # Transisi ke state SEARCHING
        self.current_state = self.STATES["SEARCHING"]

        allocated_seats = []

        # Jika prefer kursi berurutan, coba cari kursi berurutan dulu
        if prefer_consecutive:
            consecutive_seats = self._find_consecutive_seats(teater_name, jumlah_kursi)

            if consecutive_seats:
                # Transisi ke state CONSECUTIVE
                self.current_state = self.STATES["CONSECUTIVE"]
                allocated_seats = consecutive_seats
            else:
                # Jika tidak ada kursi berurutan, gunakan kursi terpisah
                self.current_state = self.STATES["SCATTERED"]
                available_seats = self.get_available_seats(teater_name)
                allocated_seats = available_seats[:jumlah_kursi]
        else:
            # Langsung gunakan kursi terpisah
            self.current_state = self.STATES["SCATTERED"]
            available_seats = self.get_available_seats(teater_name)
            allocated_seats = available_seats[:jumlah_kursi]

        # Tandai kursi sebagai tidak tersedia
        for idx in allocated_seats:
            self.seat_status[teater_name][idx] = False

        # Transisi ke state COMPLETED
        self.current_state = self.STATES["COMPLETED"]

        # Kembalikan nama kursi
        return [self.get_seat_name(idx) for idx in allocated_seats]

    def release_seat(self, teater_name: str, seat_names: List[str]) -> bool:
        if teater_name not in self.seat_status:
            return False

        success = True

        for seat_name in seat_names:
            seat_index = self.get_seat_index(seat_name)
            if 0 <= seat_index < len(self.seat_status[teater_name]):
                self.seat_status[teater_name][seat_index] = True
            else:
                success = False

        return success

    # ===================== DISKON TIKET =====================

    def apply_discount(
            self,
            harga_awal: int,
            jam_tayang: str,
            is_member: bool = False,
            is_libur: bool = False
    ) -> int:
        total_diskon_persen = 0

        if is_libur:
            total_diskon_persen += self.config_manager.get_diskon_libur()
        if is_member:
            total_diskon_persen += self.config_manager.get_diskon_member()

        total_diskon_persen += self.config_manager.get_diskon_by_jam(jam_tayang)

        harga_setelah_diskon = harga_awal - (harga_awal * total_diskon_persen // 100)
        return harga_setelah_diskon
