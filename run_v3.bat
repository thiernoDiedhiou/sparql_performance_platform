@echo off
REM Script de lancement de SPARQL Performance Platform v3.0
REM Design professionnel et cohérent

echo ===============================================================================
echo    SPARQL Performance Platform v3.0 - Design Professionnel
echo ===============================================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.8+ depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Activer l'environnement virtuel si disponible
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
    echo [OK] Environnement virtuel active
    echo.
) else (
    echo [WARNING] Environnement virtuel non trouve
    echo [INFO] Utilisation de Python global
    echo.
)

REM Vérifier que Streamlit est installé
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Streamlit n'est pas installe
    echo.
    echo Installation de Streamlit...
    pip install streamlit
    echo.
)

echo [INFO] Demarrage de la plateforme v3.0...
echo.
echo ===============================================================================
echo    Acces: http://localhost:8501
echo    Version: 3.0 - Design Professionnel
echo    Appuyez sur Ctrl+C pour arreter
echo ===============================================================================
echo.

REM Lancer Streamlit avec main_v3.py
streamlit run main_v3.py

pause
