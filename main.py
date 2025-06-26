from inventory import Inventory
from graph_routes import Graph
from redistribution import Redistributor
from alerts import AlertSystem

inv = Inventory()
net = Graph()
alert = AlertSystem(inv)
redis = Redistributor(inv, net)

net.add_edge("WarehouseA", "HospitalB", 5)
net.add_edge("HospitalB", "PharmacyX", 2)
net.add_edge("WarehouseB", "HospitalB", 4)
net.add_edge("WarehouseC", "HospitalB", 6)
net.add_edge("WarehouseC", "ClinicC", 3)

inv.add_medicine("Paracetamol", "P123", 30, "2025-01-10", "WarehouseA", quality_score=4)
inv.add_medicine("Paracetamol", "P456", 25, "2024-06-28", "WarehouseB", quality_score=2)
inv.add_medicine("Paracetamol", "P789", 50, "2024-06-20", "WarehouseC", quality_score=3, reserved=True)
inv.add_medicine("Adrenaline", "A111", 15, "2024-06-30", "WarehouseC", quality_score=1)
inv.add_medicine("Adrenaline", "A222", 5, "2024-07-02", "WarehouseB", quality_score=2, blocked=True)

alert.show_expiry_alerts()
alert.show_low_stock_alerts()
alert.show_special_flags()

print("\nRedistributing 40 Paracetamol to PharmacyX:")
redis.redistribute("Paracetamol", 40, "PharmacyX")

print("\nEmergency: 10 Adrenaline to ClinicC")
redis.redistribute("Adrenaline", 10, "ClinicC")
