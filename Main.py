# ======================================
# AutoTicket CLI Project
# ======================================
# File: main.py

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modul-modul yang sudah dikembangkan
from Config.Config_manager import ConfigManager
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Service.film_service import FilmService
from Validation.ticket_validator import TicketValidator


class Main:
    """
    Kelas utama untuk aplikasi AutoTicket CLI.
    Mengimplementasikan Code Reuse dengan menggunakan modul-modul yang sudah ada.
    """

    def __init__(self):
        """
        Inisialisasi aplikasi AutoTicket CLI
        """
        # Inisialisasi ConfigManager
        self.config_manager = ConfigManager()
        try:
            self.config_manager.load_config()
        except (FileNotFoundError, ValueError) as e:
            print(f"Error saat memuat konfigurasi: {e}")
            sys.exit(1)

        # Inisialisasi modul-modul lain dengan dependency injection
        self.film_service = FilmService(self.config_manager)
        self.price_calculator = PriceCalculator(self.config_manager)
        self.seat_manager = SeatManager(self.config_manager)
        self.ticket_validator = TicketValidator(self.config_manager)

        # Informasi bioskop
        self.bioskop_info = self.config_manager.get_bioskop_info()

    def clear_screen(self):
        """
        Membersihkan layar terminal
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_header(self):
        """
        Menampilkan header aplikasi
        """
        self.clear_screen()
        print("=" * 50)
        print(f"  {self.bioskop_info.get('nama', 'AutoTicket')} - Sistem Pemesanan Tiket")
        print(f"  {self.bioskop_info.get('lokasi', '')}")
        print("=" * 50)
        print(f"  Tanggal: {datetime.now().strftime('%d %B %Y')}")
        print("=" * 50)

    def show_menu(self):
        """
        Menampilkan menu utama aplikasi
        """
        self.show_header()
        print("\n=== AutoTicket Menu ===")
        print("1. Lihat Daftar Film")
        print("2. Pesan Tiket")
        print("3. Lihat Status Kursi")
        print("4. Jalankan API Server")
        print("0. Keluar")
        print("=" * 20)
        return input("Pilih menu: ")

    def show_films(self):
        """
        Menampilkan daftar film yang tersedia
        """
        self.show_header()
        print("\n=== Daftar Film ===\n")

        films = self.film_service.get_all_films()
        if not films:
            print("Tidak ada film yang tersedia saat ini.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        for i, film in enumerate(films, 1):
            print(f"{i}. {film['judul']} - {film['genre']} ({film['durasi']} menit)")

        print("\n0. Kembali ke Menu Utama")
        choice = input("\nPilih film untuk melihat detail (1-{}): ".format(len(films)))

        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(films):
            self.show_film_detail(films[int(choice) - 1]['judul'])
        else:
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk melanjutkan...")

    def show_film_detail(self, title: str):
        """
        Menampilkan detail film dan jadwal tayang

        Args:
            title: Judul film
        """
        self.show_header()
        print(f"\n=== Detail Film ===\n")

        film_info = self.film_service.get_film_info(title)
        if not film_info:
            print(f"Film '{title}' tidak ditemukan.")
            input("\nTekan Enter untuk kembali...")
            return

        print(f"Judul    : {film_info['judul']}")
        print(f"Genre    : {film_info['genre']}")
        print(f"Durasi   : {film_info['durasi']} menit")
        print(f"Sinopsis : {film_info['sinopsis']}")
        print(f"Teater   : {film_info['teater']}")
        print(f"Harga    : Rp {film_info['harga_tiket']}")

        print("\nJadwal Tayang:")
        for i, jadwal in enumerate(film_info['jadwal'], 1):
            print(f"{i}. {jadwal}")

        print("\n1. Pesan Tiket untuk Film Ini")
        print("0. Kembali ke Daftar Film")

        choice = input("\nPilihan Anda: ")
        if choice == "1":
            self.order_ticket(title)
        elif choice != "0":
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk melanjutkan...")

    def show_seat_status(self, teater_name: Optional[str] = None):
        """
        Menampilkan status kursi untuk teater tertentu

        Args:
            teater_name: Nama teater, jika None akan meminta input dari pengguna
        """
        self.show_header()
        print("\n=== Status Kursi ===\n")

        if teater_name is None:
            # Dapatkan semua teater yang tersedia
            teaters = set()
            for film in self.film_service.get_all_films():
                film_info = self.film_service.get_film_info(film['judul'])
                if film_info and 'teater' in film_info:
                    teaters.add(film_info['teater'])

            if not teaters:
                print("Tidak ada teater yang tersedia.")
                input("\nTekan Enter untuk kembali ke menu...")
                return

            print("Teater yang tersedia:")
            teater_list = list(teaters)
            for i, teater in enumerate(teater_list, 1):
                print(f"{i}. {teater}")

            print("\n0. Kembali ke Menu Utama")
            choice = input("\nPilih teater (1-{}): ".format(len(teater_list)))

            if choice == "0":
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(teater_list):
                teater_name = teater_list[int(choice) - 1]
            else:
                print("Pilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
                return

        # Tampilkan layout kursi
        if teater_name not in self.seat_manager.seat_status:
            print(f"Teater '{teater_name}' tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        print(f"Status Kursi untuk Teater {teater_name}:\n")
        layout = self.seat_manager.get_seat_layout(teater_name)
        for row in layout:
            print(" ".join(row))

        print("\nKeterangan:")
        print("O = Kursi tersedia")
        print("X = Kursi sudah dipesan")

        input("\nTekan Enter untuk kembali ke menu...")

    def order_ticket(self, film_title: Optional[str] = None):
        """
        Proses pemesanan tiket

        Args:
            film_title: Judul film, jika None akan meminta input dari pengguna
        """
        self.show_header()
        print("\n=== Pemesanan Tiket ===\n")

        # Jika judul film belum ditentukan, minta pengguna memilih film
        if film_title is None:
            films = self.film_service.get_all_films()
            if not films:
                print("Tidak ada film yang tersedia saat ini.")
                input("\nTekan Enter untuk kembali ke menu...")
                return

            print("Film yang tersedia:")
            for i, film in enumerate(films, 1):
                print(f"{i}. {film['judul']} - {film['genre']} ({film['durasi']} menit)")

            print("\n0. Kembali ke Menu Utama")
            choice = input("\nPilih film (1-{}): ".format(len(films)))

            if choice == "0":
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(films):
                film_title = films[int(choice) - 1]['judul']
            else:
                print("Pilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
                return

        # Dapatkan informasi film
        film_info = self.film_service.get_film_info(film_title)
        if not film_info:
            print(f"Film '{film_title}' tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Pilih jadwal tayang
        print(f"\nJadwal tayang untuk {film_title}:")
        for i, jadwal in enumerate(film_info['jadwal'], 1):
            print(f"{i}. {jadwal}")

        print("\n0. Kembali ke Menu Utama")
        choice = input("\nPilih jadwal (1-{}): ".format(len(film_info['jadwal'])))

        if choice == "0":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(film_info['jadwal']):
            showtime = film_info['jadwal'][int(choice) - 1]
        else:
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk melanjutkan...")
            return

        # Tanyakan apakah hari libur dan status member
        is_holiday = input("Apakah hari ini hari libur? (y/n): ").lower() == 'y'
        is_member = input("Apakah Anda member? (y/n): ").lower() == 'y'

        # Hitung harga
        price_info = self.price_calculator.get_price(film_title, showtime, is_holiday, is_member)
        if not price_info:
            print("Gagal menghitung harga tiket.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Tampilkan informasi harga
        print("\n=== Informasi Harga ===")
        print(f"Harga dasar: Rp {price_info['harga_dasar']}")
        print(f"Diskon waktu ({price_info['diskon_waktu']['persen']}%): Rp {price_info['diskon_waktu']['nominal']}")

        if is_holiday:
            print(
                f"Diskon hari libur ({price_info['diskon_libur']['persen']}%): Rp {price_info['diskon_libur']['nominal']}")

        if is_member:
            print(
                f"Diskon member ({price_info['diskon_member']['persen']}%): Rp {price_info['diskon_member']['nominal']}")

        print(f"Total diskon: Rp {price_info['total_diskon']}")
        print(f"Harga setelah diskon: Rp {price_info['harga_setelah_diskon']}")
        print(f"Biaya admin: Rp {price_info['biaya_admin']}")
        print(f"Total harga per tiket: Rp {price_info['total_harga']}")

        # Konfirmasi pemesanan
        confirm = input("\nLanjutkan pemesanan? (y/n): ").lower()
        if confirm != 'y':
            print("Pemesanan dibatalkan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Pilih kursi
        teater_name = film_info['teater']
        self.show_header()
        print(f"\n=== Pilih Kursi untuk {film_title} ({showtime}) ===\n")

        # Tampilkan layout kursi
        print(f"Status Kursi untuk Teater {teater_name}:\n")
        layout = self.seat_manager.get_seat_layout(teater_name)
        for row in layout:
            print(" ".join(row))

        print("\nKeterangan:")
        print("O = Kursi tersedia")
        print("X = Kursi sudah dipesan")

        # Minta input kursi
        while True:
            seats_input = input("\nMasukkan kode kursi (pisahkan dengan koma, contoh: A1,A2): ")
            if not seats_input:
                print("Input tidak boleh kosong!")
                continue

            seats = [seat.strip().upper() for seat in seats_input.split(',')]
            valid_seats = True

            # Validasi kursi
            for seat in seats:
                seat_index = self.seat_manager.get_seat_index(seat)
                if seat_index == -1:
                    print(f"Format kursi '{seat}' tidak valid!")
                    valid_seats = False
                    break

                if seat_index >= len(self.seat_manager.seat_status[teater_name]) or not \
                self.seat_manager.seat_status[teater_name][seat_index]:
                    print(f"Kursi '{seat}' tidak tersedia!")
                    valid_seats = False
                    break

            if valid_seats:
                break

        # Hitung total harga
        total_price = price_info['total_harga'] * len(seats)

        # Konfirmasi pemesanan final
        self.show_header()
        print("\n=== Konfirmasi Pemesanan ===\n")
        print(f"Film: {film_title}")
        print(f"Jadwal: {showtime}")
        print(f"Teater: {teater_name}")
        print(f"Kursi: {', '.join(seats)}")
        print(f"Harga per tiket: Rp {price_info['total_harga']}")
        print(f"Total harga: Rp {total_price}")

        confirm = input("\nKonfirmasi pemesanan? (y/n): ").lower()
        if confirm != 'y':
            print("Pemesanan dibatalkan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Proses pemesanan
        for seat in seats:
            seat_index = self.seat_manager.get_seat_index(seat)
            self.seat_manager.seat_status[teater_name][seat_index] = False

        # Tampilkan tiket
        reservation_id = f"RES-{hash(str(seats) + str(total_price)) % 10000:04d}"

        self.show_header()
        print("\n=== Tiket ===\n")
        print("=" * 40)
        print(f"  {self.bioskop_info.get('nama', 'AutoTicket')}")
        print("=" * 40)
        print(f"  ID Reservasi: {reservation_id}")
        print(f"  Film: {film_title}")
        print(f"  Jadwal: {showtime}")
        print(f"  Teater: {teater_name}")
        print(f"  Kursi: {', '.join(seats)}")
        print(f"  Total: Rp {total_price}")
        print("=" * 40)
        print("  Terima kasih telah menggunakan AutoTicket!")
        print("=" * 40)

        input("\nTekan Enter untuk kembali ke menu...")

    def run_api(self):
        """
        Menjalankan aplikasi dalam mode API
        """
        self.show_header()
        print("\n=== AutoTicket API Server ===\n")

        try:
            import uvicorn
            print("Memulai API server...")
            print("Akses API di http://localhost:8000")
            print("Akses dokumentasi Swagger di http://localhost:8000/docs")
            print("\nTekan Ctrl+C untuk menghentikan server.")

            # Import app dari api.py
            from api import app
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError:
            print("Error: FastAPI atau Uvicorn tidak terinstall.")
            print("Silakan install dengan 'pip install fastapi uvicorn'")
            input("\nTekan Enter untuk kembali ke menu...")
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
            input("\nTekan Enter untuk kembali ke menu...")

    def run(self):
        """
        Menjalankan aplikasi AutoTicket CLI
        """
        while True:
            choice = self.show_menu()

            if choice == "1":
                self.show_films()
            elif choice == "2":
                self.order_ticket()
            elif choice == "3":
                self.show_seat_status()
            elif choice == "4":
                self.run_api()
            elif choice == "0":
                self.show_header()
                print("\nTerima kasih telah menggunakan AutoTicket!")
                print("Sampai jumpa kembali!\n")
                sys.exit(0)
            else:
                print("Pilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")


# Menjalankan aplikasi jika file ini dijalankan langsung
if __name__ == "__main__":
    app = Main()
    app.run()