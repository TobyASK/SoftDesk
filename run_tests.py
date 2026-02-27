#!/usr/bin/env python
"""
Script pour exécuter tous les tests SoftDesk avec pytest.
Compatible avec Windows, Linux et macOS.
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Exécute la suite de tests SoftDesk."""
    
    # Vérifier que nous sommes dans le bon répertoire
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Récupérer le Python de l'environnement virtuel
    venv_path = project_root / ".venv"
    
    if not venv_path.exists():
        print("❌ Erreur: L'environnement virtuel .venv n'existe pas.")
        print("Créez-le d'abord avec: python -m venv .venv")
        return 1
    
    # Chemin du Python dans l'environnement virtuel
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print(f"❌ Erreur: Python n'a pas pu être trouvé dans {python_exe}")
        return 1
    
    # Vérifier que pytest est installé
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "show", "pytest"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("📦 Installation des dépendances...")
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "-q", "-e", "."],
            check=True
        )
    
    # Afficher le header
    print()
    print("=" * 40)
    print("   Exécution des tests SoftDesk")
    print("=" * 40)
    print()
    
    # Exécuter pytest
    cmd = [str(python_exe), "-m", "pytest", "-v", "--tb=short"] + sys.argv[1:]
    result = subprocess.run(cmd)
    
    # Afficher le statut final
    print()
    print("=" * 40)
    if result.returncode == 0:
        print("   ✅ Tous les tests ont réussi!")
    else:
        print("   ❌ Certains tests ont échoué!")
    print("=" * 40)
    print()
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
