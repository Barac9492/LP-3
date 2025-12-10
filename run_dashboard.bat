@echo off
REM Launch LP Monitoring Dashboard (Windows)

echo Starting LP Investment Monitoring Dashboard...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    pip install streamlit plotly
)

REM Launch dashboard
echo Launching dashboard on http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run dashboard.py
