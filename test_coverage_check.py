# test_coverage_check.py
# Script sederhana untuk menampilkan coverage report per file

import coverage
import unittest

def print_coverage_report():
    # Inisialisasi coverage
    cov = coverage.Coverage()
    cov.start()

    # Jalankan semua unit test yang ada di folder 'test'
    loader = unittest.TestLoader()
    tests = loader.discover('test')   # pastikan folder test kamu namanya 'test'
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(tests)

    # Stop coverage dan tampilkan report
    cov.stop()
    cov.save()

    print("\n========== COVERAGE REPORT ==========")
    cov.report(show_missing=True)
    print("=====================================\n")

    # Optional: kalau mau simpan juga ke file html (bisa dibuka di browser)
    cov.html_report(directory='htmlcov')
    print("HTML report generated in htmlcov/index.html")

if __name__ == "__main__":
    print_coverage_report()
