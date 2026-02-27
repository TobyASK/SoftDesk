@echo off
REM Script de preparation et lancement du projet SoftDesk
REM Effectue toutes les etapes apres le git clone

setlocal enabledelayedexpansion

echo.
echo =====================================
echo   SoftDesk - Setup and Launch Script
echo =====================================
echo.

REM Verifier et installer Poetry si necessaire
python -m poetry --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation de Poetry...
    python -m pip install poetry
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer Poetry.
        pause
        exit /b 1
    )
    echo [OK] Poetry installe
    echo.
) else (
    echo [OK] Poetry detecte
    echo.
)

REM Configurer Poetry pour eviter les chemins trop longs
echo [INFO] Configuration de Poetry...
python -m poetry config virtualenvs.in-project true
python -m poetry config virtualenvs.path "%CD%\.venv"

REM Etape 1 : Creer le fichier .env s'il n'existe pas
if not exist ".env" (
    echo [INFO] Creation du fichier .env...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Fichier .env cree depuis .env.example
        echo.
        echo [ATTENTION] Editez .env et changez SECRET_KEY pour la production
        echo.
    ) else (
        echo [ERREUR] Fichier .env.example non trouve.
        pause
        exit /b 1
    )
) else (
    echo [OK] Fichier .env existe deja
    echo.
)

REM Etape 2 : Installer les dependances
if not exist ".venv" (
    echo [INFO] Installation des dependances avec Poetry...
    python -m poetry install
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances.
        pause
        exit /b 1
    )
    echo [OK] Dependances installes
    echo.
) else (
    echo [OK] Environnement virtuel Poetry existe deja
    echo.
)

REM Etape 3 : Appliquer les migrations
echo [INFO] Application des migrations...
python -m poetry run python manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Echec des migrations.
    pause
    exit /b 1
)
echo [OK] Migrations appliquees
echo.

REM Etape 4 : Optionnel - Creer un superutilisateur
set /p create_admin="Creer un superutilisateur ? (y/n) : "
if /i "!create_admin!"=="y" (
    echo [INFO] Creation du superutilisateur...
    python -m poetry run python manage.py createsuperuser
    echo.
)

REM Etape 5 : Lancer le serveur
echo [INFO] Lancement du serveur Django...
echo.
echo =====================================
echo   Serveur disponible a :
echo   - API      : http://localhost:8000/api/v1
echo   - Admin    : http://localhost:8000/admin
echo   - Browse   : http://localhost:8000
echo =====================================
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python -m poetry run python manage.py runserver
