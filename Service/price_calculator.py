from config.config_manager import ConfigManager

class PriceCalculator:
    def __init__(self):
        self.config = ConfigManager()
        
    def calculate_price(self, seat_type, quantity, discount_code=None):
        base_price = self.config.get_seat_prices().get(seat_type, 0)
        total = base_price * quantity
        
        if discount_code:
            total = self.config.apply_discount(total, discount_code)
            
        return round(total)
