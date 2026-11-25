"""A binary min-heap written from scratch (no heapq).

Items are ordered by key(item). Ties are broken by insertion order, so the
heap is stable and never has to compare two items directly.

    push      O(log n)
    pop       O(log n)
    peek      O(1)
    build     O(n)   (bottom-up heapify)
"""


class MinHeap:
    def __init__(self, items=None, key=lambda x: x):
        self._key = key
        self._counter = 0
        self._data = []  # list of (key, insertion_order, item)
        if items:
            for item in items:
                self._data.append(self._entry(item))
            self._heapify()

    def _entry(self, item):
        entry = (self._key(item), self._counter, item)
        self._counter += 1
        return entry

    # ---- public API -------------------------------------------------

    def push(self, item):
        self._data.append(self._entry(item))
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty MinHeap")
        self._swap(0, len(self._data) - 1)
        _, _, item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item

    def peek(self):
        if not self._data:
            raise IndexError("peek from empty MinHeap")
        return self._data[0][2]

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    # ---- internals --------------------------------------------------

    def _heapify(self):
        # Sift down every internal node, last parent first: O(n) overall.
        for i in range(len(self._data) // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i][:2] < self._data[parent][:2]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and self._data[left][:2] < self._data[smallest][:2]:
                smallest = left
            if right < n and self._data[right][:2] < self._data[smallest][:2]:
                smallest = right
            if smallest == i:
                return
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]
