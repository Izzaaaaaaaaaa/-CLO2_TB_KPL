# ======================================
# AutoTicket Profiling Tools
# ======================================
# File: profiling/memory_profiler.py

import sys
import os
import memory_profiler
import time
from functools import wraps
from prettytable import PrettyTable
import csv
from datetime import datetime

# Tambahkan path root project ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Service.autoticket_facade import AutoTicketFacade
from Config.Config_manager import ConfigManager

class MemoryProfiler:
    def __init__(self):
        self.facade = AutoTicketFacade()
        self.results = []

    def profile_memory(self, func_name, iterations=100):
        """Decorator untuk mengukur penggunaan memori"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Mengukur penggunaan memori sebelum eksekusi
                start_time = time.time()
                mem_before = memory_profiler.memory_usage()[0]

                # Eksekusi fungsi
                result = func(*args, **kwargs)

                # Mengukur penggunaan memori setelah eksekusi
                end_time = time.time()
                mem_after = memory_profiler.memory_usage()[0]

                # Menghitung metrik
                mem_used = mem_after - mem_before
                exec_time = end_time - start_time
                mem_per_op = mem_used / iterations if iterations > 0 else 0
                time_per_op = exec_time / iterations if iterations > 0 else 0

                # Menyimpan hasil
                self.results.append({
                    'fungsi': func_name,
                    'iterasi': iterations,
                    'waktu_total': round(exec_time, 4),
                    'waktu_per_operasi': round(time_per_op, 6),
                    'memori_total': round(mem_used, 4),
                    'memori_per_operasi': round(mem_per_op, 6),
                    'hasil': result
                })

                print(f"✅ Profiling '{func_name}' selesai: +{mem_used:.4f} MiB ({exec_time:.4f} s)")
                return result
            return wrapper
        return decorator

    def profile_film_list(self, iterations=100):
        """Profiling daftar film"""
        print("🎬 Profiling mendapatkan daftar film...")

        @self.profile_memory("get_films", iterations)
        def _profile():
            for _ in range(iterations):
                films = self.facade.get_films()
            return len(films)

        return _profile()

    def profile_search_by_genre(self, genre="Action", iterations=100):
        """Profiling pencarian berdasarkan genre"""
        print(f"🔍 Profiling pencarian film genre {genre}...")

        @self.profile_memory(f"get_films_by_genre_{genre}", iterations)
        def _profile():
            for _ in range(iterations):
                films = self.facade.get_films(genre=genre)
            return len(films)

        return _profile()

    def profile_seat_allocation(self, film_title="Avengers: Endgame", iterations=20):
        """Profiling alokasi kursi"""
        print(f"💺 Profiling alokasi kursi untuk film {film_title}...")

        film_detail = self.facade.get_film_detail(film_title)
        if not film_detail["success"]:
            print("⚠️ Film tidak ditemukan")
            return 0

        teater = film_detail["film"].teater

        @self.profile_memory("assign_seat", iterations)
        def _profile():
            for _ in range(iterations):
                result = self.facade._seat_manager.assign_seat(teater, 2, prefer_consecutive=True)
                # Reset status kursi setelah setiap alokasi untuk simulasi
                self.facade._seat_manager.seat_status[teater] = [True] * self.facade._config.get_max_kursi()
            return 1 if result else 0

        return _profile()

    def profile_price_calculation(self, iterations=50):
        """Profiling perhitungan harga"""
        print("💰 Profiling perhitungan harga tiket...")

        @self.profile_memory("calculate_ticket_price", iterations)
        def _profile():
            for _ in range(iterations):
                self.facade.calculate_ticket_price(
                    "Avengers: Endgame", "10:00",
                    is_holiday=True, is_member=True, ticket_count=2
                )
            return 1

        return _profile()

    def profile_booking_flow(self, iterations=10):
        """Profiling alur pemesanan lengkap"""
        print("🎫 Profiling alur pemesanan lengkap...")

        @self.profile_memory("booking_flow", iterations)
        def _profile():
            success_count = 0
            for i in range(iterations):
                # Get film list
                films = self.facade.get_films()
                film_title = films[i % len(films)].judul

                # Get film detail
                detail = self.facade.get_film_detail(film_title)
                if not detail["success"]:
                    continue

                showtime = detail["film"].jadwal[0]

                # Check seats
                result = self.facade.check_seats(film_title=film_title)

                # Book tickets
                booking = self.facade.book_tickets(
                    film_title, showtime, 2,
                    is_holiday=(i % 2 == 0),
                    is_member=True,
                    seat_preference="berurutan"
                )

                if booking.get("success", False):
                    success_count += 1

            return success_count

        return _profile()

    def display_results(self):
        """Menampilkan hasil profiling dalam bentuk tabel"""
        if not self.results:
            print("❌ Tidak ada hasil profiling untuk ditampilkan")
            return

        print("\n" + "="*80)
        print("📊 HASIL MEMORY PROFILING".center(80))
        print("="*80)

        table = PrettyTable()
        table.field_names = [
            "Fungsi", "Iterasi", "Waktu Total (s)",
            "Waktu/Op (s)", "Memory Total (MiB)",
            "Memory/Op (MiB)", "Hasil"
        ]

        for result in self.results:
            table.add_row([
                result['fungsi'],
                result['iterasi'],
                result['waktu_total'],
                result['waktu_per_operasi'],
                result['memori_total'],
                result['memori_per_operasi'],
                result['hasil']
            ])

        print(table)

    def save_results_to_csv(self):
        """Menyimpan hasil profiling ke CSV"""
        if not self.results:
            print("❌ Tidak ada hasil profiling untuk disimpan")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_profiling_{timestamp}.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.results[0].keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

        print(f"✅ Hasil profiling disimpan ke {filename}")

    def run_all_profiles(self):
        """Menjalankan semua profil memori"""
        print("\n" + "="*80)
        print("🚀 MEMULAI MEMORY PROFILING".center(80))
        print("="*80 + "\n")

        # Menjalankan profiling untuk semua operasi
        self.profile_film_list()
        self.profile_search_by_genre("Action")
        self.profile_search_by_genre("Drama")
        self.profile_seat_allocation()
        self.profile_price_calculation()
        self.profile_booking_flow()

        # Menampilkan dan menyimpan hasil
        self.display_results()
        self.save_results_to_csv()

        print("\n" + "="*80)
        print("🏁 MEMORY PROFILING SELESAI".center(80))
        print("="*80)

        return self.results

if __name__ == "__main__":
    try:
        # Memastikan module yang dibutuhkan tersedia
        import prettytable
    except ImportError:
        print("⚠️ Module prettytable tidak ditemukan. Menginstal...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "prettytable"])

    profiler = MemoryProfiler()
    profiler.run_all_profiles()
