import unittest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app
from Config.Config_manager import ConfigManager
from Service.film_service import FilmService
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
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

    # ========== API Endpoint Tests ==========
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
        self.assertGreater(data["price_info"]["total_price_per_ticket"], 0)

    def test_get_available_seats(self):
        response = self.client.get("/seats/Teater 1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("seats", data)
        self.assertIsInstance(data["seats"], list)

    def test_reservation_success(self):
        seats_response = self.client.get("/seats/Teater 1")
        seats = seats_response.json()["seats"]
        self.assertGreaterEqual(len(seats), 2, "Tidak cukup kursi untuk test.")

        payload = {
            "film_title": "The Lion King",
            "showtime": "09:30",
            "seats": seats[:2],
            "is_holiday": False,
            "is_member": True
        }

        response = self.client.post("/reservation", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "confirmed")
        self.assertGreater(data["total"], 0)

    def test_reservation_invalid_film(self):
        payload = {
            "film_title": "Film Palsu",
            "showtime": "09:30",
            "seats": ["A1"],
            "is_holiday": False,
            "is_member": False
        }
        response = self.client.post("/reservation", json=payload)
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
        self.assertEqual(response.status_code, 400)

    # ========== Unit Test: ConfigManager ==========
    def test_config_values(self):
        self.assertGreaterEqual(self.config.get_diskon_libur(), 0)
        self.assertGreaterEqual(self.config.get_diskon_member(), 0)
        self.assertGreaterEqual(self.config.get_biaya_admin(), 0)
        self.assertIsInstance(self.config.get_max_kursi(), int)

    # ========== Unit Test: FilmService ==========
    def test_film_service_info(self):
        film = self.film_service.get_film_info("The Lion King")
        self.assertIsNotNone(film)
        self.assertEqual(film["judul"], "The Lion King")

    def test_film_schedule(self):
        schedule = self.film_service.get_film_schedule("F9: The Fast Saga")
        self.assertIn("19:30", schedule)

    def test_film_by_genre(self):
        result = self.film_service.get_film_by_genre("action")
        self.assertTrue(any("Action" in film["genre"] for film in result))

    # ========== Unit Test: PriceCalculator ==========
    def test_calculator_price_result(self):
        result = self.calculator.get_price("Avengers: Endgame", "10:00", is_holiday=True, is_member=True)
        self.assertGreater(result["harga_dasar"], 0)
        self.assertGreater(result["total_harga"], 0)

    # ========== Unit Test: SeatManager ==========
    def test_seat_allocation_and_release(self):
        seats = self.seat_manager.assign_seat("Teater 1", 2)
        self.assertEqual(len(seats), 2)
        released = self.seat_manager.release_seat("Teater 1", seats)
        self.assertTrue(released)

    def test_seat_name_index_mapping(self):
        seat_name = self.seat_manager.get_seat_name(12)  # Should be B3
        index = self.seat_manager.get_seat_index(seat_name)
        self.assertIsInstance(seat_name, str)
        self.assertIsInstance(index, int)
        self.assertGreaterEqual(index, 0)

    # ========== Unit Test: TicketValidator ==========
    def test_validator_film_and_showtime(self):
        self.assertTrue(self.validator.is_valid_film("F9: The Fast Saga"))
        self.assertTrue(self.validator.is_valid_showtime("F9: The Fast Saga", "19:30"))
        self.assertFalse(self.validator.is_valid_showtime("F9: The Fast Saga", "00:00"))
        self.assertFalse(self.validator.is_valid_film("Film Ga Ada"))

    def test_validator_teater(self):
        teater = self.validator.get_teater_by_film("The Lion King")
        self.assertTrue(self.validator.is_valid_teater(teater))

if __name__ == '__main__':
    unittest.main()
