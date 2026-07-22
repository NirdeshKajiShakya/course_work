import bisect
import random
import time
import tracemalloc

# ==========================================
# CORE ALGORITHM IMPLEMENTATION
# ==========================================
def weighted_job_scheduling(jobs):
    """
    Computes the maximum profit for a set of non-overlapping jobs using Dynamic Programming.
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    # Sort jobs by finish time: O(n log n)
    jobs.sort(key=lambda x: x['finish'])
    n = len(jobs)
    
    finish_times = [j['finish'] for j in jobs]
    dp = [0] * (n + 1)
    
    for i in range(1, n + 1):
        # Binary search for predecessor p(i): O(log n)
        p_i = bisect.bisect_right(finish_times, jobs[i - 1]['start'], hi=i - 1)
        
        # Recurrence: Max of excluding job i OR including job i + dp[p_i]
        dp[i] = max(dp[i - 1], jobs[i - 1]['profit'] + dp[p_i])
        
    return dp[n]


# ==========================================
# VERIFICATION & BENCHMARKING SUITE
# ==========================================
def run_verification_test():
    """Runs a known test case to prove algorithmic correctness."""
    print("--- 1. VERIFICATION TEST ---")
    sample_jobs = [
        {'start': 1, 'finish': 3, 'profit': 50},
        {'start': 2, 'finish': 5, 'profit': 20},
        {'start': 4, 'finish': 6, 'profit': 70},
        {'start': 6, 'finish': 7, 'profit': 30},
        {'start': 5, 'finish': 8, 'profit': 110},
        {'start': 7, 'finish': 9, 'profit': 60}
    ]
    max_profit = weighted_job_scheduling(sample_jobs)
    print(f"Sample Jobs Input Count: {len(sample_jobs)}")
    print(f"Computed Maximum Profit: {max_profit}")
    assert max_profit == 210, "Logic Error: Expected 210!"
    print("Status: PASSED (Correct optimal path found)\n")


def generate_random_jobs(num_jobs):
    """Generates synthetic valid job datasets for testing."""
    random.seed(42)  # Fixed seed for reproducible benchmarks
    jobs = []
    for _ in range(num_jobs):
        start = random.randint(1, 100000)
        duration = random.randint(1, 100)
        profit = random.randint(10, 500)
        jobs.append({'start': start, 'finish': start + duration, 'profit': profit})
    return jobs


def run_empirical_benchmarks():
    """Measures wall-clock execution time and memory usage across dataset sizes."""
    print("--- 2. EMPIRICAL BENCHMARK RESULTS ---")
    sizes = [100, 1000, 10000]
    
    print(f"{'Node Count (N)':<15} | {'Execution Time (ms)':<20} | {'Peak Memory (KB)':<18}")
    print("-" * 60)
    
    for n in sizes:
        dataset = generate_random_jobs(n)
        
        # Start tracking time and memory
        tracemalloc.start()
        t_start = time.perf_counter()
        
        result = weighted_job_scheduling(dataset)
        
        t_end = time.perf_counter()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed_time_ms = (t_end - t_start) * 1000
        peak_mem_kb = peak_mem / 1024
        
        print(f"{n:<15} | {elapsed_time_ms:<20.3f} | {peak_mem_kb:<18.2f}")


if __name__ == "__main__":
    run_verification_test()
    run_empirical_benchmarks()