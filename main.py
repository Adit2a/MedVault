"""MedVault demo. Dates are relative to today, so the demo never goes stale."""
from datetime import date, timedelta

from alerts import AlertSystem
from graph_routes import Graph
from inventory import Inventory
from redistribution import Redistributor


def days(n):
    return date.today() + timedelta(days=n)


def section(title):
    print(f"\n== {title} ==")


def show(items, empty="none"):
    for item in items or [empty]:
        print(" ", item)


inv = Inventory()
net = Graph()
alerts = AlertSystem(inv, low_stock_threshold=10, expiry_window_days=30)
redis = Redistributor(inv, net)

net.add_edge("WarehouseA", "HospitalB", 5)
net.add_edge("HospitalB", "PharmacyX", 2)
net.add_edge("WarehouseB", "HospitalB", 4)
net.add_edge("WarehouseC", "HospitalB", 6)
net.add_edge("WarehouseC", "ClinicC", 3)

inv.add_medicine("Paracetamol", "P001", 20, days(-5), "WarehouseB", quality_score=4)   # expired
inv.add_medicine("Paracetamol", "P123", 30, days(200), "WarehouseA", quality_score=4)
inv.add_medicine("Paracetamol", "P456", 25, days(20), "WarehouseB", quality_score=2)
inv.add_medicine("Paracetamol", "P789", 50, days(10), "WarehouseC", quality_score=3, reserved=True)
inv.add_medicine("Adrenaline", "A111", 15, days(90), "WarehouseC", quality_score=5)
inv.add_medicine("Adrenaline", "A222", 5, days(60), "WarehouseB", quality_score=2, blocked=True)
inv.add_medicine("Adrenaline", "A333", 8, days(120), "ClinicC", quality_score=5, reserved=True)

section("Expired (pull from shelves, never shipped)")
show(alerts.expired())
section("Expiring within 30 days")
show(alerts.near_expiry())
section("Reserved / blocked")
show(alerts.flagged())


def run(name, qty, to, emergency=False):
    label = "EMERGENCY: " if emergency else ""
    section(f"{label}{qty} {name} -> {to}")
    result = redis.redistribute(name, qty, to, emergency=emergency)
    show(result.transfers, empty="no usable stock reachable")
    if result.shortfall:
        print(f"  Still short by {result.shortfall} units")


run("Paracetamol", 40, "PharmacyX")
run("Adrenaline", 20, "HospitalB", emergency=True)

section("Low stock after transfers")
show([f"{n} at {loc}: {q} units" for n, loc, q in alerts.low_stock()])
