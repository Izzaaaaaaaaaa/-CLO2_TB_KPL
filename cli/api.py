from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
from service.autoticket_facade import AutoTicketFacade
from env_loader import get_env

# Gunakan environment variable untuk menginisialisasi FastAPI
app = FastAPI(
    title="AutoTicket API",
    description="API untuk sistem pemesanan tiket bioskop",
    version=get_env("API_VERSION", "1.0.0")
)

# Inisialisasi facade menggunakan environment variable untuk config path
facade = AutoTicketFacade()  # Internally uses CONFIG_PATH from env

class SeatReservation(BaseModel):
    film_title: str
    showtime: str
    seats: List[str]
    is_holiday: bool = False
    is_member: bool = False

class TicketRequest(BaseModel):
    film_title: str
    showtime: str
    ticket_count: int
    is_holiday: bool = False
    is_member: bool = False
    seat_preference: str = "berurutan"

@app.get("/", tags=["Info"])
def read_root():
    """
    Endpoint root untuk informasi API
    """
    return {"message": "Selamat datang di AutoTicket API", "version": get_env("API_VERSION", "1.0.0")}

@app.get("/films", tags=["Film"])
def get_films(genre: str = None):
    """
    Mendapatkan daftar semua film atau filter berdasarkan genre
    """
    films = facade.get_films(genre)
    if not films:
        raise HTTPException(status_code=404, detail="Tidak ada film yang tersedia")
    return [film.dict() for film in films]

@app.get("/films/{title}", tags=["Film"])
def get_film_by_title(title: str):
    """
    Mendapatkan informasi film berdasarkan judul
    """
    result = facade.get_film_detail(title)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result["film"].dict()

@app.get("/films/{title}/showtimes", tags=["Film"])
def get_film_showtimes(title: str):
    """
    Mendapatkan jadwal tayang untuk film tertentu
    """
    result = facade.get_film_detail(title)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result["film"].jadwal

@app.get("/films/{title}/price", tags=["Film"])
def get_film_price(
    title: str,
    showtime: str,
    is_holiday: bool = False,
    is_member: bool = False,
    ticket_count: int = 1
):
    """
    Mendapatkan informasi harga tiket untuk film tertentu
    """
    price_result = facade.calculate_ticket_price(
        title, showtime, is_holiday, is_member, ticket_count
    )

    if not price_result["success"]:
        raise HTTPException(status_code=404, detail=price_result["message"])
    return {
        "film": title,
        "showtime": showtime,
        "is_holiday": is_holiday,
        "is_member": is_member,
        "ticket_count": ticket_count,
        "price_info": {
            "base_price": price_result["harga_dasar"],
            "discounts": {
                "time_discount": price_result["diskon"]["waktu"],
                "holiday_discount": price_result["diskon"]["libur"],
                "member_discount": price_result["diskon"]["member"],
                "total_discount": price_result["total_diskon"]
            },
            "admin_fee": price_result["biaya_admin"],
            "price_per_ticket": price_result["harga_per_tiket"],
        },
        "total_price": price_result["total"]
    }

@app.get("/seats/{teater_name}", tags=["Kursi"])
def get_available_seats(teater_name: str):
    """
    Mendapatkan daftar kursi yang tersedia untuk teater tertentu
    """
    result = facade.check_seats(theater_name=teater_name)

    if not result["success"]:
        return {"message": result["message"], "seats": []}

    return {
        "teater": teater_name,
        "available_count": result["total"],
        "seats": result["contoh_kursi"]
    }

@app.post("/book", tags=["Reservasi"])
def book_tickets(request: TicketRequest):
    """
    Memesan tiket film dengan jumlah tertentu
    """
    result = facade.book_tickets(
        request.film_title,
        request.showtime,
        request.ticket_count,
        request.is_holiday,
        request.is_member,
        request.seat_preference
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "reservation_id": result["reservation_id"],
        "film": result["film"],
        "showtime": result["jadwal"],
        "teater": result["teater"],
        "seats": result["kursi"],
        "price": result["harga"],
        "status": result["status"]
    }

@app.post("/reservation", tags=["Reservasi"])
def reserve_specific_seats(reservation: SeatReservation):
    """
    Memesan tiket film dengan kursi spesifik
    """
    # Validasi film dengan facade
    film_details = facade.get_film_detail(reservation.film_title)
    if not film_details["success"]:
        raise HTTPException(status_code=404, detail=film_details["message"])

    # Validasi jadwal
    film = film_details["film"]
    if reservation.showtime not in film.jadwal:
        raise HTTPException(status_code=400, detail=f"Jadwal '{reservation.showtime}' tidak valid")

    # Cek ketersediaan kursi
    seat_check = facade.check_seats(theater_name=film.teater)
    if not seat_check["success"]:
        raise HTTPException(status_code=400, detail=seat_check["message"])

    # Validasi kursi spesifik yang diminta
    for seat in reservation.seats:
        seat_index = facade._seat_manager.get_seat_index(seat)
        if seat_index == -1:
            raise HTTPException(status_code=400, detail=f"Format kursi '{seat}' tidak valid")

        if seat_index >= len(facade._seat_manager.seat_status[film.teater]) or not facade._seat_manager.seat_status[film.teater][seat_index]:
            raise HTTPException(status_code=400, detail=f"Kursi '{seat}' tidak tersedia")

    # Tandai kursi sebagai dipesan
    for seat in reservation.seats:
        seat_index = facade._seat_manager.get_seat_index(seat)
        facade._seat_manager.seat_status[film.teater][seat_index] = False

    # Hitung harga
    price_result = facade.calculate_ticket_price(
        reservation.film_title,
        reservation.showtime,
        reservation.is_holiday,
        reservation.is_member,
        len(reservation.seats)
    )

    if not price_result["success"]:
        # Kembalikan kursi jika perhitungan gagal
        facade.cancel_booking(film.teater, reservation.seats)
        raise HTTPException(status_code=404, detail=price_result["message"])

    import secrets
    reservation_id = f"RES-{secrets.randbelow(9000) + 1000}"

    return {
        "reservation_id": reservation_id,
        "film": reservation.film_title,
        "showtime": reservation.showtime,
        "teater": film.teater,
        "seats": reservation.seats,
        "price": price_result["total"],
        "status": "confirmed"
    }
