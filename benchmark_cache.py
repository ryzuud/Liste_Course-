import sys
from unittest.mock import MagicMock

sys.modules['flask'] = MagicMock()

import time
import os
import json
from app import FICHIER_RECETTES

_RECETTES_CACHE = None
_RECETTES_CACHE_MTIME = 0.0

def charger_recettes_cached() -> list[dict]:
    global _RECETTES_CACHE, _RECETTES_CACHE_MTIME
    try:
        current_mtime = os.path.getmtime(FICHIER_RECETTES)
    except OSError:
        current_mtime = 0.0

    if _RECETTES_CACHE is not None and current_mtime == _RECETTES_CACHE_MTIME:
        return _RECETTES_CACHE

    with open(FICHIER_RECETTES, "r", encoding="utf-8") as f:
        data = json.load(f)

    _RECETTES_CACHE = data.get("recettes", [])
    _RECETTES_CACHE_MTIME = current_mtime
    return _RECETTES_CACHE

def run_benchmark():
    start_time = time.time()
    iterations = 10000
    for _ in range(iterations):
        charger_recettes_cached()
    end_time = time.time()

    total_time = end_time - start_time
    print(f"Time for {iterations} calls: {total_time:.4f} seconds")
    print(f"Average time per call: {total_time / iterations * 1000:.4f} ms")

if __name__ == "__main__":
    run_benchmark()
