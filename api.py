# ======================================
# AutoTicket CLI Project
# ======================================
# File: api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

# Import internal modules
from Config.Config_manager import ConfigManager
from Service.film_service import FilmService
from Service.price_calculator import PriceCalculator
from Service.seat_manager import SeatManager
from Validation.ticket_validator import TicketValidator

# Initialize FastAPI
app = FastAPI(
    title="AutoTicket API",
    description="API untuk sistem pemesanan tiket bioskop AutoTicket",
    version="1.0.0"
)

# Initialize services
config_manager = ConfigManager()
config_manager.load_config()
film_service = FilmService(config_manager)
price_calculator = PriceCalculator(config_manager)
seat_manager = SeatManager(config_manager)
ticket_validator = TicketValidator(config_manager)

# Request model
class SeatReservation(BaseModel):
    film_title: str
    showtime: str
    seats: List[str]
    is_holiday: bool = False
    is_member: bool = False

@app.get("/", tags=["Info"])
def read_root():
    return {"message": "Selamat datang di AutoTicket API", "version": "1.0.0"}

@app.get("/films", tags=["Film"])
def get_all_films():
    films = film_service.get_all_films()
    if not films:
        raise HTTPException(status_code=404, detail="Tidak ada film yang tersedia")
    return films

@app.get("/films/{title}", tags=["Film"])
def get_film_details(title: str):
    film = film_service.get_film_info(title)
    if not film:
        raise HTTPException(status_code=404, detail=f"Film '{title}' tidak ditemukan")
    return film

@app.get("/films/{title}/showtimes", tags=["Film"])
def get_showtimes(title: str):
    showtimes = film_service.get_film_schedule(title)
    if not showtimes:
        raise HTTPException(status_code=404, detail=f"Jadwal untuk film '{title}' tidak ditemukan")
    return showtimes

@app.get("/films/{title}/price", tags=["Harga"])
def get_ticket_price(title: str, showtime: str, is_holiday: bool = False, is_member: bool = False):
    film = film_service.get_film_info(title)
    if not film:
        raise HTTPException(status_code=404, detail=f"Film '{title}' tidak ditemukan")

    if not ticket_validator.is_valid_showtime(title, showtime):
        raise HTTPException(status_code=400, detail=f"Jadwal '{showtime}' tidak valid")

    price_info = price_calculator.get_price(title, showtime, is_holiday, is_member)
    if not price_info:
        raise HTTPException(status_code=404, detail=f"Informasi harga untuk film '{title}' tidak ditemukan")

    return {
        "film": title,
        "showtime": showtime,
        "price_info": {
            "base_price": price_info.get("harga_dasar", 0),
            "discounts": {
                "time_discount": price_info.get("diskon_waktu", {}).get("nominal", 0),
                "holiday_discount": price_info.get("diskon_libur", {}).get("nominal", 0),
                "member_discount": price_info.get("diskon_member", {}).get("nominal", 0),
                "total_discount": price_info.get("total_diskon", 0)
            },
            "price_after_discount": price_info.get("harga_setelah_diskon", 0),
            "admin_fee": price_info.get("biaya_admin", 0),
            "total_price_per_ticket": price_info.get("total_harga", price_info.get("total", 0))
        },
        "is_holiday": is_holiday,
        "is_member": is_member
    }

@app.get("/seats/{teater_name}", tags=["Kursi"])
def get_seats(teater_name: str):
    available_seats = seat_manager.get_available_seats(teater_name)
    if not available_seats and teater_name in seat_manager.seat_status:
        return {"message": f"Tidak ada kursi tersedia di {teater_name}", "seats": []}

    seat_names = [seat_manager.get_seat_name(idx) for idx in available_seats]
    return {
        "teater": teater_name,
        "available_count": len(available_seats),
        "seats": seat_names
    }

@app.post("/reservation", tags=["Reservasi"])
def reserve_seat(reservation: SeatReservation):
    title = reservation.film_title
    showtime = reservation.showtime
    seats = reservation.seats

    film = film_service.get_film_info(title)
    if not film:
        raise HTTPException(status_code=404, detail=f"Film '{title}' tidak ditemukan")

    if not ticket_validator.is_valid_showtime(title, showtime):
        raise HTTPException(status_code=400, detail=f"Jadwal '{showtime}' tidak valid")

    teater_name = film_service.get_film_teater(title)
    if not teater_name:
        raise HTTPException(status_code=404, detail=f"Teater untuk film '{title}' tidak ditemukan")

    for seat in seats:
        seat_index = seat_manager.get_seat_index(seat)
        if seat_index == -1:
            raise HTTPException(status_code=400, detail=f"Format kursi '{seat}' tidak valid")
        if seat_index >= len(seat_manager.seat_status[teater_name]) or not seat_manager.seat_status[teater_name][seat_index]:
            raise HTTPException(status_code=400, detail=f"Kursi '{seat}' tidak tersedia")

    for seat in seats:
        seat_index = seat_manager.get_seat_index(seat)
        seat_manager.seat_status[teater_name][seat_index] = False

    price_info = price_calculator.get_price(title, showtime, reservation.is_holiday, reservation.is_member)
    if not price_info:
        raise HTTPException(status_code=404, detail=f"Informasi harga untuk film '{title}' tidak ditemukan")

    price_per_ticket = price_info.get("total_harga", price_info.get("total", 0))
    total_price = price_per_ticket * len(seats)

    return {
        "film": title,
        "showtime": showtime,
        "teater": teater_name,
        "seats": seats,
        "price_info": {
            "price_per_ticket": price_per_ticket,
            "total_seats": len(seats)
        },
        "total": total_price,
        "reservation_id": f"RES-{hash(str(reservation) + str(total_price)) % 10000:04d}",
        "status": "confirmed"
    }

# Run API with Uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
