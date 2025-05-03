# main.py

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
    print("7. Keluar")


def main():
    config = ConfigManager()
    config.load_config()

    film_service = FilmService(config)
    seat_manager = SeatManager(config)
    calculator = PriceCalculator(config)
    validator = TicketValidator(config)

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-7): ").strip()

        if pilihan == '1':
            print("\n📽️ Daftar Film:")
            for film in film_service.get_all_films():
                print(f"- {film['judul']} | Genre: {film['genre']} | Teater: {film['teater']} | Harga: Rp{film['harga_tiket']}")
        
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
            if seat_manager.get_total_available_seats(teater) > 0:
                seats = seat_manager.get_available_seats(teater)
                print(f"\n💺 Kursi tersedia di {teater}: {len(seats)} kursi")
                print("Contoh kursi tersedia:", ', '.join(seat_manager.get_seat_name(i) for i in seats[:10]))
            else:
                print(f"Tidak ada kursi tersedia di {teater}.")

        elif pilihan == '6':
            film_title = input("Judul film: ").strip()
            jam_tayang = input("Jam tayang (HH:MM): ").strip()
            jumlah_tiket = int(input("Jumlah tiket: "))
            is_libur = input("Apakah hari libur? (y/n): ").lower() == 'y'
            is_member = input("Apakah kamu member? (y/n): ").lower() == 'y'

            hasil = validator.validate_ticket_request(film_title, jam_tayang, jumlah_tiket)
            if not hasil["valid"]:
                print(hasil["message"])
                continue

            teater = hasil["teater"]
            kursi = seat_manager.assign_seat(teater, jumlah_tiket)
            if not kursi:
                print("❌ Tidak cukup kursi tersedia.")
                continue

            harga = calculator.get_price(film_title, jam_tayang, is_libur, is_member)

            print("\n✅ Tiket berhasil dipesan!")
            print(f"🎬 Film     : {film_title}")
            print(f"🕒 Jam      : {jam_tayang}")
            print(f"🏢 Teater   : {teater}")
            print(f"💺 Kursi    : {', '.join(kursi)}")
            print(f"💰 Total    : Rp{harga['total_harga']}")

        elif pilihan == '7':
            print("👋 Terima kasih telah menggunakan AutoTicket CLI.")
            break

        else:
            print("❌ Pilihan tidak valid. Silakan coba lagi.")


if __name__ == "__main__":
    main()
