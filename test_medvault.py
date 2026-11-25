import random
import unittest
from datetime import date, timedelta

from alerts import AlertSystem
from graph_routes import Graph
from inventory import Inventory
from min_heap import MinHeap
from redistribution import Redistributor

TODAY = date(2026, 1, 1)


def d(n):
    return TODAY + timedelta(days=n)


class MinHeapTest(unittest.TestCase):
    def test_pops_in_sorted_order(self):
        rng = random.Random(42)
        for _ in range(50):
            values = [rng.randint(-100, 100) for _ in range(rng.randint(0, 60))]
            heap = MinHeap()
            for v in values:
                heap.push(v)
            self.assertEqual([heap.pop() for _ in range(len(heap))], sorted(values))

    def test_heapify_constructor(self):
        values = [5, 3, 9, 1, 1, 7]
        heap = MinHeap(values)
        self.assertEqual(heap.peek(), 1)
        self.assertEqual([heap.pop() for _ in values], sorted(values))

    def test_key_and_stable_ties(self):
        heap = MinHeap(key=lambda x: x[0])
        for item in [(2, "a"), (1, "b"), (2, "c"), (1, "d")]:
            heap.push(item)
        self.assertEqual([heap.pop()[1] for _ in range(4)], ["b", "d", "a", "c"])

    def test_empty(self):
        with self.assertRaises(IndexError):
            MinHeap().pop()


class GraphTest(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        self.g.add_edge("A", "B", 1)
        self.g.add_edge("B", "C", 2)
        self.g.add_edge("A", "C", 10)
        self.g.add_location("Island")

    def test_shortest_path(self):
        self.assertEqual(self.g.shortest_path("A", "C"), (3, ["A", "B", "C"]))
        self.assertEqual(self.g.shortest_path("A", "A"), (0, ["A"]))

    def test_unreachable(self):
        self.assertEqual(self.g.shortest_path("A", "Island"), (float("inf"), []))

    def test_negative_edge_rejected(self):
        with self.assertRaises(ValueError):
            self.g.add_edge("A", "D", -1)


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory(today=TODAY)
        self.inv.add_medicine("X", "old", 10, d(-1), "W")
        self.inv.add_medicine("X", "late", 10, d(100), "W")
        self.inv.add_medicine("X", "soon", 10, d(5), "W")
        self.inv.add_medicine("X", "blocked", 10, d(1), "W", blocked=True)
        self.inv.add_medicine("X", "reserved", 10, d(2), "W", reserved=True)

    def test_fefo_skips_expired_blocked_reserved(self):
        ids = [b.batch_id for b in self.inv.priority_batches("X")]
        self.assertEqual(ids, ["soon", "late"])

    def test_emergency_includes_reserved(self):
        ids = [b.batch_id for b in self.inv.priority_batches("X", allow_reserved=True)]
        self.assertEqual(ids, ["reserved", "soon", "late"])

    def test_stock_ignores_expired_and_blocked(self):
        self.assertEqual(self.inv.get_stock("X"), 30)


class RedistributorTest(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory(today=TODAY)
        self.net = Graph()
        self.net.add_edge("Near", "Dest", 1)
        self.net.add_edge("Far", "Dest", 50)
        self.net.add_location("Island")
        self.redis = Redistributor(self.inv, self.net, distance_weight=1.0)

    def test_never_ships_expired_stock(self):
        self.inv.add_medicine("X", "expired", 100, d(-3), "Near")
        result = self.redis.redistribute("X", 10, "Dest")
        self.assertEqual(result.transfers, [])
        self.assertEqual(result.shortfall, 10)

    def test_distance_changes_the_choice(self):
        # Far batch expires 20 days sooner but is 49 km further: Near wins.
        self.inv.add_medicine("X", "near", 10, d(40), "Near")
        self.inv.add_medicine("X", "far", 10, d(20), "Far")
        result = self.redis.redistribute("X", 10, "Dest")
        self.assertEqual(result.transfers[0].batch_id, "near")

    def test_expiry_wins_when_distance_is_similar(self):
        self.net.add_edge("Near2", "Dest", 2)
        self.inv.add_medicine("X", "a", 10, d(40), "Near")
        self.inv.add_medicine("X", "b", 10, d(5), "Near2")
        result = self.redis.redistribute("X", 10, "Dest")
        self.assertEqual(result.transfers[0].batch_id, "b")

    def test_deducts_from_the_chosen_batch_and_moves_stock(self):
        keep = self.inv.add_medicine("X", "keep", 10, d(1), "Near", reserved=True)
        use = self.inv.add_medicine("X", "use", 10, d(30), "Near")
        result = self.redis.redistribute("X", 4, "Dest")
        self.assertEqual(keep.quantity, 10)
        self.assertEqual(use.quantity, 6)
        self.assertEqual(self.inv.get_stock("X", "Dest"), 4)
        self.assertEqual(result.transfers[0].path, ["Near", "Dest"])

    def test_partial_fulfilment_and_unreachable(self):
        self.inv.add_medicine("X", "n", 5, d(30), "Near")
        self.inv.add_medicine("X", "f", 5, d(30), "Far")
        self.inv.add_medicine("X", "i", 100, d(30), "Island")
        result = self.redis.redistribute("X", 20, "Dest")
        self.assertEqual(sum(t.quantity for t in result.transfers), 10)
        self.assertEqual(result.shortfall, 10)

    def test_emergency_uses_reserved_and_prefers_nearest(self):
        self.inv.add_medicine("X", "far", 10, d(1), "Far")
        self.inv.add_medicine("X", "near_res", 10, d(300), "Near", reserved=True)
        self.assertEqual(self.redis.redistribute("X", 5, "Dest").transfers[0].batch_id, "far")
        result = self.redis.redistribute("X", 5, "Dest", emergency=True)
        self.assertEqual(result.transfers[0].batch_id, "near_res")


class AlertsTest(unittest.TestCase):
    def test_alerts(self):
        inv = Inventory(today=TODAY)
        inv.add_medicine("X", "exp", 5, d(-1), "W")
        inv.add_medicine("X", "soon", 5, d(10), "W")
        inv.add_medicine("X", "fine", 50, d(300), "V", blocked=True)
        alerts = AlertSystem(inv, low_stock_threshold=10, expiry_window_days=30)
        self.assertEqual([m.batch_id for m in alerts.expired()], ["exp"])
        self.assertEqual([m.batch_id for m in alerts.near_expiry()], ["soon"])
        self.assertEqual(sorted(alerts.low_stock()), [("X", "V", 0), ("X", "W", 5)])
        self.assertEqual([m.batch_id for m in alerts.flagged()], ["fine"])


if __name__ == "__main__":
    unittest.main()
