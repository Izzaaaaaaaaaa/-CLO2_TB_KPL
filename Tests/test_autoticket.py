import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from api import app

from Config.Config_manager import ConfigManager
from Service.film_service import FilmService
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator

client = TestClient(app)

# Inisialisasi modul
config = ConfigManager("config.json")
config.load_config()
film_service = FilmService(config)
calculator = PriceCalculator(config)
seat_manager = SeatManager(config)
validator = TicketValidator(config)

# ========== API Endpoint Tests ==========
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_all_films():
    response = client.get("/films")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_film_by_title():
    response = client.get("/films/Avengers: Endgame")
    assert response.status_code == 200
    data = response.json()
    assert data["judul"] == "Avengers: Endgame"

def test_get_film_showtimes():
    response = client.get("/films/Spider-Man: No Way Home/showtimes")
    assert response.status_code == 200
    assert "11:00" in response.json()

def test_get_film_price():
    response = client.get("/films/F9: The Fast Saga/price?showtime=19:30&is_holiday=true&is_member=true")
    assert response.status_code == 200
    data = response.json()
    assert data["price_info"]["total_price_per_ticket"] > 0

def test_get_available_seats():
    response = client.get("/seats/Teater 1")
    assert response.status_code == 200
    data = response.json()
    assert "seats" in data
    assert isinstance(data["seats"], list)

def test_reservation_success():
    seats_response = client.get("/seats/Teater 1")
    seats = seats_response.json()["seats"]
    if len(seats) < 2:
        assert False, "Tidak cukup kursi untuk test."

    payload = {
        "film_title": "The Lion King",
        "showtime": "09:30",
        "seats": seats[:2],
        "is_holiday": False,
        "is_member": True
    }

    response = client.post("/reservation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["total"] > 0

def test_reservation_invalid_film():
    payload = {
        "film_title": "Film Palsu",
        "showtime": "09:30",
        "seats": ["A1"],
        "is_holiday": False,
        "is_member": False
    }
    response = client.post("/reservation", json=payload)
    assert response.status_code == 404

def test_reservation_invalid_time():
    payload = {
        "film_title": "The Lion King",
        "showtime": "00:00",
        "seats": ["A2"],
        "is_holiday": False,
        "is_member": False
    }
    response = client.post("/reservation", json=payload)
    assert response.status_code == 400

# ========== Unit Test: ConfigManager ==========
def test_config_values():
    assert config.get_diskon_libur() >= 0
    assert config.get_diskon_member() >= 0
    assert config.get_biaya_admin() >= 0
    assert isinstance(config.get_max_kursi(), int)

# ========== Unit Test: FilmService ==========
def test_film_service_info():
    film = film_service.get_film_info("The Lion King")
    assert film is not None
    assert film["judul"] == "The Lion King"

def test_film_schedule():
    schedule = film_service.get_film_schedule("F9: The Fast Saga")
    assert "19:30" in schedule

def test_film_by_genre():
    result = film_service.get_film_by_genre("action")
    assert any("Action" in film["genre"] for film in result)

# ========== Unit Test: PriceCalculator ==========
def test_calculator_price_result():
    result = calculator.get_price("Avengers: Endgame", "10:00", is_holiday=True, is_member=True)
    assert result["harga_dasar"] > 0
    assert result["total_harga"] > 0

# ========== Unit Test: SeatManager ==========
def test_seat_allocation_and_release():
    seats = seat_manager.assign_seat("Teater 1", 2)
    assert seats and len(seats) == 2
    released = seat_manager.release_seat("Teater 1", seats)
    assert released is True

def test_seat_name_index_mapping():
    seat_name = seat_manager.get_seat_name(12)  # Should be B3
    index = seat_manager.get_seat_index(seat_name)
    assert isinstance(seat_name, str)
    assert isinstance(index, int)
    assert index >= 0

# ========== Unit Test: TicketValidator ==========
def test_validator_film_and_showtime():
    assert validator.is_valid_film("F9: The Fast Saga") is True
    assert validator.is_valid_showtime("F9: The Fast Saga", "19:30") is True
    assert validator.is_valid_showtime("F9: The Fast Saga", "00:00") is False
    assert validator.is_valid_film("Film Ga Ada") is False

def test_validator_teater():
    teater = validator.get_teater_by_film("The Lion King")
    assert validator.is_valid_teater(teater) is True
