import heapq
from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, src, dest, distance):
        self.graph[src].append((dest, distance))
        self.graph[dest].append((src, distance))

    def dijkstra(self, start, end):
        pq = [(0, start, [])]
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == end:
                return (cost, path)
            for neighbor, dist in self.graph[node]:
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + dist, neighbor, path))
        return (float('inf'), [])