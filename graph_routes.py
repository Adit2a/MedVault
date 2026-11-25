from collections import defaultdict

from min_heap import MinHeap


class Graph:
    """Undirected weighted graph of facilities (adjacency list)."""

    def __init__(self):
        self.graph = defaultdict(list)

    def add_location(self, name):
        self.graph[name]  # touching a defaultdict creates the node

    def add_edge(self, src, dest, distance):
        if distance < 0:
            raise ValueError("Dijkstra needs non-negative distances")
        self.graph[src].append((dest, distance))
        self.graph[dest].append((src, distance))

    def dijkstra(self, source):
        """Single-source shortest paths.

        Returns (dist, prev): dist[node] is the shortest distance from
        source, prev[node] is the node before it on that path.
        O((V + E) log V) with the binary heap.
        """
        dist = {source: 0}
        prev = {}
        visited = set()
        pq = MinHeap([(0, source)], key=lambda e: e[0])

        while pq:
            d, node = pq.pop()
            if node in visited:
                continue  # stale entry; a shorter one was already processed
            visited.add(node)
            for neighbor, w in self.graph[node]:
                nd = d + w
                if nd < dist.get(neighbor, float("inf")):
                    dist[neighbor] = nd
                    prev[neighbor] = node
                    pq.push((nd, neighbor))
        return dist, prev

    @staticmethod
    def build_path(prev, source, target):
        """Walk prev[] back from target to source."""
        if target != source and target not in prev:
            return []
        path = [target]
        while path[-1] != source:
            path.append(prev[path[-1]])
        return path[::-1]

    def shortest_path(self, start, end):
        dist, prev = self.dijkstra(start)
        if end not in dist:
            return float("inf"), []
        return dist[end], self.build_path(prev, start, end)
