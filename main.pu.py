# main.py

from inventory import Inventory
from graph_routes import Graph
from redistribution import Redistributor
from alerts import AlertSystem

inv = Inventory()
net = Graph()
alert = AlertSystem(inv)
redis = Redistributor(inv, net)

# Add distribution routes (edges)
net.add_edge("WarehouseA", "HospitalB", 5)
net.add_edge("HospitalB", "PharmacyX", 2)
net.add_edge("WarehouseA", "PharmacyX", 10)
net.add_edge("WarehouseA", "WarehouseB", 3)
net.add_edge("WarehouseB", "HospitalB", 4)

# Add some medicines
inv.add_medicine("Paracetamol", "P123", 100, "2025-01-10", "WarehouseA")
inv.add_medicine("Paracetamol", "P456", 40, "2024-06-30", "WarehouseB")
inv.add_medicine("Adrenaline", "A123", 20, "2024-07-01", "WarehouseB")

# Simulate operations
alert.show_expiry_alerts()
alert.show_low_stock_alerts()

# Redistribute request
print("\n🛠️ Redistribution:")
redis.redistribute("Paracetamol", 50, "PharmacyX")

# Emergency
print("\n🚨 Emergency Request:")
redis.redistribute("Adrenaline", 15, "HospitalB")
