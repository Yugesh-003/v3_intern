@echo off
echo ========================================
echo RAG Evaluation Dashboard
echo Using Existing Working Environment
echo ========================================
echo.

REM Activate the working .venv environment
call .venv\Scripts\activate.bat

REM Check if Streamlit is installed
python -c "import streamlit" 2>NUL
if errorlevel 1 (
    echo Streamlit not found. Installing...
    pip install streamlit==1.31.0 plotly==5.18.0
    echo.
)

echo Starting dashboard...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

REM Navigate to streamlit app and run
cd streamlit_app
streamlit run app.py

pause