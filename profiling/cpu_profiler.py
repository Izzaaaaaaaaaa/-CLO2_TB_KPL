# ======================================
# AutoTicket Profiling Tools
# ======================================
# File: profiling/cpu_profiler.py

import sys
import os
import cProfile
import pstats
import io
import time
from functools import wraps
from datetime import datetime
from prettytable import PrettyTable
import csv

# Tambahkan path root project ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Service.autoticket_facade import AutoTicketFacade

class CPUProfiler:
    def __init__(self):
        self.facade = AutoTicketFacade()
        self.results = []
        self.detailed_results = []

    def profile_cpu(self, func_name, iterations=1):
        """Decorator untuk CPU profiling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Setup profiler
                pr = cProfile.Profile()
                start_time = time.time()
                pr.enable()

                # Eksekusi fungsi
                result = func(*args, **kwargs)

                # Disable profiler
                pr.disable()
                end_time = time.time()

                # Simpan hasil profiling
                s = io.StringIO()
                sortby = 'cumulative'
                ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
                ps.print_stats(20)  # print 20 fungsi teratas

                # Parsing stats untuk detail fungsi
                function_stats = []
                detailed_output = s.getvalue()

                # Ambil baris-baris yang relevan (skip header)
                lines = detailed_output.split('\n')[5:]  # Skip 5 baris header
                for line in lines:
                    if line.strip() and not line.startswith('   '):  # Baris fungsi utama
                        try:
                            parts = line.strip().split()
                            if len(parts) >= 6:
                                # Format baris: ncalls tottime percall cumtime percall filename:lineno(function)
                                function_stats.append({
                                    'ncalls': parts[0],
                                    'tottime': float(parts[1]),
                                    'percall_tot': float(parts[2]) if len(parts) > 2 else 0,
                                    'cumtime': float(parts[3]) if len(parts) > 3 else 0,
                                    'percall_cum': float(parts[4]) if len(parts) > 4 else 0,
                                    'function': ' '.join(parts[5:])
                                })
                        except Exception as e:
                            # Skip baris yang tidak sesuai format dan log error
                            print(f"⚠️ Error parsing line: {line} - {str(e)}")
                            continue

                # Menyimpan metrik utama
                total_time = end_time - start_time
                self.results.append({
                    'fungsi': func_name,
                    'iterasi': iterations,
                    'waktu_total': round(total_time, 4),
                    'waktu_per_operasi': round(total_time / iterations, 6) if iterations > 0 else 0,
                    'jumlah_fungsi_dipanggil': len(function_stats),
                    'hasil': result
                })

                # Menyimpan detail fungsi yang dipanggil
                for stat in function_stats[:10]:  # Simpan 10 fungsi teratas saja
                    self.detailed_results.append({
                        'operasi_utama': func_name,
                        'fungsi': stat['function'],
                        'panggilan': stat['ncalls'],
                        'waktu_total': stat['tottime'],
                        'waktu_kumulatif': stat['cumtime'],
                        'waktu_per_panggilan': stat['percall_tot']
                    })

                print(f"✅ CPU Profiling '{func_name}' selesai: {total_time:.4f} s")
                return result
            return wrapper
        return decorator

    @property
    def hotspots(self):
        """Mengembalikan 10 fungsi teratas berdasarkan waktu kumulatif"""
        if not self.detailed_results:
            return []

        # Urutkan berdasarkan waktu kumulatif
        sorted_results = sorted(self.detailed_results,
                                key=lambda x: x['waktu_kumulatif'],
                                reverse=True)
        return sorted_results[:10]

    def profile_booking_flow(self, iterations=20):
        """Profiling seluruh alur pemesanan tiket"""
        print("🎫 Profiling alur pemesanan tiket...")

        @self.profile_cpu("booking_flow", iterations)
        def _profile():
            success_count = 0
            # Simulasi pemesanan
            for i in range(iterations):
                try:  # Perbaikan indentasi di sini
                    # 1. Dapatkan film
                    films = self.facade.get_films()
                    if not films:
                        continue

                    film_title = films[i % len(films)].judul

                    # 2. Dapatkan detail film
                    film_detail = self.facade.get_film_detail(film_title)
                    if not film_detail["success"]:
                        continue

                    # 3. Ambil jadwal
                    if not film_detail["film"].jadwal:
                        continue
                    showtime = film_detail["film"].jadwal[0]

                    # 4. Cek kursi
                    seat_check = self.facade.check_seats(film_title=film_title)

                    # 5. Hitung harga
                    price_info = self.facade.calculate_ticket_price(
                        film_title, showtime,
                        is_holiday=(i % 2 == 0),
                        is_member=(i % 3 == 0),
                        ticket_count=((i % 3) + 1)
                    )

                    # 6. Pesan tiket
                    booking = self.facade.book_tickets(
                        film_title, showtime,
                        ((i % 3) + 1),
                        is_holiday=(i % 2 == 0),
                        is_member=(i % 3 == 0),
                        seat_preference="berurutan" if i % 2 == 0 else "bebas"
                    )

                    if booking.get("success", False):
                        success_count += 1
                except Exception as e:
                    print(f"⚠️ Error dalam simulasi pemesanan: {str(e)}")

            return success_count

        return _profile()

    def profile_api_endpoints(self, iterations=20):
        """Profiling CPU untuk simulasi panggilan API endpoint"""
        print("🌐 Profiling API endpoints...")

        @self.profile_cpu("api_endpoints", iterations)
        def _profile():
            try:
                # Import di sini untuk menghindari ImportError jika FastAPI tidak tersedia
                from fastapi.testclient import TestClient

                # Import aplikasi API - perlu memastikan modul ini tersedia
                try:
                    from api import app
                except ImportError:
                    print("⚠️ Module api.py tidak ditemukan. Pastikan file sudah dibuat.")
                    return {'error': 'API module tidak tersedia'}

                client = TestClient(app)

                response_times = {
                    'root': 0,
                    'films': 0,
                    'film_detail': 0,
                    'showtimes': 0,
                    'price': 0,
                    'seats': 0,
                    'book': 0
                }

                # Simulasi permintaan API
                for i in range(iterations):
                    try:
                        # GET endpoints
                        start = time.time()
                        client.get("/")
                        response_times['root'] += time.time() - start

                        start = time.time()
                        client.get("/films")
                        response_times['films'] += time.time() - start

                        start = time.time()
                        client.get("/films/Avengers: Endgame")
                        response_times['film_detail'] += time.time() - start

                        start = time.time()
                        client.get("/films/Spider-Man: No Way Home/showtimes")
                        response_times['showtimes'] += time.time() - start

                        start = time.time()
                        client.get("/films/F9: The Fast Saga/price?showtime=19:30&is_holiday=true&is_member=true")
                        response_times['price'] += time.time() - start

                        start = time.time()
                        client.get("/seats/Teater 1")
                        response_times['seats'] += time.time() - start

                        # POST endpoint
                        if i % 5 == 0:  # Lakukan pemesanan hanya setiap 5 iterasi
                            payload = {
                                "film_title": "The Lion King",
                                "showtime": "09:30",
                                "ticket_count": 2,
                                "is_holiday": i % 2 == 0,
                                "is_member": i % 3 == 0,
                                "seat_preference": "berurutan"
                            }

                            start = time.time()
                            client.post("/book", json=payload)
                            response_times['book'] += time.time() - start
                    except Exception as e:
                        print(f"⚠️ Error dalam API request: {str(e)}")

                # Hitung rata-rata waktu respons
                for key in response_times:
                    divisor = iterations
                    if key == 'book':
                        divisor = max(iterations // 5, 1)  # Book hanya setiap 5 iterasi
                    response_times[key] = response_times[key] / divisor

                return response_times

            except ImportError as e:
                print(f"⚠️ Error dalam testing API endpoints: {e}")
                print("Pastikan FastAPI dan dependencies terkait sudah diinstall:")
                print("pip install fastapi uvicorn")
                return {'error': str(e)}

        return _profile()

    def profile_get_films(self, iterations=100):
        """Profiling fungsi get_films"""
        print("🎬 Profiling get_films...")

        @self.profile_cpu("get_films", iterations)
        def _profile():
            results_count = 0
            try:
                for _ in range(iterations):
                    films = self.facade.get_films()
                    results_count = len(films)
                return results_count
            except Exception as e:
                print(f"⚠️ Error dalam profile_get_films: {str(e)}")
                return 0

        return _profile()

    def profile_calculate_price(self, iterations=100):
        """Profiling perhitungan harga"""
        print("💰 Profiling calculate_ticket_price...")

        @self.profile_cpu("calculate_ticket_price", iterations)
        def _profile():
            success_count = 0
            try:
                for _ in range(iterations):
                    result = self.facade.calculate_ticket_price(
                        "Avengers: Endgame", "10:00",
                        is_holiday=True, is_member=True, ticket_count=2
                    )
                    if result.get("success", False):
                        success_count += 1
                return success_count
            except Exception as e:
                print(f"⚠️ Error dalam profile_calculate_price: {str(e)}")
                return 0

        return _profile()

    def display_results(self):
        """Menampilkan hasil profiling dalam bentuk tabel"""
        if not self.results:
            print("❌ Tidak ada hasil profiling untuk ditampilkan")
            return

        print("\n" + "="*80)
        print("📊 HASIL CPU PROFILING (OPERASI UTAMA)".center(80))
        print("="*80)

        table = PrettyTable()
        table.field_names = [
            "Fungsi", "Iterasi", "Waktu Total (s)",
            "Waktu/Op (s)", "Jumlah Fungsi", "Hasil"
        ]

        # Atur lebar kolom dan perataan
        table.max_width["Fungsi"] = 25
        table.max_width["Hasil"] = 30
        table.align["Fungsi"] = "l"
        table.align["Hasil"] = "l"
        table.align["Waktu Total (s)"] = "r"
        table.align["Waktu/Op (s)"] = "r"

        for result in self.results:
            # Format hasil agar tidak terlalu panjang
            hasil_str = str(result['hasil'])
            if len(hasil_str) > 30:
                hasil_str = hasil_str[:27] + "..."

            table.add_row([
                result['fungsi'],
                result['iterasi'],
                round(result['waktu_total'], 6),
                round(result['waktu_per_operasi'], 6),
                result['jumlah_fungsi_dipanggil'],
                hasil_str
            ])

        print(table)

        # Tampilkan CPU hotspots
        print("\n" + "="*80)
        print("🔥 CPU HOTSPOTS (10 TERATAS)".center(80))
        print("="*80)

        if self.hotspots:
            hotspot_table = PrettyTable()
            hotspot_table.field_names = [
                "Fungsi", "Panggilan", "Waktu Total (s)",
                "Waktu Kumulatif (s)", "Waktu/Panggilan (s)"
            ]

            # Atur lebar kolom dan perataan
            hotspot_table.max_width["Fungsi"] = 40
            hotspot_table.align["Fungsi"] = "l"
            hotspot_table.align["Waktu Total (s)"] = "r"
            hotspot_table.align["Waktu Kumulatif (s)"] = "r"
            hotspot_table.align["Waktu/Panggilan (s)"] = "r"

            for hotspot in self.hotspots:
                fungsi_nama = hotspot['fungsi']
                if len(fungsi_nama) > 40:
                    fungsi_nama = fungsi_nama[:37] + "..."

                hotspot_table.add_row([
                    fungsi_nama,
                    hotspot['panggilan'],
                    round(hotspot['waktu_total'], 6),
                    round(hotspot['waktu_kumulatif'], 6),
                    round(hotspot['waktu_per_panggilan'], 6),
                ])

            print(hotspot_table)
        else:
            print("Tidak ada data hotspot tersedia")

    def save_results_to_csv(self):
        """Menyimpan hasil profiling ke CSV"""
        if not self.results:
            print("❌ Tidak ada hasil profiling untuk disimpan")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Simpan hasil utama
        main_filename = f"cpu_profiling_main_{timestamp}.csv"
        with open(main_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.results[0].keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

        # Simpan hasil detail
        detail_filename = f"cpu_profiling_detail_{timestamp}.csv"  # Perbaikan format string di sini
        if self.detailed_results:
            with open(detail_filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.detailed_results[0].keys())
                writer.writeheader()
                for result in self.detailed_results:
                    writer.writerow(result)

            print(f"✅ Hasil profiling disimpan ke {main_filename} dan {detail_filename}")
        else:
            print(f"✅ Hasil profiling utama disimpan ke {main_filename}")
            print("⚠️ Tidak ada hasil detail untuk disimpan")

    def run_all_profiles(self):
        """Menjalankan semua profil CPU"""
        print("\n" + "="*80)
        print("🚀 MEMULAI CPU PROFILING".center(80))
        print("="*80 + "\n")

        try:
            # Menjalankan profiling untuk operasi dasar
            self.profile_get_films()
            self.profile_calculate_price()

            # Menjalankan profiling untuk alur lengkap
            self.profile_booking_flow()

            # Jalankan profiling API jika FastAPI tersedia
            try:
                from fastapi.testclient import TestClient
                self.profile_api_endpoints()
            except ImportError:
                print("⚠️ FastAPI test client tidak tersedia, melewati profiling API endpoints")
                print("Untuk mengaktifkan API profiling, install: pip install fastapi uvicorn")

            # Menampilkan dan menyimpan hasil
            self.display_results()
            self.save_results_to_csv()

        except Exception as e:
            print(f"❌ Error saat menjalankan profiling: {str(e)}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*80)
        print("🏁 CPU PROFILING SELESAI".center(80))
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

    profiler = CPUProfiler()
    profiler.run_all_profiles()
