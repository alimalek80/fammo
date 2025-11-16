@echo off
REM Build Tailwind CSS for production (minified)

echo ========================================
echo   Building Tailwind CSS (Production)
echo ========================================
echo.

.\tailwindcss.exe -i .\static\src\input.css -o .\static\css\output.css --minify

echo.
echo Build complete! Output: static\css\output.css
echo.
pause
