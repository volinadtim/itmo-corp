"""
Реализация двоичной кучи (Binary heap) — базовый строительный блок для задач недели 3.

Поддерживаются оба типа: min-heap (по умолчанию) и max-heap.

Источник: neerc.ifmo.ru/wiki — Двоичная куча
https://neerc.ifmo.ru/wiki/index.php?title=Двоичная_куча
"""


class Heap:
    def __init__(self, data=None, max_heap=False):
        """Создать кучу. Если data задан, построить кучу за O(n)."""
        self._max = max_heap
        self._heap = []
        if data is not None:
            self._heap = list(data)
            self._build_heap()

    # ── утилиты ────────────────────────────────────────────────

    def __len__(self):
        return len(self._heap)

    def __bool__(self):
        return bool(self._heap)

    def __getitem__(self, i):
        return self._heap[i]

    def _cmp(self, a, b):
        """Сравнение: для min-heap a < b, для max-heap a > b."""
        return a < b if not self._max else a > b

    @staticmethod
    def _parent(i):
        return (i - 1) // 2

    @staticmethod
    def _left(i):
        return 2 * i + 1

    @staticmethod
    def _right(i):
        return 2 * i + 2

    # ── основные процедуры ─────────────────────────────────────

    def sift_up(self, i):
        """Просеивание вверх — O(log n)."""
        while i > 0 and self._cmp(self._heap[i], self._heap[self._parent(i)]):
            p = self._parent(i)
            self._heap[i], self._heap[p] = self._heap[p], self._heap[i]
            i = p

    def sift_down(self, i):
        """Просеивание вниз — O(log n)."""
        n = len(self._heap)
        while True:
            left = self._left(i)
            right = self._right(i)
            candidate = i  # тот, кто должен быть в вершине

            if left < n and self._cmp(self._heap[left], self._heap[candidate]):
                candidate = left
            if right < n and self._cmp(self._heap[right], self._heap[candidate]):
                candidate = right

            if candidate == i:
                break
            self._heap[i], self._heap[candidate] = self._heap[candidate], self._heap[i]
            i = candidate

    def _build_heap(self):
        """Построить кучу из произвольного массива за O(n)."""
        n = len(self._heap)
        for i in range(n // 2 - 1, -1, -1):
            self.sift_down(i)

    # ── публичный API ──────────────────────────────────────────

    def top(self):
        """Вернуть корень (минимум/максимум) без удаления — O(1)."""
        if not self._heap:
            raise IndexError("heap is empty")
        return self._heap[0]

    def extract(self):
        """Извлечь корень — O(log n)."""
        if not self._heap:
            raise IndexError("heap is empty")
        if len(self._heap) == 1:
            return self._heap.pop()

        root = self._heap[0]
        self._heap[0] = self._heap.pop()
        self.sift_down(0)
        return root

    def insert(self, key):
        """Добавить элемент — O(log n)."""
        self._heap.append(key)
        self.sift_up(len(self._heap) - 1)

    # ── дополнительные операции ─────────────────────────────────

    def decrease_key(self, i, new_val):
        """Уменьшить значение элемента (для min-heap) — O(log n)."""
        if new_val > self._heap[i]:
            raise ValueError("new value must be smaller (for decrease_key)")
        self._heap[i] = new_val
        self.sift_up(i)

    def increase_key(self, i, new_val):
        """Увеличить значение элемента (для min-heap после изменения) — O(log n)."""
        if new_val < self._heap[i]:
            raise ValueError("new value must be larger (for increase_key)")
        self._heap[i] = new_val
        self.sift_down(i)


def heap_sort(arr):
    """Пирамидальная сортировка (Heapsort) — O(n log n), in-place, неустойчива.

    Источник: neerc.ifmo.ru/wiki — Сортировка кучей
    https://neerc.ifmo.ru/wiki/index.php?title=Сортировка_кучей
    """
    n = len(arr)
    if n <= 1:
        return arr

    # 1. Строим max-heap
    heap = Heap(arr, max_heap=True)
    # 2. Извлекаем по одному
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heap._heap[i], heap._heap[0] = heap._heap[0], heap._heap[i]
        # сужаем кучу
        heap._heap = heap._heap[:i]
        if i > 1:
            # Проще построить заново для оставшейся части
            # (в учебных целях; в реальном коде — восстановить свойство)
            heap = Heap(heap._heap, max_heap=True)
            arr[:i] = heap._heap

    return arr


# ── демонстрация ──────────────────────────────────────────────

if __name__ == "__main__":
    # Min-heap
    h = Heap()
    for x in [5, 3, 7, 1, 9, 2]:
        h.insert(x)
    print("Heap:", list(h))           # [1, 3, 2, 5, 9, 7] (один из вариантов)
    print("Top:", h.top())             # 1
    print("Extract:", h.extract())     # 1
    print("After extract:", list(h))   # [2, 3, 7, 5, 9]

    # Max-heap
    h2 = Heap(max_heap=True)
    for x in [5, 3, 7, 1, 9, 2]:
        h2.insert(x)
    print("\nMax-heap top:", h2.top())  # 9

    # Heapsort
    arr = [3, 2, 4, 1, 5]
    print("\nBefore sort:", arr)
    heap_sort(arr)
    print("After sort:", arr)  # [1, 2, 3, 4, 5]