@echo off
title Landslide Detection Server
color 0A
echo ========================================
echo  Landslide Detection System
echo ========================================
echo.
echo Starting server...
echo Server will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
cd /d "D:\data cience\lanslide detection intenship project"
myvenv\Scripts\python.exe app.py
echo.
echo Server stopped.
pause
