import os
import threading
import webbrowser
import uvicorn
from Service.autoticket_facade import AutoTicketFacade
from api import app
from env_loader import get_env

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
    # Menggunakan variabel lingkungan dari .env
    api_host = get_env("API_HOST", "127.0.0.1")
    api_port = int(get_env("API_PORT", "8000"))
    api_docs_url = get_env("API_DOCS_URL", "http://localhost:8000/docs")
    
    print(f"\n🚀 Memulai server API di http://{api_host}:{api_port}")
    webbrowser.open(api_docs_url)
    uvicorn.run(app, host=api_host, port=api_port)

def show_film_list(facade):
    print("\n🎞 Daftar Film:")
    for film in facade.get_films():
        print(f"- {film.judul} | Genre: {film.genre} | Teater: {film.teater} | Harga: Rp{film.harga_tiket}")

def search_film_by_genre(facade):
    while True:
        genre = input("Masukkan genre: ").strip().lower()
        if not genre:
            print("⚠️ Genre tidak boleh kosong. Silakan coba lagi.")
            continue

        results = facade.get_films(genre=genre)
        if results:
            print(f"\n🎬 Film dengan genre '{genre}':")
            for film in results:
                print(f"- {film.judul}")
        else:
            print(f"⚠️ Tidak ada film dengan genre '{genre}'.")
        break  # keluar dari loop setelah satu pencarian berhasil (ditemukan atau tidak)


def show_film_schedule(facade):
    while True:
        title = input("Masukkan judul film: ").strip()
        if not title:
            print("⚠️ Judul film tidak boleh kosong. Silakan coba lagi.")
            continue

        result = facade.get_film_detail(title)
        if result["success"]:
            film = result["film"]
            print(f"\n🕒 Jadwal tayang untuk {film.judul}: {', '.join(film.jadwal)}")
        else:
            print(f"⚠️ {result['message']}")
        break


def show_film_info(facade):
    while True:
        title = input("Masukkan judul film: ").strip()
        if not title:
            print("⚠️ Judul film tidak boleh kosong. Silakan coba lagi.")
            continue

        result = facade.get_film_detail(title)
        if result["success"]:
            film = result["film"]
            print(f"\n📋 Informasi lengkap film '{film.judul}':")
            print(f"Genre  : {film.genre}")
            print(f"Durasi : {film.durasi}")
            print(f"Rating : {film.rating}")
            print(f"Teater : {film.teater}")
            print(f"Jadwal : {', '.join(film.jadwal)}")
            print(f"Harga  : Rp{film.harga_tiket}")
        else:
            print(f"⚠️ {result['message']}")
        break


def check_seat_availability(facade):
    choice = input("Cek berdasarkan teater (1) atau film (2)? ").strip()

    if choice not in ["1", "2"]:
        print("⚠️ Pilihan tidak valid. Harap masukkan angka 1 untuk teater atau 2 untuk film.")
        return

    if choice == "1":
        theater = input("Masukkan nama teater: ").strip()
        if not theater:
            print("⚠️ Nama teater tidak boleh kosong.")
            return
        result = facade.check_seats(theater_name=theater)

    elif choice == "2":
        film = input("Masukkan judul film: ").strip()
        if not film:
            print("⚠️ Judul film tidak boleh kosong.")
            return
        result = facade.check_seats(film_title=film)

    if result["success"]:
        print(f"\n💺 Kursi tersedia di {result['teater']}: {result['total']}")
        print("Contoh kursi:", ', '.join(result['contoh_kursi']))
    else:
        print(f"⚠️ {result['message']}")


def book_ticket(facade):
    try:
        title = input("Judul film: ").strip()
        if not title:
            print("⚠️ Judul film tidak boleh kosong.")
            return

        # 🔍 Tampilkan jadwal otomatis saat input judul
        result = facade.get_film_detail(title)
        if result["success"]:
            film = result["film"]
            print(f"🕒 Jadwal tayang untuk {film.judul}: {', '.join(film.jadwal)}")
        else:
            print(f"⚠️ {result['message']}")
            return

        showtime = input("Jam tayang (HH:MM): ").strip()
        if not showtime:
            print("⚠️ Jam tayang tidak boleh kosong.")
            return

        ticket_input = input("Jumlah tiket: ").strip()
        if not ticket_input:
            print("⚠️ Jumlah tiket tidak boleh kosong.")
            return
        if not ticket_input.isdigit():
            print("⚠️ Jumlah tiket harus angka.")
            return

        ticket_count = int(ticket_input)

        is_holiday = input("Hari libur? (y/n): ").strip().lower() == 'y'
        is_member = input("Member? (y/n): ").strip().lower() == 'y'
        seat_pref = input("Preferensi kursi (berurutan/bebas): ").strip().lower()

        if seat_pref not in ["berurutan", "bebas"]:
            seat_pref = "berurutan"  # Default jika input tidak valid

        # Gunakan metode terpadu dari facade
        result = facade.book_tickets(
            title, showtime, ticket_count, is_holiday, is_member, seat_pref
        )

        if result["success"]:
            print("\n✅ Tiket berhasil dipesan!")
            print(f"🎫 ID Reservasi: {result['reservation_id']}")
            print(f"🎬 Film   : {result['film']}")
            print(f"🕒 Jam    : {result['jadwal']}")
            print(f"🏢 Teater : {result['teater']}")
            print(f"💺 Kursi  : {', '.join(result['kursi'])}")
            print(f"💰 Total  : Rp{result['harga']}")
        else:
            print(f"⚠️ {result['message']}")

    except Exception as e:
        print(f"⚠️ Terjadi kesalahan: {str(e)}")

def run_api():
    print("\n🌐 Mode Web (Swagger) sedang berjalan...")
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    input("🔙 Tekan Enter untuk kembali ke menu CLI...")

def main():
    # Inisialisasi facade - satu-satunya titik kontak dengan sistem
    facade = AutoTicketFacade()

    while True:
        display_menu()
        choice = input("Masukkan pilihan Anda (1-8): ").strip()

        menu_handlers = {
            '1': lambda: show_film_list(facade),
            '2': lambda: search_film_by_genre(facade),
            '3': lambda: show_film_schedule(facade),
            '4': lambda: show_film_info(facade),
            '5': lambda: check_seat_availability(facade),
            '6': lambda: book_ticket(facade),
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