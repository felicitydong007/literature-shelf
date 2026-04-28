@echo off
cd /d D:\download_papers
.\.venv\Scripts\python.exe scan_papers.py --refresh-all
pause
