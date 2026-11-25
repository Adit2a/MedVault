from dataclasses import dataclass

from graph_routes import Graph
from inventory import Inventory
from min_heap import MinHeap


@dataclass
class Transfer:
    batch_id: str
    from_location: str
    to_location: str
    quantity: int
    distance: float
    path: list
    days_until_expiry: int

    def __str__(self):
        route = " -> ".join(self.path)
        return (f"{self.quantity} units of batch {self.batch_id} from {self.from_location}"
                f" ({self.distance} km via {route}, expires in {self.days_until_expiry} days)")


@dataclass
class RedistributionResult:
    transfers: list
    shortfall: int


class Redistributor:
    """Greedy fulfilment that weighs expiry against distance.

    Each candidate batch gets a cost:

        cost = days_until_expiry + distance_weight * distance_km

    and batches are taken cheapest-first from a MinHeap. A low cost means
    "about to expire and close by". distance_weight sets the trade-off:
    with 1.0, one extra km costs as much as one extra day of shelf life.
    In an emergency, reserved stock is allowed and distance counts far
    more, so the nearest usable stock goes first.
    """

    def __init__(self, inventory: Inventory, network: Graph,
                 distance_weight=1.0, emergency_distance_weight=100.0):
        self.inventory = inventory
        self.network = network
        self.distance_weight = distance_weight
        self.emergency_distance_weight = emergency_distance_weight

    def redistribute(self, name, qty_needed, to_location, emergency=False):
        today = self.inventory.today
        weight = self.emergency_distance_weight if emergency else self.distance_weight

        # Roads are two-way, so ONE Dijkstra from the destination gives the
        # distance to every possible source (instead of one run per batch).
        dist, prev = self.network.dijkstra(to_location)

        candidates = MinHeap(key=lambda c: c[0])
        for batch in self.inventory.dispatchable_batches(name, allow_reserved=emergency):
            if batch.location == to_location or batch.location not in dist:
                continue  # already there, or unreachable
            d = dist[batch.location]
            cost = batch.days_until_expiry(today) + weight * d
            candidates.push((cost, -batch.quality_score, batch, d))

        transfers = []
        remaining = qty_needed
        while remaining > 0 and candidates:
            _, _, batch, d = candidates.pop()
            source = batch.location
            moved = batch.take(remaining)       # deduct from THIS batch only
            self.inventory.receive(batch, moved, to_location)
            remaining -= moved
            path = self.network.build_path(prev, to_location, source)[::-1]
            transfers.append(Transfer(batch.batch_id, source, to_location, moved,
                                      d, path, batch.days_until_expiry(today)))

        return RedistributionResult(transfers, remaining)
