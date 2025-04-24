from typing import Dict, List, Tuple, Optional
from Config.Config_manager import ConfigManager

class SeatManager:

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.max_kursi = config_manager.get_max_kursi()
        self.teater_info = config_manager.get_teater_info()

        self.seat_status: Dict[str, List[bool]] = {}

        jumlah_teater = self.teater_info.get("jumlah_teater", 0)
        tipe_teater = self.teater_info.get("tipe_teater", {})

        for teater_name in tipe_teater.keys():
            self.seat_status[teater_name] = [True] * self.max_kursi

    def get_seat_status(self, teater_name: str) -> List[bool]:
        return self.seat_status.get(teater_name, [])

    def get_available_seats(self, teater_name: str) -> List[int]:
        seats = self.seat_status.get(teater_name, [])
        return [i for i, available in enumerate(seats) if available]

    def get_total_available_seats(self, teater_name: str) -> int:
        return sum(1 for seat in self.seat_status.get(teater_name, []) if seat)