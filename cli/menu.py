from cli.actions import (
    show_film_list,
    search_film_by_genre,
    show_film_schedule,
    show_film_info,
    check_seat_availability,
    book_ticket,
)
from cli.api_runner import run_api
from Service.autoticket_facade import AutoTicketFacade

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

def start_cli():
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
