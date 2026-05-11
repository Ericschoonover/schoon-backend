@echo off
.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
