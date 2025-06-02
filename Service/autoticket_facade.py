from typing import Dict, List, Any, Optional, Union
from Config.Config_manager import ConfigManager
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator
from entities import Film
from data_manager import DataManager

class AutoTicketFacade:
    """
    Facade untuk sistem AutoTicket yang menyediakan antarmuka tingkat tinggi
    yang menyembunyikan kompleksitas subsistem di belakangnya.

    Mengimplementasikan Facade Pattern dengan:
    - Menyederhanakan antarmuka kompleks
    - Mengelola interaksi antar subsistem
    - Menyembunyikan kompleksitas implementasi
    """
    def __init__(self, config_path: str = 'config.json'):
        # Inisialisasi konfigurasi - Subsistem 1
        self._config = ConfigManager(config_path)
        self._config.load_config()

        # Setup film manager - Subsistem 2
        self._film_manager = DataManager[Film]()
        self._load_film_data()

        # Inisialisasi subsistem lainnya
        self._seat_manager = SeatManager(self._config)
        self._calculator = PriceCalculator(self._config)
        self._validator = TicketValidator(self._config)

    # ===================== METODE PRIVATE UNTUK MENANGANI LOGIKA INTERNAL =====================

    def _load_film_data(self) -> None:
        """Memuat data film dari konfigurasi (metode private)"""
        film_data = self._config.config.get("film", [])
        for f in film_data:
            self._film_manager.tambah(Film(**f))

    # ===================== OPERASI PUBLIK TERPADU (UNIFIED PUBLIC API) =====================

    def get_films(self, genre: Optional[str] = None) -> List[Film]:
        """
        Mendapatkan daftar film, dengan filter opsional berdasarkan genre.

        Args:
            genre: Opsional. Filter berdasarkan genre.

        Returns:
            Daftar film, difilter jika genre ditentukan.
        """
        films = self._film_manager.ambil_semua()

        if genre:
            # Filter berdasarkan genre jika ditentukan
            return [f for f in films if genre.lower() in f.genre.lower()]

        return films

    def get_film_detail(self, title: str) -> Dict[str, Any]:
        """
        Mendapatkan detail film termasuk jadwal, teater, dan harga dasar.

        Args:
            title: Judul film

        Returns:
            Dict berisi detail film atau None jika tidak ditemukan
        """
        film = next((f for f in self._film_manager.ambil_semua() if f.judul.lower() == title.lower()), None)

        if not film:
            return {"success": False, "message": f"Film '{title}' tidak ditemukan"}

        base_price = self._calculator.get_base_price(film.judul)

        return {
            "success": True,
            "film": film,
            "teater": film.teater,
            "jadwal": film.jadwal,
            "harga_dasar": base_price
        }

    def check_seats(self, theater_name: Optional[str] = None, film_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Memeriksa ketersediaan kursi di teater tertentu atau teater untuk film tertentu.

        Args:
            theater_name: Nama teater (opsional jika film_title diberikan)
            film_title: Judul film (opsional jika theater_name diberikan)

        Returns:
            Informasi ketersediaan kursi
        """
        # Tentukan teater berdasarkan film jika tidak ada nama teater yang diberikan
        if not theater_name and film_title:
            film = next((f for f in self._film_manager.ambil_semua() if f.judul.lower() == film_title.lower()), None)
            if not film:
                return {"success": False, "message": f"Film '{film_title}' tidak ditemukan"}
            theater_name = film.teater

        if not theater_name:
            return {"success": False, "message": "Diperlukan nama teater atau judul film"}

        if theater_name not in self._seat_manager.seat_status:
            return {"success": False, "message": f"Teater '{theater_name}' tidak ditemukan"}
        total = self._seat_manager.get_total_available_seats(theater_name)

        if total <= 0:
            return {"success": False, "message": "Tidak ada kursi tersedia"}

        seats = self._seat_manager.get_available_seats(theater_name)
        seat_names = [self._seat_manager.get_seat_name(i) for i in seats[:10]]

        return {
            "success": True,
            "teater": theater_name,
            "total": total,
            "contoh_kursi": seat_names
        }

    def calculate_ticket_price(self, film_title: str, showtime: str,
                               is_holiday: bool = False, is_member: bool = False,
                               ticket_count: int = 1) -> Dict[str, Any]:
        """
        Menghitung harga tiket dengan semua diskon yang berlaku.

        Args:
            film_title: Judul film
            showtime: Jam tayang
            is_holiday: Apakah hari libur
            is_member: Apakah member
            ticket_count: Jumlah tiket

        Returns:
            Informasi harga tiket
        """
        # Validasi film dan jadwal
        film = next((f for f in self._film_manager.ambil_semua() if f.judul.lower() == film_title.lower()), None)

        if not film:
            return {"success": False, "message": f"Film '{film_title}' tidak ditemukan"}

        if showtime not in film.jadwal:
            return {"success": False, "message": f"Jadwal '{showtime}' tidak tersedia"}

        # Gunakan subsistem kalkulator untuk menghitung harga
        price_info = self._calculator.get_price(film_title, showtime, is_holiday, is_member, ticket_count)

        return {
            "success": True,
            "film": film_title,
            "harga_dasar": price_info.get("harga_dasar", 0),
            "diskon": {
                "waktu": price_info.get("diskon_waktu", {}).get("nominal", 0),
                "libur": price_info.get("diskon_libur", {}).get("nominal", 0),
                "member": price_info.get("diskon_member", {}).get("nominal", 0)
            },
            "total_diskon": price_info.get("total_diskon", 0),
            "biaya_admin": price_info.get("biaya_admin", 0),
            "harga_per_tiket": price_info.get("harga_per_tiket", 0),
            "jumlah_tiket": ticket_count,
            "total": price_info.get("total_harga", 0)
        }

    def book_tickets(self, film_title: str, showtime: str, ticket_count: int,
                    is_holiday: bool = False, is_member: bool = False,
                    seat_preference: str = "berurutan") -> Dict[str, Any]:
        """
        Operasi terpadu untuk memesan tiket film - menggabungkan berbagai subsistem.
        Menyembunyikan kompleksitas validasi, alokasi kursi, dan perhitungan harga.

        Args:
            film_title: Judul film
            showtime: Jam tayang
            ticket_count: Jumlah tiket
            is_holiday: Apakah hari libur
            is_member: Apakah member
            seat_preference: Preferensi kursi ("berurutan" atau "bebas")

        Returns:
            Hasil pemesanan tiket
        """
        # 1. Validasi parameter dasar
        validation = self._validator.validate_ticket_request(film_title, showtime, ticket_count)
        if not validation["valid"]:
            return {"success": False, "message": validation["message"]}

        teater = validation["teater"]

        # 2. Periksa ketersediaan kursi
        available_seats = self._seat_manager.get_total_available_seats(teater)
        if available_seats < ticket_count:
            return {
                "success": False,
                "message": f"Kursi tidak cukup. Hanya tersedia {available_seats} kursi"
            }

        # 3. Alokasi kursi
        prefer_consecutive = (seat_preference.lower() == "berurutan")
        seats = self._seat_manager.assign_seat(teater, ticket_count, prefer_consecutive)

        if not seats or len(seats) < ticket_count:
            return {"success": False, "message": "Gagal mengalokasikan kursi"}

        # 4. Hitung harga tiket
        price_result = self.calculate_ticket_price(
            film_title, showtime, is_holiday, is_member, ticket_count
        )

        if not price_result["success"]:
            # Kembalikan kursi jika ada masalah dengan harga
            self._seat_manager.release_seat(teater, seats)
            return price_result

        # 5. Hasilkan nomor reservasi unik
        import secrets
        reservation_id = f"RES-{secrets.randbelow(9000) + 1000}"

        # 6. Menggabungkan semua informasi untuk hasil akhir
        return {
            "success": True,
            "reservation_id": reservation_id,
            "film": film_title,
            "teater": teater,
            "jadwal": showtime,
            "kursi": seats,
            "jumlah_tiket": ticket_count,
            "is_holiday": is_holiday,
            "is_member": is_member,
            "harga": price_result["total"],
            "status": "confirmed"
        }

    def cancel_booking(self, teater: str, seats: List[str]) -> Dict[str, Any]:
        """
        Membatalkan pemesanan dengan membebaskan kursi.

        Args:
            teater: Nama teater
            seats: Daftar kursi yang akan dibebaskan

        Returns:
            Status operasi
        """
        result = self._seat_manager.release_seat(teater, seats)

        if result:
            return {"success": True, "message": "Reservasi berhasil dibatalkan"}
        else:
            return {"success": False, "message": "Gagal membatalkan reservasi"}
