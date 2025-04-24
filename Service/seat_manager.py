class SeatManager:
    def __init__(self):
        self.seats = {
            'regular': [True]*50,
            'premium': [True]*30,
            'vip': [True]*20
        }
    
    def auto_select_seat(self, seat_type):
        available = self.seats[seat_type].index(True)
        if available != -1:
            self.seats[seat_type][available] = False
            return f"{seat_type.upper()}-{available+1}"
        return None
