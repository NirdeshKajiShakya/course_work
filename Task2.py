import heapq
from typing import Dict, List, Tuple, Optional

# =====================================================================
# 1. GRAPH DATA STRUCTURE (Adjacency List)
# =====================================================================
class Graph:
    """
    Weighted Directed Graph representation using an Adjacency List.
    Designed for Transportation Network Optimization[cite: 1].
    """
    def __init__(self, is_directed: bool = True):
        self.is_directed: bool = is_directed
        self.adj: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(self, u: str, v: str, weight: float) -> None:
        """Adds a weighted directed edge from u to v."""
        if u not in self.adj: 
            self.adj[u] = []
        if v not in self.adj: 
            self.adj[v] = []
        self.adj[u].append((v, weight))
        
        if not self.is_directed:
            self.adj[v].append((u, weight))

    def get_vertices(self) -> List[str]:
        """Returns all vertex identifiers in the graph."""
        return list(self.adj.keys())

    def get_neighbors(self, u: str) -> List[Tuple[str, float]]:
        """Returns adjacency list entries for vertex u."""
        return self.adj.get(u, [])

    def get_all_edges(self) -> List[Tuple[str, str, float]]:
        """Returns a flat list of all directed edges as (u, v, weight)."""
        edges = []
        for u in self.adj:
            for v, w in self.adj[u]:
                edges.append((u, v, w))
        return edges


# =====================================================================
# 2. ALGORITHM IMPLEMENTATIONS
# =====================================================================

def dijkstra(graph: Graph, start: str) -> Dict[str, float]:
    """
    Computes single-source shortest paths for non-negative edge weights[cite: 1].
    Time Complexity: O(|E| log |V|)[cite: 1]
    """
    dist = {v: float('inf') for v in graph.get_vertices()}
    dist[start] = 0
    pq = [(0, start)]  # (distance, node)
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if d > dist[u]:
            continue
            
        for v, w in graph.get_neighbors(u):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
                
    return dist


def prim_mst(graph: Graph, start: str) -> Dict[str, float]:
    """
    Computes the Minimum Spanning Tree (MST) key values for backbone minimization[cite: 1].
    Time Complexity: O(|E| log |V|)[cite: 1]
    """
    key = {v: float('inf') for v in graph.get_vertices()}
    in_mst = {v: False for v in graph.get_vertices()}
    key[start] = 0
    pq = [(0, start)]  # (weight, node)
    
    while pq:
        w_curr, u = heapq.heappop(pq)
        
        if in_mst[u]:
            continue
        in_mst[u] = True
        
        for v, w in graph.get_neighbors(u):
            if not in_mst[v] and w < key[v]:
                key[v] = w
                heapq.heappush(pq, (w, v))
                
    return key


def bellman_ford(graph: Graph, start: str) -> Dict[str, float]:
    """
    Computes shortest paths under real-valued weights and detects negative cycles[cite: 1].
    Time Complexity: O(|V| * |E|)[cite: 1]
    """
    dist = {v: float('inf') for v in graph.get_vertices()}
    dist[start] = 0
    edges = graph.get_all_edges()
    vertices = graph.get_vertices()
    
    # Relax edges |V| - 1 times
    for _ in range(len(vertices) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:  # Early stop optimization
            break
            
    # Check for negative-weight cycles
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            raise ValueError("Graph contains a negative-weight cycle.")
            
    return dist


# =====================================================================
# 3. EXECUTION / BENCHMARKING ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    # Initialize a sample transport network graph
    g = Graph(is_directed=True)
    g.add_edge("City_A", "City_B", 5.0)
    g.add_edge("City_B", "City_C", 2.0)
    g.add_edge("City_A", "City_C", 10.0)
    g.add_edge("City_C", "City_D", 3.0)
    
    print("Vertices:", g.get_vertices())
    print("Dijkstra from City_A:", dijkstra(g, "City_A"))
    print("Prim's MST from City_A:", prim_mst(g, "City_A"))
    print("Bellman-Ford from City_A:", bellman_ford(g, "City_A"))

#Benchmarking and performance analysis can be added here for larger graphs.
import random
import time

def generate_random_graph(num_nodes: int, num_edges: int, is_directed: bool = True) -> Graph:
    """Generates a random connected graph with non-negative weights."""
    g = Graph(is_directed=is_directed)
    nodes = [f"N_{i}" for i in range(num_nodes)]
    
    # Ensure connectivity (Line graph backbone)
    for i in range(num_nodes - 1):
        g.add_edge(nodes[i], nodes[i+1], random.uniform(1.0, 50.0))
        
    # Fill remaining edges randomly
    current_edges = num_nodes - 1
    while current_edges < num_edges:
        u, v = random.sample(nodes, 2)
        g.add_edge(u, v, random.uniform(1.0, 50.0))
        current_edges += 1
        
    return g

def benchmark_algorithms(runs: int = 5):
    test_cases = [
        ("Sparse", 1000, 3000),
        ("Dense", 1000, 100000),
        ("Large Sparse", 10000, 40000)
    ]
    
    print(f"{'Category':<15} | {'|V|, |E|':<18} | {'Dijkstra (ms)':<15} | {'Prim (ms)':<15} | {'Bellman-Ford (ms)':<15}")
    print("-" * 85)
    
    for name, v_count, e_count in test_cases:
        g = generate_random_graph(v_count, e_count)
        start_node = "N_0"
        
        # 1. Benchmark Dijkstra
        t0 = time.perf_counter()
        for _ in range(runs): dijkstra(g, start_node)
        dijkstra_ms = ((time.perf_counter() - t0) / runs) * 1000
        
        # 2. Benchmark Prim
        t0 = time.perf_counter()
        for _ in range(runs): prim_mst(g, start_node)
        prim_ms = ((time.perf_counter() - t0) / runs) * 1000
        
        # 3. Benchmark Bellman-Ford (Limit runs on dense graphs if slow)
        bf_runs = 1 if name == "Large Sparse" else runs
        t0 = time.perf_counter()
        for _ in range(bf_runs): bellman_ford(g, start_node)
        bf_ms = ((time.perf_counter() - t0) / bf_runs) * 1000
        
        print(f"{name:<15} | {f'({v_count}, {e_count})':<18} | {dijkstra_ms:<15.2f} | {prim_ms:<15.2f} | {bf_ms:<15.2f}")

if __name__ == "__main__":
    benchmark_algorithms()