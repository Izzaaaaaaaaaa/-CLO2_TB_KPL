# main.py

import os
import uvicorn
import webbrowser
from Config.Config_manager import ConfigManager
from Service.film_service import FilmService
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator


def tampilkan_menu():
    print("\n===== 🎟️ AutoTicket CLI =====")
    print("1. Lihat daftar film")
    print("2. Cari film berdasarkan genre")
    print("3. Lihat jadwal film")
    print("4. Lihat informasi film lengkap")
    print("5. Cek ketersediaan kursi")
    print("6. Pesan tiket")
    print("7. Jalankan API (Web Mode)")
    print("8. Keluar")


def start_api_server():
    """Menjalankan server API FastAPI"""
    print("\n🚀 Memulai server API...")
    print("Server API berjalan di http://localhost:8000")
    print("Dokumentasi API tersedia di http://localhost:8000/docs")
    print("\nTekan Ctrl+C di terminal ini untuk menghentikan server.")

    # Membuka browser secara otomatis ke dokumentasi API
    webbrowser.open('http://localhost:8000/docs')

    try:
        # Jalankan server API
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n⏹️ Server API dihentikan.")
    except Exception as e:
        print(f"\n❌ Error saat menjalankan server API: {str(e)}")


def main():
    config = ConfigManager()
    config.load_config()

    film_service = FilmService(config)
    seat_manager = SeatManager(config)
    calculator = PriceCalculator(config)
    validator = TicketValidator(config)

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-8): ").strip()

        if pilihan == '1':
            print("\n🎞️ Daftar Film:")
            for film in film_service.get_all_films():
                print(
                    f"- {film['judul']} | Genre: {film['genre']} | Teater: {film['teater']} | Harga: Rp{film['harga_tiket']}")

        elif pilihan == '2':
            genre = input("Masukkan genre (contoh: Action, Drama, Sci-Fi): ").strip()
            hasil = film_service.get_film_by_genre(genre)
            if hasil:
                print(f"\n🎬 Film dengan genre '{genre}':")
                for film in hasil:
                    print(f"- {film['judul']}")
            else:
                print(f"Tidak ada film dengan genre '{genre}'.")

        elif pilihan == '3':
            film_title = input("Masukkan judul film: ").strip()
            jadwal = film_service.get_film_schedule(film_title)
            if jadwal:
                print(f"\n🕒 Jadwal tayang untuk {film_title}: {', '.join(jadwal)}")
            else:
                print(f"Tidak ditemukan jadwal untuk '{film_title}'.")

        elif pilihan == '4':
            film_title = input("Masukkan judul film: ").strip()
            film = film_service.get_film_info(film_title)
            if film:
                print(f"\n📋 Informasi lengkap film '{film_title}':")
                print(f"Genre   : {film['genre']}")
                print(f"Durasi  : {film['durasi']}")
                print(f"Rating  : {film['rating']}")
                print(f"Teater  : {film['teater']}")
                print(f"Jadwal  : {', '.join(film['jadwal'])}")
                print(f"Harga   : Rp{film['harga_tiket']}")
            else:
                print(f"Film '{film_title}' tidak ditemukan.")

        elif pilihan == '5':
            teater = input("Masukkan nama teater (contoh: Teater 1): ").strip()
            if teater in seat_manager.seat_status:
                available_count = seat_manager.get_total_available_seats(teater)
                if available_count > 0:
                    seats = seat_manager.get_available_seats(teater)
                    print(f"\n💺 Kursi tersedia di {teater}: {available_count} kursi")
                    print("Contoh kursi tersedia:", ', '.join(seat_manager.get_seat_name(i) for i in seats[:10]))
                else:
                    print(f"Tidak ada kursi tersedia di {teater}.")
            else:
                print(f"Teater '{teater}' tidak ditemukan.")

        elif pilihan == '6':
            film_title = input("Judul film: ").strip()
            jam_tayang = input("Jam tayang (HH:MM): ").strip()
            jumlah_tiket = input("Jumlah tiket: ").strip()

            # Validasi input jumlah tiket
            try:
                jumlah_tiket = int(jumlah_tiket)
            except ValueError:
                print("❌ Jumlah tiket harus berupa angka.")
                continue

            is_libur = input("Apakah hari libur? (y/n): ").lower() == 'y'
            is_member = input("Apakah kamu member? (y/n): ").lower() == 'y'

            if not validator.is_valid_film(film_title):
                print(f"❌ Film '{film_title}' tidak ditemukan.")
                continue

            if not validator.is_valid_showtime(film_title, jam_tayang):
                print(f"❌ Jadwal '{jam_tayang}' tidak tersedia untuk film '{film_title}'.")
                continue

            # Dapatkan teater untuk film ini
            film_info = film_service.get_film_info(film_title)
            teater = film_info.get("teater", "")

            if not teater:
                print("❌ Informasi teater tidak ditemukan.")
                continue

            # Cek ketersediaan kursi
            if seat_manager.get_total_available_seats(teater) < jumlah_tiket:
                print(f"❌ Tidak cukup kursi tersedia di {teater}.")
                continue

            # Alokasi kursi
            kursi = seat_manager.assign_seats(teater, jumlah_tiket)
            if not kursi:
                print("❌ Gagal mengalokasikan kursi.")
                continue

            # Hitung harga
            harga = calculator.get_price(film_title, jam_tayang, is_libur, is_member)

            print("\n✅ Tiket berhasil dipesan!")
            print(f"🎬 Film     : {film_title}")
            print(f"🕒 Jam      : {jam_tayang}")
            print(f"🏢 Teater   : {teater}")
            print(f"💺 Kursi    : {', '.join(kursi)}")
            print(f"💰 Total    : Rp{harga['total_harga']}")

        elif pilihan == '7':
            start_api_server()

        elif pilihan == '8':
            print("👋 Terima kasih telah menggunakan AutoTicket CLI.")
            break

        else:
            print("❌ Pilihan tidak valid. Silakan coba lagi.")


if __name__ == "__main__":
    main()
