import math
import random
import time

# ==========================================
# 1. SYNTHETIC DATASET GENERATOR
# ==========================================
def generate_vrptw_instance(num_customers, seed=42):
    """
    Generates a reproducible VRPTW benchmark instance.
    Returns depot dict and a list of customer dicts.
    """
    random.seed(seed)
    
    depot = {
        'id': 0,
        'x': 50.0,
        'y': 50.0,
        'demand': 0,
        'a': 0.0,
        'b': 1000.0,
        'service': 0.0
    }
    
    customers = []
    for i in range(1, num_customers + 1):
        x = random.uniform(0.0, 100.0)
        y = random.uniform(0.0, 100.0)
        dist_from_depot = math.hypot(x - depot['x'], y - depot['y'])
        
        # Ensure arrival from depot is feasible
        earliest_start = round(dist_from_depot + random.uniform(0.0, 100.0), 2)
        latest_start = round(earliest_start + random.uniform(30.0, 100.0), 2)
        
        customers.append({
            'id': i,
            'x': x,
            'y': y,
            'demand': random.randint(10, 35),
            'a': earliest_start,
            'b': latest_start,
            'service': 10.0  # Fixed service duration per customer
        })
        
    return depot, customers


# ==========================================
# 2. HEURISTIC 1: GREEDY CONSTRUCTION (TW-NN)
# ==========================================
def greedy_tw_nn(depot, customers, capacity, gamma=1.0):
    """
    Time-Window Nearest Neighbor (TW-NN) Greedy Construction.
    Time Complexity: O(N^2), Space Complexity: O(N)
    """
    unvisited = list(range(len(customers)))
    routes = []
    
    while unvisited:
        route = [depot]
        curr_node = depot
        curr_time = 0.0
        curr_load = 0
        
        while unvisited:
            best_cand_idx = None
            best_cand_pos = -1
            best_cost = float('inf')
            
            for pos, cand_idx in enumerate(unvisited):
                c = customers[cand_idx]
                dist = math.hypot(curr_node['x'] - c['x'], curr_node['y'] - c['y'])
                arr_time = max(curr_time + dist, c['a'])
                
                # Check Capacity and Upper Time Window Feasibility
                if curr_load + c['demand'] <= capacity and arr_time <= c['b']:
                    wait_time = max(0.0, c['a'] - (curr_time + dist))
                    cost = dist + gamma * wait_time
                    if cost < best_cost:
                        best_cost = cost
                        best_cand_idx = cand_idx
                        best_cand_pos = pos
            
            if best_cand_idx is None:
                break  # Return to depot and launch a new route
                
            c = customers[best_cand_idx]
            dist = math.hypot(curr_node['x'] - c['x'], curr_node['y'] - c['y'])
            curr_time = max(curr_time + dist, c['a']) + c['service']
            curr_load += c['demand']
            
            route.append(c)
            curr_node = c
            unvisited.pop(best_cand_pos)
            
        route.append(depot)  # Complete route back at depot
        routes.append(route)
        
    return routes


# ==========================================
# 3. HEURISTIC 2: FEASIBILITY-PRESERVING 2-OPT
# ==========================================
def validate_and_cost_route(route):
    """
    Validates time window feasibility for a route and returns total distance.
    Returns float('inf') if any time window constraint is violated.
    """
    curr_time = 0.0
    total_dist = 0.0
    
    for idx in range(len(route) - 1):
        u, v = route[idx], route[idx + 1]
        dist = math.hypot(u['x'] - v['x'], u['y'] - v['y'])
        curr_time = max(curr_time + dist, v['a'])
        
        if curr_time > v['b']:
            return float('inf')  # Infeasible due to time window breach
            
        curr_time += v['service']
        total_dist += dist
        
    return total_dist


def local_search_2opt(routes):
    """
    Intra-route 2-Opt Local Search with Downstream Feasibility Checks.
    Time Complexity: O(k * N^3), Space Complexity: O(N)
    """
    improved_routes = []
    
    for route in routes:
        best_route = list(route)
        best_dist = validate_and_cost_route(best_route)
        improved = True
        
        while improved:
            improved = False
            # Nodes at index 0 and len-1 are the depot; operate on intermediate segment
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route) - 1):
                    # Construct 2-opt edge swap
                    candidate_route = best_route[:i] + best_route[i:j+1][::-1] + best_route[j+1:]
                    candidate_dist = validate_and_cost_route(candidate_route)
                    
                    if candidate_dist < best_dist - 1e-6:
                        best_dist = candidate_dist
                        best_route = candidate_route
                        improved = True
                        break
                if improved:
                    break
                    
        improved_routes.append(best_route)
        
    return improved_routes


# ==========================================
# 4. BENCHMARKING & EVALUATION HARNESS
# ==========================================
def calculate_solution_metrics(routes):
    """Computes total distance and total vehicle count for a solution."""
    total_dist = 0.0
    for r in routes:
        total_dist += validate_and_cost_route(r)
    return total_dist, len(routes)


def run_benchmarks():
    test_sizes = [25, 50, 100]
    fleet_capacity = 200
    
    print("=" * 95)
    print("ST5003CEM TASK 4: VRPTW HEURISTIC BENCHMARK EVALUATION")
    print("=" * 95)
    print(f"{'N':<5} | {'Metric':<18} | {'Greedy TW-NN (Heuristic 1)':<28} | {'2-Opt Local Search (Heuristic 2)':<28}")
    print("-" * 95)
    
    for N in test_sizes:
        depot, customers = generate_vrptw_instance(N, seed=42)
        
        # --- Benchmark Heuristic 1: Greedy TW-NN ---
        t0 = time.perf_counter()
        greedy_routes = greedy_tw_nn(depot, customers, capacity=fleet_capacity, gamma=1.0)
        t1 = time.perf_counter()
        greedy_time_ms = (t1 - t0) * 1000.0
        greedy_dist, greedy_vehicles = calculate_solution_metrics(greedy_routes)
        
        # --- Benchmark Heuristic 2: 2-Opt Local Search ---
        t0 = time.perf_counter()
        opt_routes = local_search_2opt(greedy_routes)
        t1 = time.perf_counter()
        opt_time_ms = ((t1 - t0) * 1000.0) + greedy_time_ms  # Total time includes construction
        opt_dist, opt_vehicles = calculate_solution_metrics(opt_routes)
        
        # Distance Improvement %
        dist_imp = ((greedy_dist - opt_dist) / greedy_dist) * 100.0
        
        # Display Results Row
        print(f"{N:<5} | Distance (km)      | {greedy_dist:<28.2f} | {opt_dist:<28.2f}")
        print(f"{'':<5} | Fleet Size (Veh)   | {greedy_vehicles:<28d} | {opt_vehicles:<28d}")
        print(f"{'':<5} | Wall-clock Time    | {greedy_time_ms:<25.3f} ms | {opt_time_ms:<25.3f} ms")
        print(f"{'':<5} | Improvement (%)    | {'Baseline':<28} | {dist_imp:<27.2f}%")
        print("-" * 95)


def print_sample_route_details():
    """Prints detailed route composition for N=25 instance."""
    N = 25
    capacity = 200
    depot, customers = generate_vrptw_instance(N, seed=42)
    
    greedy_routes = greedy_tw_nn(depot, customers, capacity=capacity)
    opt_routes = local_search_2opt(greedy_routes)
    
    print("\n" + "=" * 95)
    print(f"DETAILED ROUTE BREAKDOWN FOR SAMPLE INSTANCE (N = {N}, Capacity = {capacity})")
    print("=" * 95)
    
    for idx, route in enumerate(opt_routes, 1):
        node_sequence = " -> ".join([f"v{node['id']}" for node in route])
        route_dist = validate_and_cost_route(route)
        route_load = sum([node['demand'] for node in route])
        print(f"Route {idx}: {node_sequence}")
        print(f"         Distance: {route_dist:.2f} km | Total Demand Served: {route_load}/{capacity}\n")


if __name__ == "__main__":
    run_benchmarks()
    print_sample_route_details()