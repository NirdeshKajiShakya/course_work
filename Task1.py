import sys
import time
import random
from typing import List, Optional, Tuple

# Increase recursion depth for unbalanced BST degradation tests on large N
sys.setrecursionlimit(20000)

# ==========================================
# 1. DATA MODEL
# ==========================================
class City:
    """Represents a city node entry."""
    __slots__ = ('city_id', 'name', 'lat', 'lon', 'population')
    
    def __init__(self, city_id: int, name: str, lat: float, lon: float, population: int):
        self.city_id = city_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.population = population

def generate_city_dataset(size: int, sorted_by_id: bool = False) -> List[City]:
    """Generates synthetic city data in random or sorted order."""
    ids = list(range(1, size + 1))
    if not sorted_by_id:
        random.shuffle(ids)
        
    return [
        City(
            city_id=cid,
            name=f"City_{cid}",
            lat=round(random.uniform(26.0, 30.0), 4),
            lon=round(random.uniform(80.0, 88.0), 4),
            population=random.randint(1000, 1000000)
        )
        for cid in ids
    ]

# ==========================================
# 2. DATA STRUCTURES
# ==========================================

# --- BINARY SEARCH TREE ---
class BSTNode:
    __slots__ = ('city', 'left', 'right')
    def __init__(self, city: City):
        self.city = city
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None

class BinarySearchTree:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, city: City) -> None:
        new_node = BSTNode(city)
        if not self.root:
            self.root = new_node
            return
        
        curr = self.root
        while True:
            if city.city_id < curr.city.city_id:
                if curr.left is None:
                    curr.left = new_node
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = new_node
                    break
                curr = curr.right

    def search(self, city_id: int) -> Optional[City]:
        curr = self.root
        while curr:
            if curr.city.city_id == city_id:
                return curr.city
            elif city_id < curr.city.city_id:
                curr = curr.left
            else:
                curr = curr.right
        return None


# --- AVL TREE ---
class AVLNode:
    __slots__ = ('city', 'left', 'right', 'height')
    def __init__(self, city: City):
        self.city = city
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1

class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _rotate_right(self, z: AVLNode) -> AVLNode:
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _rotate_left(self, z: AVLNode) -> AVLNode:
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def insert(self, city: City) -> None:
        self.root = self._insert_recursive(self.root, city)

    def _insert_recursive(self, node: Optional[AVLNode], city: City) -> AVLNode:
        if not node:
            return AVLNode(city)

        if city.city_id < node.city.city_id:
            node.left = self._insert_recursive(node.left, city)
        else:
            node.right = self._insert_recursive(node.right, city)

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Left Left
        if balance > 1 and city.city_id < node.left.city.city_id:
            return self._rotate_right(node)
        # Right Right
        if balance < -1 and city.city_id > node.right.city.city_id:
            return self._rotate_left(node)
        # Left Right
        if balance > 1 and city.city_id > node.left.city.city_id:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # Right Left
        if balance < -1 and city.city_id < node.right.city.city_id:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, city_id: int) -> Optional[City]:
        curr = self.root
        while curr:
            if curr.city.city_id == city_id:
                return curr.city
            elif city_id < curr.city.city_id:
                curr = curr.left
            else:
                curr = curr.right
        return None


# --- MIN HEAP ---
class MinHeap:
    def __init__(self):
        self.heap: List[City] = []

    def insert(self, city: City) -> None:
        self.heap.append(city)
        self._bubble_up(len(self.heap) - 1)

    def search(self, city_id: int) -> Optional[City]:
        # Linear search for Min-Heap
        for city in self.heap:
            if city.city_id == city_id:
                return city
        return None

    def _bubble_up(self, index: int) -> None:
        parent = (index - 1) // 2
        while index > 0 and self.heap[index].city_id < self.heap[parent].city_id:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            index = parent
            parent = (index - 1) // 2


# --- CHAINING HASH TABLE ---
class HashNode:
    __slots__ = ('key', 'value', 'next')
    def __init__(self, key: int, value: City):
        self.key = key
        self.value = value
        self.next: Optional['HashNode'] = None

class ChainingHashTable:
    def __init__(self, capacity: int = 10007):
        self.capacity = capacity
        self.buckets: List[Optional[HashNode]] = [None] * capacity

    def _hash(self, key: int) -> int:
        return key % self.capacity

    def insert(self, city: City) -> None:
        index = self._hash(city.city_id)
        new_node = HashNode(city.city_id, city)
        
        if not self.buckets[index]:
            self.buckets[index] = new_node
            return

        curr = self.buckets[index]
        while curr:
            if curr.key == city.city_id:
                curr.value = city
                return
            if not curr.next:
                break
            curr = curr.next
        curr.next = new_node

    def search(self, city_id: int) -> Optional[City]:
        index = self._hash(city_id)
        curr = self.buckets[index]
        while curr:
            if curr.key == city_id:
                return curr.value
            curr = curr.next
        return None
    

#

import matplotlib.pyplot as plt

def benchmark_execution(sizes=[100, 1000, 10000]):
    data_structures = {
        "BST": BinarySearchTree,
        "AVL": AVLTree,
        "Min-Heap": MinHeap,
        "Hash Table": lambda: ChainingHashTable(capacity=15000)
    }

    # Tracking storage for results
    results = {ds_name: {"random_ins": [], "sorted_ins": [], "search": []} for ds_name in data_structures}

    print(f"{'Structure':<12} | {'N':<6} | {'Order':<8} | {'Insert (ms)':<12} | {'Search (ms)':<12}")
    print("-" * 60)

    for size in sizes:
        target_search_ids = [random.randint(1, size) for _ in range(500)]

        for is_sorted in [False, True]:
            dataset = generate_city_dataset(size, sorted_by_id=is_sorted)
            order_str = "Sorted" if is_sorted else "Random"

            for ds_name, ds_cls in data_structures.items():
                ds_instance = ds_cls()

                # Measure Insertion Time
                t_start = time.perf_counter()
                for city in dataset:
                    ds_instance.insert(city)
                t_end = time.perf_counter()
                insert_ms = (t_end - t_start) * 1000.0

                # Measure Search Time (Average over 500 lookups)
                t_start = time.perf_counter()
                for sid in target_search_ids:
                    _ = ds_instance.search(sid)
                t_end = time.perf_counter()
                search_ms = (t_end - t_start) * 1000.0

                if is_sorted:
                    results[ds_name]["sorted_ins"].append(insert_ms)
                else:
                    results[ds_name]["random_ins"].append(insert_ms)
                    results[ds_name]["search"].append(search_ms)

                print(f"{ds_name:<12} | {size:<6} | {order_str:<8} | {insert_ms:<12.3f} | {search_ms:<12.3f}")

    plot_benchmark_results(sizes, results)

def plot_benchmark_results(sizes, results):
    """Generates clean line charts using Matplotlib."""
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)

    markers = {'BST': 'o', 'AVL': 's', 'Min-Heap': '^', 'Hash Table': 'D'}
    colors = {'BST': '#e74c3c', 'AVL': '#3498db', 'Min-Heap': '#2ecc71', 'Hash Table': '#9b59b6'}

    # Chart 1: Insertion Time (Random Dataset)
    for ds_name in results:
        axes[0].plot(sizes, results[ds_name]["random_ins"], label=ds_name, 
                    marker=markers[ds_name], color=colors[ds_name], linewidth=2)
    axes[0].set_title("Insertion Time (Random Data)", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Dataset Size (N)", fontsize=10)
    axes[0].set_ylabel("Time (milliseconds)", fontsize=10)
    axes[0].set_xscale('log')
    axes[0].legend()

    # Chart 2: Insertion Time (Sorted Dataset - Highlighting BST Degeneration)
    for ds_name in results:
        axes[1].plot(sizes, results[ds_name]["sorted_ins"], label=ds_name, 
                    marker=markers[ds_name], color=colors[ds_name], linewidth=2)
    axes[1].set_title("Insertion Time (Sorted Data - Degradation)", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Dataset Size (N)", fontsize=10)
    axes[1].set_ylabel("Time (milliseconds)", fontsize=10)
    axes[1].set_xscale('log')
    axes[1].legend()

    # Chart 3: Search Overhead Performance
    for ds_name in results:
        axes[2].plot(sizes, results[ds_name]["search"], label=ds_name, 
                    marker=markers[ds_name], color=colors[ds_name], linewidth=2)
    axes[2].set_title("Lookup Time (500 Random Queries)", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Dataset Size (N)", fontsize=10)
    axes[2].set_ylabel("Time (milliseconds)", fontsize=10)
    axes[2].set_xscale('log')
    axes[2].legend()

    plt.tight_layout()
    plt.savefig("data_structure_benchmarks.png", dpi=300)
    print("\n[+] Success: Line graphs rendered and saved to 'data_structure_benchmarks.png'")
    plt.show()

if __name__ == "__main__":
    benchmark_execution()