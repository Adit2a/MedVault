from datetime import datetime

class Medicine:
    def __init__(self, name, batch_id, quantity, expiry_date, location, quality_score=5, is_reserved=False, is_blocked=False):
        self.name = name
        self.batch_id = batch_id
        self.quantity = quantity
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        self.location = location
        self.quality_score = quality_score
        self.is_reserved = is_reserved
        self.is_blocked = is_blocked

    def days_until_expiry(self):
        return (self.expiry_date - datetime.now()).days

    def priority_score(self):
        score = self.days_until_expiry() * 0.5 + self.quality_score * 2
        if self.is_reserved:
            score += 100
        if self.is_blocked:
            score += 1_000
        return score

    def __lt__(self, other):
        return self.priority_score() < other.priority_score()

    def __str__(self):
        flags = []
        if self.is_reserved: flags.append("RESERVED")
        if self.is_blocked: flags.append("BLOCKED")
        flag_str = " | ".join(flags) if flags else ""
        return f"{self.name} (Batch {self.batch_id}) - Qty: {self.quantity}, Exp: {self.expiry_date.date()} @ {self.location} {flag_str}"