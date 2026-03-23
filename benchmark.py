"""
benchmark.py
Experimentos de rendimiento del sistema de persistencia.
Inserta N registros y mide:
  - Tiempo de inserción
  - Tiempo de búsqueda
  - Colisiones acumuladas
  - Factor de carga final
  - Número de rehashes

Genera resultados en benchmark_results.json.
"""

import time
import json
import os
import sys

# Ajustar path para ejecución directa
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence.hash_table import HashTable
from persistence.engine import PersistenceEngine


def benchmark_hash_table(n: int, capacity: int = 16) -> dict:
    """
    Prueba la tabla hash en memoria pura (sin I/O de disco).
    """
    ht = HashTable(capacity=capacity)

    # ── Inserción ────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    for i in range(n):
        ht.put(f"key:{i}", i * 10)
    t_insert = time.perf_counter() - t0

    stats_after_insert = ht.stats()

    # ── Búsqueda ─────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    hits = 0
    for i in range(n):
        v = ht.get(f"key:{i}")
        if v is not None:
            hits += 1
    t_search = time.perf_counter() - t0

    # ── Eliminación (10%) ────────────────────────────────────────────────
    t0 = time.perf_counter()
    for i in range(0, n, 10):
        ht.delete(f"key:{i}")
    t_delete = time.perf_counter() - t0

    return {
        "n": n,
        "insert_time_ms":  round(t_insert * 1000, 4),
        "search_time_ms":  round(t_search * 1000, 4),
        "delete_time_ms":  round(t_delete * 1000, 4),
        "insert_per_sec":  round(n / t_insert),
        "search_per_sec":  round(n / t_search),
        "hits":            hits,
        "collisions":      stats_after_insert["total_collisions"],
        "rehash_count":    stats_after_insert["rehash_count"],
        "final_capacity":  stats_after_insert["capacity"],
        "final_load_factor": stats_after_insert["load_factor"],
        "max_chain_length": stats_after_insert["max_chain_length"],
    }


def benchmark_persistence_engine(n: int) -> dict:
    """
    Prueba el motor completo con I/O de disco real.
    Usa archivos temporales que se limpian al terminar.
    """
    data_path  = f"_bench_data_{n}.log"
    index_path = f"_bench_index_{n}.bin"

    try:
        engine = PersistenceEngine(data_path, index_path)

        # ── Inserción con disco ───────────────────────────────────────────
        t0 = time.perf_counter()
        for i in range(n):
            engine.save(f"bench:{i}", {"value": i, "data": "x" * 20}, "benchmark")
        t_insert = time.perf_counter() - t0

        # ── Lectura con disco ─────────────────────────────────────────────
        t0 = time.perf_counter()
        hits = 0
        sample = min(n, 500)   # muestra para no tardar demasiado en 20000
        step   = max(1, n // sample)
        for i in range(0, n, step):
            v = engine.get(f"bench:{i}")
            if v is not None:
                hits += 1
        t_search = time.perf_counter() - t0

        # ── Reconstrucción del índice ─────────────────────────────────────
        index_store_path = index_path
        if os.path.exists(index_store_path):
            os.remove(index_store_path)

        t0 = time.perf_counter()
        engine.force_rebuild()
        t_rebuild = time.perf_counter() - t0

        stats = engine.stats()

        return {
            "n": n,
            "insert_time_ms":   round(t_insert * 1000, 3),
            "search_time_ms":   round(t_search * 1000, 3),
            "rebuild_time_ms":  round(t_rebuild * 1000, 3),
            "insert_per_sec":   round(n / t_insert),
            "collisions":       stats["total_collisions"],
            "rehash_count":     stats["rehash_count"],
            "final_capacity":   stats["capacity"],
            "final_load_factor":stats["load_factor"],
            "data_file_bytes":  stats["data_file_size_bytes"],
        }
    finally:
        for f in [data_path, index_path]:
            if os.path.exists(f):
                os.remove(f)


def run_all_benchmarks():
    sizes = [1000, 5000, 20000]
    results = {
        "hash_table_only": [],
        "full_engine":     [],
    }

    print("=" * 60)
    print("  VOID RUNNER — BENCHMARK DE RENDIMIENTO")
    print("=" * 60)

    print("\n[1/2] Tabla Hash en memoria pura")
    print("-" * 50)
    for n in sizes:
        print(f"  Insertando {n:,} registros...", end=" ", flush=True)
        r = benchmark_hash_table(n)
        results["hash_table_only"].append(r)
        print(f"✓  {r['insert_time_ms']:.1f} ms insert | "
              f"{r['search_time_ms']:.1f} ms search | "
              f"{r['collisions']} colisiones | "
              f"rehash x{r['rehash_count']} | "
              f"LF={r['final_load_factor']:.3f}")

    print("\n[2/2] Motor completo con I/O de disco")
    print("-" * 50)
    for n in sizes:
        print(f"  Insertando {n:,} registros en disco...", end=" ", flush=True)
        r = benchmark_persistence_engine(n)
        results["full_engine"].append(r)
        print(f"✓  {r['insert_time_ms']:.1f} ms insert | "
              f"{r['search_time_ms']:.1f} ms search | "
              f"rebuild {r['rebuild_time_ms']:.1f} ms | "
              f"{r['data_file_bytes']:,} bytes")

    # Guardar resultados
    out_path = "benchmark_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Resultados guardados en {out_path}")
    print("=" * 60)
    return results


if __name__ == "__main__":
    run_all_benchmarks()
