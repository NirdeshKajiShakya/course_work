import time
import tracemalloc

class KnightsTour:
    def __init__(self, n=8):
        self.n = n
        # 8 possible legal moves for a chess knight
        self.move_x = [2, 1, -1, -2, -2, -1, 1, 2]
        self.move_y = [1, 2, 2, 1, -1, -2, -2, -1]
        self.states_explored = 0

    def is_valid(self, x, y, board):
        """Checks if (x, y) is within board boundaries and unvisited."""
        return 0 <= x < self.n and 0 <= y < self.n and board[x][y] == -1

    def count_onward_moves(self, x, y, board):
        """Counts remaining valid moves from (x, y) for Warnsdorff's heuristic."""
        count = 0
        for i in range(8):
            nx, ny = x + self.move_x[i], y + self.move_y[i]
            if self.is_valid(nx, ny, board):
                count += 1
        return count

    # ==========================================
    # PRUNED / HEURISTIC BACKTRACKING (WARNSDORFF)
    # ==========================================
    def solve_pruned(self, start_x=0, start_y=0):
        board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        board[start_x][start_y] = 0  # Start position step 0
        self.states_explored = 0

        if self._backtrack_pruned(start_x, start_y, 1, board):
            return board
        return None

    def _backtrack_pruned(self, curr_x, curr_y, move_count, board):
        self.states_explored += 1

        if move_count == self.n * self.n:
            return True

        # Collect legal next moves and sort by minimum onward degree (Warnsdorff's Rule)
        candidates = []
        for i in range(8):
            next_x = curr_x + self.move_x[i]
            next_y = curr_y + self.move_y[i]
            if self.is_valid(next_x, next_y, board):
                onward_degree = self.count_onward_moves(next_x, next_y, board)
                candidates.append((onward_degree, next_x, next_y))

        # Warnsdorff Pruning Constraint: Prioritize moves with FEWEST onward exits
        candidates.sort(key=lambda item: item[0])

        for _, next_x, next_y in candidates:
            board[next_x][next_y] = move_count
            if self._backtrack_pruned(next_x, next_y, move_count + 1, board):
                return True
            board[next_x][next_y] = -1  # Backtrack

        return False

    # ==========================================
    # UNPRUNED STANDARD BACKTRACKING
    # ==========================================
    def solve_unpruned(self, start_x=0, start_y=0):
        board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        board[start_x][start_y] = 0
        self.states_explored = 0

        if self._backtrack_unpruned(start_x, start_y, 1, board):
            return board
        return None

    def _backtrack_unpruned(self, curr_x, curr_y, move_count, board):
        self.states_explored += 1

        if move_count == self.n * self.n:
            return True

        # Standard unpruned order
        for i in range(8):
            next_x = curr_x + self.move_x[i]
            next_y = curr_y + self.move_y[i]
            if self.is_valid(next_x, next_y, board):
                board[next_x][next_y] = move_count
                if self._backtrack_unpruned(next_x, next_y, move_count + 1, board):
                    return True
                board[next_x][next_y] = -1

        return False


# ==========================================
# BENCHMARKING AND VERIFICATION SUITE
# ==========================================
def print_board(board):
    for row in board:
        print(" ".join(f"{val:3d}" for val in row))


if __name__ == "__main__":
    print("--- 1. KNIGHT'S TOUR VERIFICATION (8x8 Board) ---")
    tour_8x8 = KnightsTour(n=8)

    tracemalloc.start()
    t_start = time.perf_counter()

    solution_8x8 = tour_8x8.solve_pruned(0, 0)

    t_end = time.perf_counter()
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    pruned_time_ms = (t_end - t_start) * 1000
    pruned_mem_kb = peak_mem / 1024

    print("Completed Tour Grid (0 to 63):")
    print_board(solution_8x8)
    print(f"\nExecution Time: {pruned_time_ms:.2f} ms | States Explored: {tour_8x8.states_explored}")
    assert solution_8x8 is not None, "Tour failed!"
    print("Status: PASSED\n")

    print("--- 2. PRUNED vs UNPRUNED COMPARISON (5x5 Board) ---")
    # 5x5 board is used for comparative analysis because unpruned backtracking 
    # on an 8x8 board can take hours due to 8^64 worst-case state space explosion.
    tour_5x5 = KnightsTour(n=5)

    # Run Unpruned
    t_start = time.perf_counter()
    tour_5x5.solve_unpruned(0, 0)
    t_end = time.perf_counter()
    unpruned_time = (t_end - t_start) * 1000
    unpruned_states = tour_5x5.states_explored

    # Run Pruned
    t_start = time.perf_counter()
    tour_5x5.solve_pruned(0, 0)
    t_end = time.perf_counter()
    pruned_time = (t_end - t_start) * 1000
    pruned_states = tour_5x5.states_explored

    print(f"{'Strategy (5x5 Board)':<28} | {'States Explored':<18} | {'Execution Time (ms)':<20}")
    print("-" * 72)
    print(f"{'Unpruned Backtracking':<28} | {unpruned_states:<18} | {unpruned_time:<20.2f}")
    print(f"{'Pruned (Warnsdorff Heuristic)':<28} | {pruned_states:<18} | {pruned_time:<20.2f}")

    speedup = unpruned_states / pruned_states if pruned_states > 0 else 1
    print(f"\nState Space Reduction Factor: {speedup:.1f}x reduction on 5x5 board!")