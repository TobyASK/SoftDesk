# Guide d'exécution des tests - SoftDesk

Ce projet contient une suite de tests complète avec 34 tests couvrant tous les aspects de l'API.

## Prérequis

- Python 3.12+
- Environnement virtuel créé: `.venv`
- Dépendances installées (pytest, django, djangorestframework, etc.)

## Installation de l'environnement

```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows:
.venv\Scripts\activate.bat
# Sur Linux/macOS:
source .venv/bin/activate

# Installer les dépendances
pip install -e .
```

## Exécution des tests

### Option 1: Script Python (recommandé - multiplateforme)

```bash
# Tous les tests avec résumé
python run_tests.py

# Avec options pytest
python run_tests.py -q              # Quiet mode
python run_tests.py -v              # Verbose mode
python run_tests.py --cov           # Avec couverture de code
python run_tests.py -x              # S'arrêter au premier échec
```

### Option 2: Script batch Windows

```bash
run_tests.cmd
```

### Option 3: Script shell Linux/macOS

```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Option 4: Commande directe pytest

```bash
# Tous les tests
pytest -v

# Mode quiet
pytest -q

# Avec couverture de code
pytest --cov=. --cov-report=html

# Un fichier spécifique
pytest tests/test_accounts.py -v

# Un test spécifique
pytest tests/test_accounts.py::TestUserRegistration::test_register_valid_user -v

# S'arrêter au premier échec
pytest -x

# Avec traceback court
pytest --tb=short
```

## Résultats des tests

La suite de tests SoftDesk contient:

### Tests des comptes (15 tests)
- ✅ Enregistrement des utilisateurs
- ✅ Authentification JWT
- ✅ Gestion des profils utilisateur
- ✅ Validation RGPD (âge >= 15)

### Tests du tracker (19 tests)
- ✅ Gestion des projets
- ✅ Gestion des contributeurs
- ✅ Gestion des issues
- ✅ Gestion des commentaires
- ✅ Permissions et sécurité OWASP

**Total: 34 tests, couverture 86%**

## Interprétation des résultats

```
34 passed in 20.11s  ✅ Tous les tests réussissent
34 failed            ❌ Tous les tests échouent
15 passed, 19 failed ⚠️  Certains tests échouent
```

## Fichiers de configuration

- `pytest.ini` - Configuration de pytest
- `pyproject.toml` - Configuration du projet et dépendances
- `.env` - Variables d'environnement (voir `.env.example`)

## Couverture de code

Pour générer un rapport de couverture HTML:

```bash
pytest --cov=. --cov-report=html
# Ouvrir htmlcov/index.html
```

## Debugging

Pour plus de détails en cas de test échoué:

```bash
# Verbose très détaillé
pytest -vv

# Avec traceback long
pytest --tb=long

# Afficher les prints dans les tests
pytest -s

# Combiné
pytest -vvs --tb=long
```

## Dépannage courant

**"pytest command not found"**
```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  (Windows)
source .venv/bin/activate  (Linux/macOS)

# Réinstaller les dépendances
pip install -e .
```

**"DJANGO_SETTINGS_MODULE not found"**
```bash
# Le fichier pytest.ini configure automatiquement Django
# Si problème, vérifier que pytest.ini existe à la racine
```

**Tests lents**
```bash
# Utiliser -x pour s'arrêter au premier échec
pytest -x
```

## Tests continus (CI/CD)

Pour intégrer les tests dans une pipeline CI/CD:

```bash
# Commande simple
pytest --tb=short -v

# Avec couverture et JUnit XML
pytest --cov=. --junitxml=test-results.xml --cov-report=xml
```
