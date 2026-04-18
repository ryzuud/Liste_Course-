import timeit
from collections import defaultdict
import json
import os

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")

def load_data():
    with open(FICHIER_RECETTES, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("recettes", [])

def test_original(selection):
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    noms_originaux: dict[tuple[str, str], str] = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            cle = (ing["nom"].lower().strip(), ing["unite"].lower().strip())
            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = ing["nom"]
    return comptes, noms_originaux

def test_optimized(selection):
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    noms_originaux: dict[tuple[str, str], str] = {}

    cache_nom = {}
    cache_unite = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            nom = ing["nom"]
            unite = ing["unite"]

            if nom not in cache_nom:
                cache_nom[nom] = nom.lower().strip()
            nom_norm = cache_nom[nom]

            if unite not in cache_unite:
                cache_unite[unite] = unite.lower().strip()
            unite_norm = cache_unite[unite]

            cle = (nom_norm, unite_norm)

            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = nom
    return comptes, noms_originaux

data = load_data()

# Ensure semantics are strictly identical
comptes_orig, noms_orig = test_original(data)
comptes_opt, noms_opt = test_optimized(data)

assert comptes_orig == comptes_opt
assert noms_orig == noms_opt

# Performance test
large_data = data * 1000

def bench_old():
    test_original(large_data)

def bench_new():
    test_optimized(large_data)

if __name__ == '__main__':
    t_old = timeit.timeit(bench_old, number=100)
    t_new = timeit.timeit(bench_new, number=100)
    print(f"Original: {t_old:.4f}s")
    print(f"Optimized: {t_new:.4f}s")
    improvement = (t_old - t_new) / t_old * 100
    print(f"Improvement: {improvement:.2f}%")
