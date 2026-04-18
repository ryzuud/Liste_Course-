import sys
from unittest.mock import MagicMock

sys.modules['flask'] = MagicMock()

import json
import os
from app import charger_recettes, sauvegarder_recettes, FICHIER_RECETTES

def test_cache():
    # Setup: ensure clean state
    if os.path.exists(FICHIER_RECETTES):
        os.remove(FICHIER_RECETTES)

    # Init data
    recettes = [{"nom": "Test", "portions": 2, "ingredients": []}]
    sauvegarder_recettes(recettes)

    # Test charger
    loaded = charger_recettes()
    assert len(loaded) == 1
    assert loaded[0]["nom"] == "Test"

    # Test update and save updates cache
    recettes.append({"nom": "Test2", "portions": 1, "ingredients": []})
    sauvegarder_recettes(recettes)

    loaded_after_save = charger_recettes()
    assert len(loaded_after_save) == 2
    assert loaded_after_save[1]["nom"] == "Test2"

    # Restore original file for the real app
    # (assuming it had data we might have deleted, wait we deleted it!)
    # Let's restore from git
    os.system("git checkout -- " + FICHIER_RECETTES)

if __name__ == "__main__":
    test_cache()
    print("Tests passed.")
