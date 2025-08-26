@echo off
REM Aller dans le dossier du projet
cd /d C:\Users\user\Desktop\projet

REM Activer l'environnement virtuel (si tu en as un)
call venv\Scripts\activate

REM Définir les variables Flask
set FLASK_APP=app.py
set FLASK_ENV=development

REM Lancer Flask
flask run --host=127.0.0.1 --port=5000

pause
