import time
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# ==========================================
# 1. SEQUENTIAL MERGE SORT
# ==========================================
def merge(left, right):
    """Merges two sorted sub-lists into a single sorted list."""
    result = []
    i = j = 0
    len_left, len_right = len(left), len(right)
    
    while i < len_left and j < len_right:
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort_sequential(arr):
    """Standard recursive sequential merge sort implementation."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_sequential(arr[:mid])
    right = merge_sort_sequential(arr[mid:])
    return merge(left, right)

# ==========================================
# 2. CONCURRENT PARALLEL MERGE SORT
# ==========================================
def parallel_merge_sort(arr, num_threads=4):
    """
    Parallel Merge Sort utilizing ProcessPoolExecutor to bypass Python GIL.
    Splits data into chunks across worker processes and performs multi-way merge.
    """
    n = len(arr)
    if num_threads <= 1 or n <= 1000:
        return merge_sort_sequential(arr)
    
    # Calculate chunk sizes for parallel worker processes
    chunk_size = math.ceil(n / num_threads)
    chunks = [arr[i:i + chunk_size] for i in range(0, n, chunk_size)]
    
    # Phase 1: Parallel sorting of sub-arrays across worker processes
    with ProcessPoolExecutor(max_workers=num_threads) as executor:
        sorted_chunks = list(executor.map(merge_sort_sequential, chunks))
    
    # Phase 2: Sequential multi-way reduction merge phase
    while len(sorted_chunks) > 1:
        next_level = []
        for i in range(0, len(sorted_chunks), 2):
            if i + 1 < len(sorted_chunks):
                next_level.append(merge(sorted_chunks[i], sorted_chunks[i + 1]))
            else:
                next_level.append(sorted_chunks[i])
        sorted_chunks = next_level
        
    return sorted_chunks[0]

# ==========================================
# 3. PLOTTING FUNCTION (DYNAMIC EMPIRICAL DATA)
# ==========================================
def plot_results(thread_counts, observed_speedups, dataset_size, parallel_fraction=0.85):
    """Generates and saves the Speedup Graph using actual benchmark measurements."""
    threads = np.array(thread_counts)
    obs_speedup = np.array(observed_speedups)
    
    # Theoretical Models
    ideal_speedup = threads
    amdahl_speedup = 1 / ((1 - parallel_fraction) + (parallel_fraction / threads))

    # Figure Styling
    plt.figure(figsize=(8, 5), dpi=300)
    plt.plot(threads, ideal_speedup, 'k--', label='Ideal Linear Speedup ($S = T$)', linewidth=1.5)
    plt.plot(threads, amdahl_speedup, 'r:', label=f"Amdahl's Law ($p={parallel_fraction}$)", linewidth=2)
    plt.plot(threads, obs_speedup, 'b-o', label='Observed Speedup (Empirical)', linewidth=2.5, markersize=8)

    # Graph Formatting
    plt.title(f'Parallel Merge Sort: Speedup vs. Thread Count (N = {dataset_size:,})', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Number of Threads ($T$)', fontsize=11, labelpad=8)
    plt.ylabel('Speedup Factor ($S$)', fontsize=11, labelpad=8)
    plt.xticks(threads)
    plt.yticks(range(1, max(thread_counts) + 1))
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()

    # Save plot for report
    filename = 'task5_speedup_graph.png'
    plt.savefig(filename, dpi=300)
    print(f"\n[+] Speedup graph dynamically generated and saved as '{filename}'.")
    plt.show()

# ==========================================
# 4. BENCHMARK SUITE & DRIVER
# ==========================================
def run_benchmarks(dataset_size=1000000, thread_counts=[1, 2, 4, 8]):
    """Executes benchmarks, prints formatted tables, and triggers graph generation."""
    print(f"\n{'='*75}")
    print(f" TASK 5 CONCURRENT PROGRAMMING BENCHMARK SUITE (N = {dataset_size:,}) ")
    print(f"{'='*75}")
    
    # Generate random test dataset
    print(f"[*] Generating random dataset of {dataset_size:,} integers...")
    random.seed(42)  # Fixed seed for deterministic testing
    raw_data = [random.randint(1, 10_000_000) for _ in range(dataset_size)]
    
    # Validate correctness
    print("[*] Validating implementation correctness...")
    data_copy = raw_data[:10000]
    expected = sorted(data_copy)
    actual = parallel_merge_sort(data_copy, num_threads=2)
    assert actual == expected, "Error: Parallel sort output does not match expected output!"
    print("[+] Correctness check passed successfully.\n")

    # Benchmarking
    base_time = None
    observed_speedups = []

    print("-" * 75)
    print(f"{'Threads':<10} | {'Time (ms)':<15} | {'Speedup (S)':<15} | {'Efficiency (E)':<15}")
    print("-" * 75)

    for num_threads in thread_counts:
        # Time the execution
        start_time = time.perf_counter()
        _ = parallel_merge_sort(raw_data, num_threads=num_threads)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000.0
        
        if num_threads == 1:
            base_time = elapsed_ms
            speedup = 1.00
            efficiency = 100.0
        else:
            speedup = base_time / elapsed_ms
            efficiency = (speedup / num_threads) * 100.0

        observed_speedups.append(speedup)

        print(f"{num_threads:<10} | {elapsed_ms:<15.2f} | {speedup:<15.2f}x | {efficiency:<14.1f}%")

    print("-" * 75)

    # Plot the exact measured speedup
    plot_results(thread_counts, observed_speedups, dataset_size)

if __name__ == "__main__":
    run_benchmarks(dataset_size=1000000, thread_counts=[1, 2, 4, 8])