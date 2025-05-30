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

def run_api_server():
    print("\n🚀 Memulai server API di http://localhost:8000")
    webbrowser.open('http://localhost:8000/docs')
    uvicorn.run(app, host="127.0.0.1", port=8000)

def show_film_list(film_manager):
    print("\n🎞 Daftar Film:")
    for film in film_manager.ambil_semua():
        print(f"- {film.judul} | Genre: {film.genre} | Teater: {film.teater} | Harga: Rp{film.harga_tiket}")

def search_film_by_genre(film_manager):
    genre = input("Masukkan genre: ").strip().lower()
    results = [f for f in film_manager.ambil_semua() if genre in f.genre.lower()]
    if results:
        print(f"\n🎬 Film dengan genre '{genre}':")
        for film in results:
            print(f"- {film.judul}")
    else:
        print(f"⚠️ Tidak ada film dengan genre '{genre}'.")

def show_film_schedule(film_manager):
    title = input("Masukkan judul film: ").strip()
    film = film_manager.cari("judul", title)
    if film:
        print(f"\n🕒 Jadwal tayang untuk {title}: {', '.join(film[0].jadwal)}")
    else:
        print(f"⚠️ Tidak ada jadwal untuk film '{title}'.")

def show_film_info(film_manager):
    title = input("Masukkan judul film: ").strip()
    film = film_manager.cari("judul", title)
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
        print(f"⚠️ Film '{title}' tidak ditemukan.")

def check_seat_availability(seat_manager):
    theater = input("Masukkan nama teater: ").strip()
    if theater in seat_manager.seat_status:
        total = seat_manager.get_total_available_seats(theater)
        if total > 0:
            seats = seat_manager.get_available_seats(theater)
            print(f"\n💺 Kursi tersedia: {total}")
            print("Contoh:", ', '.join(seat_manager.get_seat_name(i) for i in seats[:10]))
        else:
            print("⚠️ Tidak ada kursi tersedia.")
    else:
        print(f"⚠️ Teater '{theater}' tidak ditemukan.")

def book_ticket(film_manager, seat_manager, calculator, validator):
    try:
        title = input("Judul film: ").strip()
        showtime = input("Jam tayang (HH:MM): ").strip()
        ticket_count = int(input("Jumlah tiket: "))
        is_holiday = input("Hari libur? (y/n): ").strip().lower() == 'y'
        is_member = input("Member? (y/n): ").strip().lower() == 'y'

        film = film_manager.cari("judul", title)
        if not film:
            print(f"⚠️ Film '{title}' tidak ditemukan.")
            return
        if showtime not in film[0].jadwal:
            print(f"⚠️ Jadwal '{showtime}' tidak tersedia.")
            return
        theater = film[0].teater
        if seat_manager.get_total_available_seats(theater) < ticket_count:
            print("⚠️ Kursi tidak cukup.")
            return
        seats = seat_manager.assign_seat(theater, ticket_count)
        if not seats:
            print("⚠️ Gagal mengalokasikan kursi.")
            return

        # Pass ticket count to get_price
        price = calculator.get_price(title, showtime, is_holiday, is_member, ticket_count)

        print("\n✅ Tiket berhasil dipesan!")
        print(f"🎬 Film   : {title}")
        print(f"🕒 Jam    : {showtime}")
        print(f"🏢 Teater : {theater}")
        print(f"💺 Kursi  : {', '.join(seats)}")
        print(f"💰 Total  : Rp{price['total_harga']}")
    except ValueError:
        print("⚠️ Jumlah tiket harus angka.")
    except Exception as e:
        print(f"⚠️ Terjadi kesalahan: {str(e)}")

def run_api():
    print("\n🌐 Mode Web (Swagger) sedang berjalan...")
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    input("🔙 Tekan Enter untuk kembali ke menu CLI...")

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

        menu_handlers = {
            '1': lambda: show_film_list(film_manager),
            '2': lambda: search_film_by_genre(film_manager),
            '3': lambda: show_film_schedule(film_manager),
            '4': lambda: show_film_info(film_manager),
            '5': lambda: check_seat_availability(seat_manager),
            '6': lambda: book_ticket(film_manager, seat_manager, calculator, validator),
            '7': run_api,
            '8': lambda: print("\n🙏 Terima kasih telah menggunakan AutoTicket. Sampai jumpa di pemesanan berikutnya!")
        }

        if choice in menu_handlers:
            if choice == '8':
                menu_handlers[choice]()
                break
            menu_handlers[choice]()
        else:
            print("⚠️ Pilihan tidak valid. Silakan pilih antara 1 hingga 8.")

if __name__ == "__main__":
    main()
