def show_film_list(facade):
    print("\n🎞 Daftar Film:")
    for film in facade.get_films():
        print(f"- {film.judul} | Genre: {film.genre} | Teater: {film.teater} | Harga: Rp{film.harga_tiket}")

def search_film_by_genre(facade):
    genre = input("Masukkan genre: ").strip().lower()
    if not genre:
        print("⚠️ Genre tidak boleh kosong.")
        return
    results = facade.get_films(genre=genre)
    if results:
        print(f"\n🎬 Film dengan genre '{genre}':")
        for film in results:
            print(f"- {film.judul}")
    else:
        print(f"⚠️ Tidak ada film dengan genre '{genre}'.")

def show_film_schedule(facade):
    film_title = input("Masukkan judul film: ").strip()
    if not film_title:
        print("⚠️ Judul film tidak boleh kosong.")
        return

    detail = facade.get_film_detail(film_title)
    if not detail.get("success", False):
        print(detail.get("message", "⚠️ Film tidak ditemukan."))
        return

    print(f"\n📅 Jadwal untuk film '{film_title}':")
    for time in detail.get("jadwal", []):
        print(f"- {time}")

def show_film_info(facade):
    film_title = input("Masukkan judul film: ").strip()
    if not film_title:
        print("⚠️ Judul film tidak boleh kosong.")
        return

    detail = facade.get_film_detail(film_title)
    if not detail.get("success", False):
        print(detail.get("message", "⚠️ Film tidak ditemukan."))
        return

    film = detail.get("film")
    print(f"\n🎬 Informasi Film:")
    print(f"Judul: {film.judul}")
    print(f"Genre: {film.genre}")
    print(f"Durasi: {film.durasi}")
    print(f"Rating: {film.rating}")
    print(f"Teater: {film.teater}")
    print(f"Harga Dasar: Rp{detail.get('harga_dasar', film.harga_tiket)}")
    print(f"Jadwal: {', '.join(film.jadwal)}")

def check_seat_availability(facade):
    film_title = input("Masukkan judul film (opsional, kosongkan untuk cek berdasarkan teater): ").strip()
    theater_name = None

    if not film_title:
        theater_name = input("Masukkan nama teater: ").strip()
        if not theater_name:
            print("⚠️ Harus memasukkan judul film atau nama teater.")
            return

    result = facade.check_seats(theater_name, film_title)

    if not result.get("success", False):
        print(result.get("message", "⚠️ Kursi tidak tersedia."))
        return

    print(f"\n💺 Informasi Ketersediaan Kursi di Teater {result.get('teater')}:")
    print(f"Total kursi tersedia: {result.get('total')}")
    print(f"Contoh kursi tersedia: {', '.join(result.get('contoh_kursi', []))}")

def book_ticket(facade):
    # Input data untuk pemesanan
    film_title = input("Masukkan judul film: ").strip()
    if not film_title:
        print("⚠️ Judul film tidak boleh kosong.")
        return

    # Dapatkan jadwal
    detail = facade.get_film_detail(film_title)
    if not detail.get("success", False):
        print(detail.get("message", "⚠️ Film tidak ditemukan."))
        return

    # Tampilkan jadwal dan minta pilihan
    print(f"\n📅 Jadwal untuk film '{film_title}':")
    for i, time in enumerate(detail.get("jadwal", []), 1):
        print(f"{i}. {time}")

    try:
        choice = int(input("\nPilih nomor jadwal: "))
        if choice < 1 or choice > len(detail.get("jadwal", [])):
            print("⚠️ Pilihan tidak valid.")
            return

        showtime = detail.get("jadwal", [])[choice-1]
    except ValueError:
        print("⚠️ Masukan harus berupa angka.")
        return

    # Input jumlah tiket
    try:
        ticket_count = int(input("Masukkan jumlah tiket: "))
        if ticket_count < 1:
            print("⚠️ Jumlah tiket harus minimal 1.")
            return
    except ValueError:
        print("⚠️ Masukan harus berupa angka.")
        return

    # Input preferensi tambahan
    is_holiday = input("Apakah hari libur? (y/n): ").strip().lower() == 'y'
    is_member = input("Apakah member? (y/n): ").strip().lower() == 'y'
    seat_pref = input("Preferensi kursi (berurutan/bebas): ").strip().lower()

    if seat_pref not in ["berurutan", "bebas"]:
        seat_pref = "berurutan"  # Default jika input tidak valid

    # Proses pemesanan
    result = facade.book_tickets(
        film_title,
        showtime,
        ticket_count,
        is_holiday,
        is_member,
        seat_pref
    )

    if not result.get("success", False):
        print(result.get("message", "⚠️ Gagal memesan tiket."))
        return

    # Tampilkan info pemesanan
    print("\n✅ Pemesanan Berhasil!")
    print(f"ID Reservasi: {result.get('reservation_id')}")
    print(f"Film: {result.get('film')}")
    print(f"Teater: {result.get('teater')}")
    print(f"Jadwal: {result.get('jadwal')}")
    print(f"Kursi: {', '.join(result.get('kursi', []))}")
    print(f"Total Harga: Rp{result.get('harga')}")
    print(f"Status: {result.get('status')}")
