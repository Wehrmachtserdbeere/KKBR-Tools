@echo off

echo Installing Python requirements...
pip install -r requirements.txt

echo.
echo Installing Playwright Chromium...
playwright install chromium

echo.
echo Setup complete.
pause