from datetime import date, datetime


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


class Medicine:
    """One batch of one medicine at one location."""

    def __init__(self, name, batch_id, quantity, expiry_date, location,
                 quality_score=5, is_reserved=False, is_blocked=False):
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        if not 1 <= quality_score <= 5:
            raise ValueError("quality_score must be between 1 and 5")
        self.name = name
        self.batch_id = batch_id
        self.quantity = quantity
        self.expiry_date = _to_date(expiry_date)
        self.location = location
        self.quality_score = quality_score
        self.is_reserved = is_reserved
        self.is_blocked = is_blocked

    def days_until_expiry(self, today):
        return (self.expiry_date - _to_date(today)).days

    def is_expired(self, today):
        return self.days_until_expiry(today) < 0

    def is_dispatchable(self, today, allow_reserved=False):
        """Can this batch be sent out at all?"""
        return (self.quantity > 0
                and not self.is_blocked
                and not self.is_expired(today)
                and (allow_reserved or not self.is_reserved))

    def take(self, qty):
        """Remove qty units from this batch and return how many were taken."""
        taken = min(qty, self.quantity)
        self.quantity -= taken
        return taken

    def __str__(self):
        flags = []
        if self.is_reserved:
            flags.append("RESERVED")
        if self.is_blocked:
            flags.append("BLOCKED")
        flag_str = f" [{' | '.join(flags)}]" if flags else ""
        return (f"{self.name} (Batch {self.batch_id}) - Qty: {self.quantity}, "
                f"Exp: {self.expiry_date} @ {self.location}{flag_str}")

    __repr__ = __str__
