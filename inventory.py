from collections import defaultdict
from datetime import date

from medicine import Medicine
from min_heap import MinHeap


def fefo_key(batch, today):
    """First-Expiry-First-Out: soonest (unexpired) expiry first,
    then higher quality first."""
    return (batch.days_until_expiry(today), -batch.quality_score)


class Inventory:
    def __init__(self, today=None):
        # today can be fixed so tests and demos are reproducible
        self.today = today or date.today()
        self.meds_by_name = defaultdict(list)  # name -> [Medicine, ...]

    def add_medicine(self, name, batch_id, quantity, expiry, location,
                     quality_score=5, reserved=False, blocked=False):
        med = Medicine(name, batch_id, quantity, expiry, location,
                       quality_score, reserved, blocked)
        self.meds_by_name[name].append(med)
        return med

    def all_batches(self, name, location=None):
        return [m for m in self.meds_by_name.get(name, [])
                if location is None or m.location == location]

    def dispatchable_batches(self, name, location=None, allow_reserved=False):
        """Batches that may be shipped: not blocked, not expired, not empty,
        and not reserved unless allow_reserved (emergency)."""
        return [m for m in self.all_batches(name, location)
                if m.is_dispatchable(self.today, allow_reserved)]

    def priority_batches(self, name, location=None, allow_reserved=False):
        """Dispatchable batches in FEFO order, using the MinHeap."""
        heap = MinHeap(self.dispatchable_batches(name, location, allow_reserved),
                       key=lambda b: fefo_key(b, self.today))
        ordered = []
        while heap:
            ordered.append(heap.pop())
        return ordered

    def get_stock(self, name, location=None):
        """Usable stock (blocked and expired batches don't count)."""
        return sum(m.quantity for m in self.all_batches(name, location)
                   if not m.is_blocked and not m.is_expired(self.today))

    def receive(self, batch, qty, location):
        """Record qty units of batch arriving at location."""
        for m in self.meds_by_name[batch.name]:
            if m.batch_id == batch.batch_id and m.location == location:
                m.quantity += qty
                return m
        return self.add_medicine(batch.name, batch.batch_id, qty, batch.expiry_date,
                                 location, batch.quality_score)
