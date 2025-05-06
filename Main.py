import os
import threading
import webbrowser
import uvicorn
from Config.Config_manager import ConfigManager
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator
from api import app
from entities import Film
from data_manager import DataManager

# Fungsi untuk menampilkan menu CLI
def tampilkan_menu():
    print("\n🎉 Selamat datang di AutoTicket CLI 🎟️")
    print("Silakan pilih menu berikut:")
    print("1. Lihat daftar film")
    print("2. Cari film berdasarkan genre")
    print("3. Lihat jadwal film")
    print("4. Lihat informasi film lengkap")
    print("5. Cek ketersediaan kursi")
    print("6. Pesan tiket")
    print("7. Jalankan API (Web Mode)")
    print("8. Keluar")

# Fungsi untuk menjalankan server FastAPI di thread terpisah
def run_api_server():
    print("\n🚀 Memulai server API di http://localhost:8000")
    webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="127.0.0.1", port=8000)

def main():
    # Load konfigurasi
    config = ConfigManager()
    config.load_config()

    # Load data film
    film_data = config.config.get("film", [])
    film_manager = DataManager[Film]()
    for f in film_data:
        film_manager.tambah(Film(**f))

    seat_manager = SeatManager(config)
    calculator = PriceCalculator(config)
    validator = TicketValidator(config)

    while True:
        tampilkan_menu()
        pilihan = input("Masukkan pilihan Anda (1-8): ").strip()

        if pilihan == '1':
            print("\n🎞 Daftar Film:")
            for film in film_manager.ambil_semua():
                print(f"- {film.judul} | Genre: {film.genre} | Teater: {film.teater} | Harga: Rp{film.harga_tiket}")

        elif pilihan == '2':
            genre = input("Masukkan genre: ").strip().lower()
            hasil = [f for f in film_manager.ambil_semua() if genre in f.genre.lower()]
            if hasil:
                print(f"\n🎬 Film dengan genre '{genre}':")
                for film in hasil:
                    print(f"- {film.judul}")
            else:
                print(f"⚠️ Tidak ada film dengan genre '{genre}'.")

        elif pilihan == '3':
            judul = input("Masukkan judul film: ").strip()
            film = film_manager.cari("judul", judul)
            if film:
                print(f"\n🕒 Jadwal tayang untuk {judul}: {', '.join(film[0].jadwal)}")
            else:
                print(f"⚠️ Tidak ada jadwal untuk film '{judul}'.")

        elif pilihan == '4':
            judul = input("Masukkan judul film: ").strip()
            film = film_manager.cari("judul", judul)
            if film:
                f = film[0]
                print(f"\n📋 Informasi lengkap film '{f.judul}':")
                print(f"Genre  : {f.genre}")
                print(f"Durasi : {f.durasi}")
                print(f"Rating : {f.rating}")
                print(f"Teater : {f.teater}")
                print(f"Jadwal : {', '.join(f.jadwal)}")
                print(f"Harga  : Rp{f.harga_tiket}")
            else:
                print(f"⚠️ Film '{judul}' tidak ditemukan.")

        elif pilihan == '5':
            teater = input("Masukkan nama teater: ").strip()
            if teater in seat_manager.seat_status:
                total = seat_manager.get_total_available_seats(teater)
                if total > 0:
                    seats = seat_manager.get_available_seats(teater)
                    print(f"\n💺 Kursi tersedia: {total}")
                    print("Contoh:", ', '.join(seat_manager.get_seat_name(i) for i in seats[:10]))
                else:
                    print("⚠️ Tidak ada kursi tersedia.")
            else:
                print(f"⚠️ Teater '{teater}' tidak ditemukan.")

        elif pilihan == '6':
            judul = input("Judul film: ").strip()
            jam = input("Jam tayang (HH:MM): ").strip()
            try:
                jumlah = int(input("Jumlah tiket: "))
            except ValueError:
                print("⚠️ Jumlah tiket harus angka.")
                continue
            is_libur = input("Hari libur? (y/n): ").strip().lower() == 'y'
            is_member = input("Member? (y/n): ").strip().lower() == 'y'

            film = film_manager.cari("judul", judul)
            if not film:
                print(f"⚠️ Film '{judul}' tidak ditemukan.")
                continue

            if jam not in film[0].jadwal:
                print(f"⚠️ Jadwal '{jam}' tidak tersedia.")
                continue

            teater = film[0].teater
            if seat_manager.get_total_available_seats(teater) < jumlah:
                print("⚠️ Kursi tidak cukup.")
                continue

            kursi = seat_manager.assign_seat(teater, jumlah)
            if not kursi:
                print("⚠️ Gagal mengalokasikan kursi.")
                continue

            harga = calculator.get_price(judul, jam, is_libur, is_member)

            print("\n✅ Tiket berhasil dipesan!")
            print(f"🎬 Film   : {judul}")
            print(f"🕒 Jam    : {jam}")
            print(f"🏢 Teater : {teater}")
            print(f"💺 Kursi  : {', '.join(kursi)}")
            print(f"💰 Total  : Rp{harga['total_harga']}")

        elif pilihan == '7':
            print("\n🌐 Mode Web (Swagger) sedang berjalan...")
            api_thread = threading.Thread(target=run_api_server, daemon=True)
            api_thread.start()
            input("🔙 Tekan Enter untuk kembali ke menu CLI...")

        elif pilihan == '8':
            print("\n🙏 Terima kasih telah menggunakan AutoTicket. Sampai jumpa di pemesanan berikutnya!")
            break

        else:
            print("⚠️ Pilihan tidak valid. Silakan pilih antara 1 hingga 8.")

if __name__ == "__main__":
    main()
import os
import threading
import webbrowser
import uvicorn
from Config.Config_manager import ConfigManager
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator
from api import app
from entities import Film
from data_manager import DataManager

def display_menu():
    print("\n Selamat datang di AutoTicket CLI ")
    print("Silakan pilih menu berikut:")
    print("1. Lihat daftar film")
    print("2. Cari film berdasarkan genre")
    print("3. Lihat jadwal film")
    print("4. Lihat informasi film lengkap")
    print("5. Cek ketersediaan kursi")
    print("6. Pesan tiket")
    print("7. Jalankan API (Web Mode)")
    print("8. Keluar")

def run_api_server():
    print("\n Memulai server API di http://localhost:8000")
    webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="127.0.0.1", port=8000)

def main():
    config = ConfigManager()
    config.load_config()

    film_data = config.config.get("film", [])
    film_manager = DataManager[Film]()
    for f in film_data:
        film_manager.tambah(Film(**f))

    seat_manager = SeatManager(config)
    calculator = PriceCalculator(config)
    validator = TicketValidator(config)

    while True:
        display_menu()
        choice = input("Masukkan pilihan Anda (1-8): ").strip()

        if choice == '1':
            print("\n Daftar Film:")
            for film in film_manager.ambil_semua():
                print(f"- {film.judul} | Genre: {film.genre} | Teater: {film.teater} | Harga: Rp{film.harga_tiket}")

        elif choice == '2':
            genre = input("Masukkan genre: ").strip().lower()
            hasil = [f for f in film_manager.ambil_semua() if genre in f.genre.lower()]
            if hasil:
                print(f"\n Film dengan genre '{genre}':")
                for film in hasil:
                    print(f"- {film.judul}")
            else:
                print(f" Tidak ada film dengan genre '{genre}'.")

        elif choice == '3':
            judul = input("Masukkan judul film: ").strip()
            film = film_manager.cari("judul", judul)
            if film:
                print(f"\n Jadwal tayang untuk {judul}: {', '.join(film[0].jadwal)}")
            else:
                print(f" Tidak ada jadwal untuk film '{judul}'.")

        elif choice == '4':
            judul = input("Masukkan judul film: ").strip()
            film = film_manager.cari("judul", judul)
            if film:
                f = film[0]
                print(f"\n Informasi lengkap film '{f.judul}':")
                print(f"Genre  : {f.genre}")
                print(f"Durasi : {f.durasi}")
                print(f"Rating : {f.rating}")
                print(f"Teater : {f.teater}")
                print(f"Jadwal : {', '.join(f.jadwal)}")
                print(f"Harga  : Rp{f.harga_tiket}")
            else:
                print(f" Film '{judul}' tidak ditemukan.")

        elif choice == '5':
            teater = input("Masukkan nama teater: ").strip()
            if teater in seat_manager.seat_status:
                total = seat_manager.get_total_available_seats(teater)
                if total > 0:
                    seats = seat_manager.get_available_seats(teater)
                    print(f"\n Kursi tersedia: {total}")
                    print("Contoh:", ', '.join(seat_manager.get_seat_name(i) for i in seats[:10]))
                else:
                    print(" Tidak ada kursi tersedia.")
            else:
                print(f" Teater '{teater}' tidak ditemukan.")

        elif choice == '6':
            judul = input("Judul film: ").strip()
            jam = input("Jam tayang (HH:MM): ").strip()
            try:
                jumlah = int(input("Jumlah tiket: "))
            except ValueError:
                print(" Jumlah tiket harus angka.")
                continue
            is_libur = input("Hari libur? (y/n): ").strip().lower() == 'y'
            is_member = input("Member? (y/n): ").strip().lower() == 'y'

            film = film_manager.cari("judul", judul)
            if not film:
                print(f" Film '{judul}' tidak ditemukan.")
                continue

            if jam not in film[0].jadwal:
                print(f" Jadwal '{jam}' tidak tersedia.")
                continue

            teater = film[0].teater
            if seat_manager.get_total_available_seats(teater) < jumlah:
                print(" Kursi tidak cukup.")
                continue

            kursi = seat_manager.assign_seat(teater, jumlah)
            if not kursi:
                print(" Gagal mengalokasikan kursi.")
                continue

            harga = calculator.get_price(judul, jam, is_libur, is_member)

            print("\n Tiket berhasil dipesan!")
            print(f" Film   : {judul}")
            print(f" Jam    : {jam}")
            print(f" Teater : {teater}")
            print(f" Kursi  : {', '.join(kursi)}")
            print(f" Total  : Rp{harga['total_harga']}")

        elif choice == '7':
            print("\n Mode Web (Swagger) sedang berjalan...")
            api_thread = threading.Thread(target=run_api_server, daemon=True)
            api_thread.start()
            input(" Tekan Enter untuk kembali ke menu CLI...")

        elif choice == '8':
            print("\n Terima kasih telah menggunakan AutoTicket. Sampai jumpa di pemesanan berikutnya!")
            break

        else:
            print(" Pilihan tidak valid. Silakan pilih antara 1 hingga 8.")

if __name__ == "__main__":
    main()