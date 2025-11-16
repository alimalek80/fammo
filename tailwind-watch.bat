@echo off
REM Tailwind CSS Watch Mode for FAMMO
REM This script runs Tailwind in watch mode, automatically rebuilding CSS when you make changes

echo ========================================
echo   FAMMO - Tailwind CSS Watch Mode
echo ========================================
echo.
echo This will monitor your templates and rebuild CSS automatically.
echo Press Ctrl+C to stop watching.
echo.

.\tailwindcss.exe -i .\static\src\input.css -o .\static\css\output.css --watch
