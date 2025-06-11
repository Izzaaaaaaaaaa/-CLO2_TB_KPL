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
