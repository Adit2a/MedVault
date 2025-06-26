import heapq
from collections import defaultdict
from medicine import Medicine

class Inventory:
    def __init__(self):
        self.meds_by_name = defaultdict(list)

    def add_medicine(self, name, batch_id, quantity, expiry, location, quality_score=5, reserved=False, blocked=False):
        med = Medicine(name, batch_id, quantity, expiry, location, quality_score, reserved, blocked)
        self.meds_by_name[name].append(med)
        print(f"[ADDED] {med}")


    def get_medicine_batches(self, name, location=None):
        return [m for m in self.meds_by_name[name] if not m.is_blocked and (location is None or m.location == location)]

    def get_priority_batches(self, name, location=None):
        return sorted(self.get_medicine_batches(name, location), key=lambda x: x.priority_score())

    def get_stock(self, name, location=None):
        return sum(m.quantity for m in self.get_medicine_batches(name, location))

    def deduct_stock(self, name, qty_needed, from_location):
        batches = self.get_priority_batches(name, from_location)
        for med in batches:
            if qty_needed <= 0:
                break
            if med.quantity <= qty_needed:
                qty_needed -= med.quantity
                med.quantity = 0
            else:
                med.quantity -= qty_needed
                qty_needed = 0
