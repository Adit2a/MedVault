from collections import defaultdict

from inventory import Inventory


class AlertSystem:
    def __init__(self, inventory: Inventory, low_stock_threshold=10, expiry_window_days=30):
        self.inventory = inventory
        self.low_stock_threshold = low_stock_threshold
        self.expiry_window_days = expiry_window_days

    def _batches(self):
        for batches in self.inventory.meds_by_name.values():
            yield from batches

    def expired(self):
        """Expired batches that still hold stock: these must be pulled and disposed of."""
        today = self.inventory.today
        return [m for m in self._batches() if m.quantity > 0 and m.is_expired(today)]

    def near_expiry(self):
        today = self.inventory.today
        return [m for m in self._batches()
                if m.quantity > 0 and 0 <= m.days_until_expiry(today) <= self.expiry_window_days]

    def low_stock(self):
        """(name, location, usable_qty) for every location below the threshold."""
        today = self.inventory.today
        out = []
        for name, batches in self.inventory.meds_by_name.items():
            stock = defaultdict(int)
            for m in batches:
                stock[m.location] += 0 if (m.is_blocked or m.is_expired(today)) else m.quantity
            out += [(name, loc, qty) for loc, qty in stock.items()
                    if qty < self.low_stock_threshold]
        return out

    def flagged(self):
        return [m for m in self._batches() if m.is_reserved or m.is_blocked]
