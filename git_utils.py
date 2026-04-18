import os
import subprocess

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))

def _run_git(*args: str) -> subprocess.CompletedProcess:
    """Exécute une commande git dans le dossier du projet."""
    return subprocess.run(
        ["git"] + list(args),
        cwd=DOSSIER_PROJET,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
