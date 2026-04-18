import sys
from unittest.mock import MagicMock

sys.modules['flask'] = MagicMock()

import time
from app import charger_recettes

def run_benchmark():
    start_time = time.time()
    iterations = 10000
    for _ in range(iterations):
        charger_recettes()
    end_time = time.time()

    total_time = end_time - start_time
    print(f"Time for {iterations} calls: {total_time:.4f} seconds")
    print(f"Average time per call: {total_time / iterations * 1000:.4f} ms")

if __name__ == "__main__":
    run_benchmark()
