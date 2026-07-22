import random
import time
import tracemalloc

# ==========================================
# CORE ALGORITHM IMPLEMENTATION
# ==========================================
def find_min_platforms(arrival, departure):
    """
    Finds the minimum number of platforms required at a train station using a Greedy strategy.
    Time Complexity: O(n log n)
    Space Complexity: O(1) auxiliary space (modifies copies in-place)
    """
    # Sort arrival and departure arrays independently: O(n log n)
    arrival.sort()
    departure.sort()
    
    n = len(arrival)
    platforms = 0
    max_platforms = 0
    i = 0
    j = 0
    
    # Process events in chronological order
    while i < n and j < n:
        if arrival[i] <= departure[j]:
            platforms += 1
            max_platforms = max(max_platforms, platforms)
            i += 1
        else:
            platforms -= 1
            j += 1
            
    return max_platforms


# ==========================================
# VERIFICATION & BENCHMARKING SUITE
# ==========================================
def run_verification_test():
    """Runs a standard test case to verify mathematical correctness."""
    print("--- 1. VERIFICATION TEST ---")
    # Arrival and Departure times represented in 24-hour clock format (e.g., 900 = 09:00)
    arrivals = [900, 940, 950, 1100, 1500, 1800]
    departures = [910, 1200, 1120, 1130, 1900, 2000]
    
    result = find_min_platforms(arrivals, departures)
    print(f"Arrivals:   {arrivals}")
    print(f"Departures: {departures}")
    print(f"Computed Minimum Platforms Needed: {result}")
    
    assert result == 3, "Verification Failed: Expected 3 platforms!"
    print("Status: PASSED (Optimal platform allocation verified)\n")


def generate_random_train_schedule(num_trains):
    """Generates synthetic train arrival and departure times."""
    random.seed(42)  # Fixed seed for consistent timing comparisons
    arrivals = []
    departures = []
    
    for _ in range(num_trains):
        arr = random.randint(0, 86000)  # Seconds from midnight
        duration = random.randint(300, 7200)  # Train stay between 5 mins and 2 hours
        dep = arr + duration
        arrivals.append(arr)
        departures.append(dep)
        
    return arrivals, departures


def run_empirical_benchmarks():
    """Measures wall-clock execution time and memory usage across dataset sizes."""
    print("--- 2. EMPIRICAL BENCHMARK RESULTS ---")
    sizes = [100, 1000, 10000]
    
    print(f"{'Train Count (N)':<15} | {'Execution Time (ms)':<20} | {'Peak Memory (KB)':<18}")
    print("-" * 60)
    
    for n in sizes:
        arr, dep = generate_random_train_schedule(n)
        
        tracemalloc.start()
        t_start = time.perf_counter()
        
        result = find_min_platforms(arr, dep)
        
        t_end = time.perf_counter()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed_time_ms = (t_end - t_start) * 1000
        peak_mem_kb = peak_mem / 1024
        
        print(f"{n:<15} | {elapsed_time_ms:<20.3f} | {peak_mem_kb:<18.2f}")


if __name__ == "__main__":
    run_verification_test()
    run_empirical_benchmarks()