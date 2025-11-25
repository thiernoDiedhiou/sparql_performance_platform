@echo off
echo Nettoyage du cache Streamlit...
rmdir /s /q .streamlit 2>nul
rmdir /s /q __pycache__ 2>nul

echo Lancement de l'application...
streamlit run main.py --server.port 8501
