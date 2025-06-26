from inventory import Inventory
from graph_routes import Graph

class Redistributor:
    def __init__(self, inventory: Inventory, network: Graph):
        self.inventory = inventory
        self.network = network

    def redistribute(self, name, qty_needed, to_location):
        remaining = qty_needed
        potential_sources = []

        for batch in self.inventory.get_medicine_batches(name):
            if batch.location != to_location and batch.quantity > 0:
                dist, path = self.network.dijkstra(batch.location, to_location)
                if dist < float('inf'):
                    priority = batch.priority_score()
                    potential_sources.append((priority, dist, batch, path))

        potential_sources.sort()

        for _, dist, batch, path in potential_sources:
            if remaining <= 0:
                break
            pull_qty = min(batch.quantity, remaining)
            self.inventory.deduct_stock(name, pull_qty, batch.location)
            print(f"Transferring {pull_qty} units of {name} from {batch.location} → {to_location} via {path} ({dist} km) | Score: {batch.priority_score():.1f}")
            remaining -= pull_qty

        if remaining > 0:
            print(f"Still need {remaining} units of {name} at {to_location}")
