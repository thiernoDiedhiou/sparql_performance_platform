@echo off
cls
echo.
echo ===============================================================================
echo    SPARQL Performance Platform v3.1 - Interface Ultra-Professionnelle
echo ===============================================================================
echo.
echo    Changements majeurs v3.1 :
echo      - Navigation simplifiee (5 onglets au lieu de 8)
echo      - Actions rapides integrees dans la sidebar
echo      - Monitoring systeme permanent
echo      - Overlays pour Guide et Dashboard
echo      - Interface fluide et coherente
echo.
echo ===============================================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python est installe
echo.

REM Vérifier que Streamlit est installé
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Streamlit n'est pas installe
    echo.
    echo Installation de Streamlit en cours...
    pip install streamlit
    echo.
)

echo [OK] Streamlit est installe
echo.

REM Vérifier que psutil est installé (pour le monitoring)
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation de psutil pour le monitoring systeme...
    pip install psutil
    echo.
)

echo [OK] psutil est installe (monitoring actif)
echo.

echo ===============================================================================
echo    Lancement de la plateforme v3.1...
echo ===============================================================================
echo.

REM Lancer Streamlit avec la nouvelle version
streamlit run main_v3_refactored.py

pause
