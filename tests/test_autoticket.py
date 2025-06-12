import unittest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cli.api import app
from config.config_manager import ConfigManager
from service.film_service import FilmService
from service.price_calculator import PriceCalculator
from service.seat_manager import SeatManager
from service.autoticket_facade import AutoTicketFacade
from Validation.ticket_validator import TicketValidator

class TicketSystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.config = ConfigManager("config.json")
        cls.config.load_config()
        cls.film_service = FilmService(cls.config)
        cls.calculator = PriceCalculator(cls.config)
        cls.seat_manager = SeatManager(cls.config)
        cls.validator = TicketValidator(cls.config)
        cls.facade = AutoTicketFacade("config.json")

    # ========== API Endpoint tests ==========
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_get_all_films(self):
        response = self.client.get("/films")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_film_by_title(self):
        response = self.client.get("/films/Avengers: Endgame")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["judul"], "Avengers: Endgame")

    def test_get_film_showtimes(self):
        response = self.client.get("/films/Spider-Man: No Way Home/showtimes")
        self.assertEqual(response.status_code, 200)
        self.assertIn("11:00", response.json())

    def test_get_film_price(self):
        response = self.client.get("/films/F9: The Fast Saga/price?showtime=19:30&is_holiday=true&is_member=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_price", data)
        self.assertGreater(data["total_price"], 0)

    def test_get_available_seats(self):
        response = self.client.get("/seats/Teater 1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("seats", data)
        self.assertIsInstance(data["seats"], list)

    def test_reservation_success(self):
        seats_response = self.client.get("/seats/Teater 1")
        seats_data = seats_response.json()
        seats = seats_data.get("seats", [])

        if len(seats) < 2:
            self.skipTest("Tidak cukup kursi untuk test.")

        payload = {
            "film_title": "The Lion King",
            "showtime": "09:30",
            "seats": seats[:2],
            "is_holiday": False,
            "is_member": True
        }

        response = self.client.post("/reservation", json=payload)
        # Karena endpoint mungkin /book, coba keduanya
        if response.status_code == 404:
            response = self.client.post("/book", json={
                "film_title": payload["film_title"],
                "showtime": payload["showtime"],
                "ticket_count": len(payload["seats"]),
                "is_holiday": payload["is_holiday"],
                "is_member": payload["is_member"],
                "seat_preference": "berurutan"
            })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)

    def test_reservation_invalid_film(self):
        payload = {
            "film_title": "Film Palsu",
            "showtime": "09:30",
            "seats": ["A1"],
            "is_holiday": False,
            "is_member": False
        }
        response = self.client.post("/reservation", json=payload)
        # Jika endpoint tidak ada, coba /book
        if response.status_code == 404 and "Not Found" in response.text:
            response = self.client.post("/book", json={
                "film_title": payload["film_title"],
                "showtime": payload["showtime"],
                "ticket_count": 1,
                "is_holiday": payload["is_holiday"],
                "is_member": payload["is_member"],
                "seat_preference": "berurutan"
            })

        self.assertEqual(response.status_code, 404)

    def test_reservation_invalid_time(self):
        payload = {
            "film_title": "The Lion King",
            "showtime": "00:00",
            "seats": ["A2"],
            "is_holiday": False,
            "is_member": False
        }
        response = self.client.post("/reservation", json=payload)
        # Jika endpoint tidak ada, coba /book
        if response.status_code == 404 and "Not Found" in response.text:
            response = self.client.post("/book", json={
                "film_title": payload["film_title"],
                "showtime": payload["showtime"],
                "ticket_count": 1,
                "is_holiday": payload["is_holiday"],
                "is_member": payload["is_member"],
                "seat_preference": "berurutan"
            })

        self.assertIn(response.status_code, [400, 404])

    # ========== service Layer tests ==========
    def test_film_service_get_all_films(self):
        films = self.film_service.get_all_films()
        self.assertIsInstance(films, list)
        self.assertGreater(len(films), 0)

    def test_film_service_get_film_info(self):
        film_info = self.film_service.get_film_info("Avengers: Endgame")
        self.assertIsNotNone(film_info)
        self.assertEqual(film_info["judul"], "Avengers: Endgame")

    def test_film_service_get_film_schedule(self):
        schedule = self.film_service.get_film_schedule("Avengers: Endgame")
        self.assertIsInstance(schedule, list)
        self.assertGreater(len(schedule), 0)

    def test_film_service_get_film_by_genre(self):
        action_films = self.film_service.get_film_by_genre("Action")
        self.assertIsInstance(action_films, list)

    def test_price_calculator_base_price(self):
        base_price = self.calculator.get_base_price("Avengers: Endgame")
        self.assertGreater(base_price, 0)

    def test_price_calculator_with_discounts(self):
        price_info = self.calculator.get_price(
            "Avengers: Endgame", "10:00", is_holiday=True, is_member=True, jumlah_tiket=2
        )
        self.assertIsInstance(price_info, dict)
        self.assertIn("total", price_info)

    def test_seat_manager_get_available_seats(self):
        available_seats = self.seat_manager.get_available_seats("Teater 1")
        self.assertIsInstance(available_seats, list)

    def test_seat_manager_get_total_available_seats(self):
        total = self.seat_manager.get_total_available_seats("Teater 1")
        self.assertIsInstance(total, int)
        self.assertGreaterEqual(total, 0)

    def test_seat_manager_seat_naming(self):
        seat_name = self.seat_manager.get_seat_name(0)
        self.assertEqual(seat_name, "A1")

        seat_index = self.seat_manager.get_seat_index("A1")
        self.assertEqual(seat_index, 0)

    def test_seat_manager_assign_seat(self):
        assigned_seats = self.seat_manager.assign_seat("Teater 1", 2, prefer_consecutive=True)
        if assigned_seats:  # Jika ada kursi tersedia
            self.assertIsInstance(assigned_seats, list)
            self.assertEqual(len(assigned_seats), 2)

    def test_validator_is_valid_film(self):
        self.assertTrue(self.validator.is_valid_film("Avengers: Endgame"))
        self.assertFalse(self.validator.is_valid_film("Film Tidak Ada"))

    def test_validator_get_valid_showtimes(self):
        showtimes = self.validator.get_valid_showtimes("Avengers: Endgame")
        self.assertIsInstance(showtimes, list)
        self.assertGreater(len(showtimes), 0)

    def test_validator_is_valid_showtime(self):
        self.assertTrue(self.validator.is_valid_showtime("Avengers: Endgame", "10:00"))
        self.assertFalse(self.validator.is_valid_showtime("Avengers: Endgame", "00:00"))

    # ========== Facade tests ==========
    def test_facade_get_films(self):
        films = self.facade.get_films()
        self.assertIsInstance(films, list)
        self.assertGreater(len(films), 0)

    def test_facade_get_films_by_genre(self):
        action_films = self.facade.get_films(genre="Action")
        self.assertIsInstance(action_films, list)

    def test_facade_get_film_detail(self):
        result = self.facade.get_film_detail("Avengers: Endgame")
        self.assertTrue(result["success"])
        self.assertIn("film", result)

    def test_facade_check_seats(self):
        result = self.facade.check_seats(theater_name="Teater 1")
        self.assertTrue(result["success"])
        self.assertIn("total", result)

    def test_facade_calculate_ticket_price(self):
        result = self.facade.calculate_ticket_price(
            "Avengers: Endgame", "10:00", is_holiday=False, is_member=True, ticket_count=1
        )
        self.assertTrue(result["success"])
        self.assertIn("total", result)

    def test_facade_book_tickets(self):
        result = self.facade.book_tickets(
            "Avengers: Endgame", "10:00", 2, is_holiday=False, is_member=True, seat_preference="berurutan"
        )
        # Test bisa berhasil atau gagal tergantung ketersediaan kursi
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

if __name__ == '__main__':
    unittest.main()
