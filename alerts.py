from inventory import Inventory
from collections import defaultdict


class AlertSystem:
    def __init__(self, inventory: Inventory, low_stock_threshold=10):
        self.inventory = inventory
        self.low_stock_threshold = low_stock_threshold

    def show_expiry_alerts(self):
        print("\nExpiry Alerts:")
        for name in self.inventory.meds_by_name:
            for med in self.inventory.get_medicine_batches(name):
                if med.days_until_expiry() <= 10:
                    print(f"{med}")

    def show_low_stock_alerts(self):
        print("\nLow Stock Alerts:")
        for name in self.inventory.meds_by_name:
            stock_by_loc = defaultdict(int)
            for med in self.inventory.get_medicine_batches(name):
                stock_by_loc[med.location] += med.quantity
            for loc, qty in stock_by_loc.items():
                if qty < self.low_stock_threshold:
                    print(f"{name} in {loc} is LOW on stock: {qty} units")

    def show_special_flags(self):
        print("\nReserved/Blocked Batches:")
        for name in self.inventory.meds_by_name:
            for med in self.inventory.meds_by_name[name]:
                if med.is_reserved or med.is_blocked:
                    print(f"{med}")
