@echo off
echo ========================================
echo SPARQL Performance Platform v2.0
echo ========================================
echo.

REM Activer l'environnement virtuel
if exist venv\Scripts\activate.bat (
    echo [1/3] Activation environnement virtuel...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Environnement virtuel non trouve
    echo Utilisation de Python global
)

echo.
echo [2/3] Verification port 8501...

REM Tuer les processus existants sur le port 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill //PID %%a //F >nul 2>&1
)

echo Port 8501 disponible
echo.

echo [3/3] Lancement de l'application v2.0...
echo.
echo ========================================
echo Interface disponible sur:
echo http://localhost:8501
echo ========================================
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

streamlit run main_v2.py

pause
