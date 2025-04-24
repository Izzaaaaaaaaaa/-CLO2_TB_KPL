from typing import List
from config.config_manager import ConfigManager

class PriceCalculator:
    def __init__(self):
        self.config = ConfigManager()
        self.config.load_config()  #terload
    
    def _get_harga_tiket(self, jenis_kursi: str) -> int:
        """Dapatkan harga tiket berdasarkan jenis kursi"""
        harga_map = {
            "regular": self.config.get_tiket_config().get("HARGA_REGULER", 35000),
            "premium": self.config.get_tiket_config().get("HARGA_PREMIUM", 50000),
            "vip": self.config.get_tiket_config().get("HARGA_VIP", 75000)
        }
        return harga_map.get(jenis_kursi.lower(), harga_map["regular"])
    
    def hitung_subtotal(self, jenis_kursi_list: List[str]) -> int:
        """Hitung subtotal sebelum diskon dan pajak"""
        return sum(self._get_harga_tiket(jenis) for jenis in jenis_kursi_list)
    
    def hitung_diskon(self, subtotal: int, is_libur: bool = False, 
                     is_member: bool = False, jam_tayang: str = "12:00") -> int:
        """Hitung total diskon yang berlaku"""
        diskon = 0
        
        if is_libur:
            diskon += subtotal * self.config.get_diskon_libur() // 100
        
        if is_member:
            diskon += subtotal * self.config.get_diskon_member() // 100
        
        diskon_waktu = self.config.get_diskon_by_jam(jam_tayang)
        diskon += subtotal * diskon_waktu // 100
        
        return diskon
    
    def hitung_pajak(self, amount: int) -> int:
        """Hitung pajak"""
        return amount * self.config.get_tiket_config().get("PAJAK", 10) // 100
    
    def hitung_total(self, jenis_kursi_list: List[str], 
                    is_libur: bool = False, 
                    is_member: bool = False, 
                    jam_tayang: str = "12:00") -> int:
        """
        Hitung total harga yang harus dibayar
        """
        subtotal = self.hitung_subtotal(jenis_kursi_list)
        diskon = self.hitung_diskon(subtotal, is_libur, is_member, jam_tayang)
        subtotal_setelah_diskon = subtotal - diskon
        pajak = self.hitung_pajak(subtotal_setelah_diskon)
        biaya_admin = self.config.get_biaya_admin()
        
        return subtotal_setelah_diskon + pajak + biaya_admin

# Contoh penggunaan
if __name__ == '__main__':
    calculator = PriceCalculator()
    
    # pemesanan 2 tiket regular dan 1 premium di hari libur untuk member, jam 20:00
    total = calculator.hitung_total(
        jenis_kursi_list=["regular", "regular", "premium"],
        is_libur=True,
        is_member=True,
        jam_tayang="20:00"
    )
    
    print(f"Total harga yang harus dibayar: Rp {total:,}")
