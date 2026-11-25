# MedVault

A small medicine inventory and redistribution system for a network of warehouses, hospitals and clinics. It tracks medicine batches, raises alerts, and decides which batches to send where, using a custom min-heap and Dijkstra's algorithm.

Pure Python 3.8+, no dependencies.

```bash
python main.py                      # demo
python -m unittest test_medvault    # 17 tests
```

## What it does

- **Batch tracking.** Each batch has a quantity, expiry date, location, quality score (1 to 5) and optional *reserved* or *blocked* flags.
- **Dispatch rules.** Expired, blocked and empty batches are never shipped. Reserved stock is held back except in an emergency.
- **FEFO ordering.** Within a location, batches go out first-expiry-first-out, with higher quality breaking ties.
- **Distance-aware redistribution.** To fill a request at a facility, every reachable batch gets a cost of `days_until_expiry + distance_weight * km`, and batches are taken cheapest-first until the request is filled. A request that can't be filled reports its shortfall.
- **Emergency mode.** Reserved stock becomes available and distance is weighted 100x, so the nearest usable stock goes first.
- **Alerts.** Expired stock to dispose of, batches expiring within N days, low stock per location, and flagged batches.

## Data structures and algorithms

| Piece | Where | Complexity |
|---|---|---|
| Binary min-heap written from scratch (sift-up, sift-down, O(n) heapify, stable ties) | `min_heap.py` | push/pop O(log n), build O(n) |
| Dijkstra's single-source shortest paths, on that heap | `graph_routes.py` | O((V + E) log V) |
| Adjacency-list graph, roads are two-way | `graph_routes.py` | |
| Hash map `medicine name -> batches` | `inventory.py` | O(1) lookup by name |
| Greedy fulfilment from a min-heap of candidate batches | `redistribution.py` | O(B log B) for B batches |

Because roads are two-way, the redistributor runs Dijkstra **once from the destination** to get the distance to every source, rather than once per batch. A request costs one Dijkstra plus one heap pass over the batches: O((V + E) log V + B log B).

## Files

- `min_heap.py`: the `MinHeap` class
- `medicine.py`: `Medicine` (one batch) and the dispatch rules
- `inventory.py`: batch storage, FEFO ordering, stock counts, receiving transfers
- `graph_routes.py`: facility graph and Dijkstra
- `redistribution.py`: the greedy, distance-aware `Redistributor`
- `alerts.py`: expiry, low-stock and flag alerts
- `main.py`: demo (dates are relative to today, so it never goes stale)
- `test_medvault.py`: unit tests

## Known limits and next steps

- The greedy choice is not globally optimal across several simultaneous requests; that would be a min-cost flow problem.
- Travel time isn't modelled, so a batch that would expire in transit could still be picked.
- Inventory lives in memory; a real system would persist it.
