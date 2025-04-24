from typing import List
from config.config_manager import ConfigManager

class PriceCalculator:
    def __init__(self):
        self.config = ConfigManager()
        
    def calculate_subtotal(self, seat_types: List[str]) -> float:
        """Calculator subtotal Dana's table-driven """
        seat_prices = self.config.get_seat_prices()
        return sum(seat_prices.get(seat_type, 0) for seat_type in seat_types)
    
    def apply_discounts(self, subtotal: float, is_holiday: bool, is_member: bool, showtime: str) -> float:
        """discounts Dana discount logic"""
        discounted_total = subtotal
        
        if is_holiday:
            discounted_total *= (1 - self.config.get_discount())
        
        if is_member:
            discounted_total *= (1 - self.config.get_member_discount())
        

        time_discount = self.config.get_time_based_discount(showtime)
        discounted_total *= (1 - time_discount)
        
        return discounted_total
    
    def calculate_total(self, seat_types: List[str], is_holiday: bool = False, 
                       is_member: bool = False, showtime: str = "12:00") -> float:
        """pricing calculation Dana"""
        subtotal = self.calculate_subtotal(seat_types)
        discounted = self.apply_discounts(subtotal, is_holiday, is_member, showtime)
        total = discounted * (1 + self.config.get_tax_rate()) + self.config.get_admin_fee()
        return round(total, 2)
