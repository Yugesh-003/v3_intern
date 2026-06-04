@echo off
echo ========================================
echo RAG Evaluation Dashboard Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run: install_windows.bat
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Verifying dependencies...
python -c "import streamlit" 2>NUL
if errorlevel 1 (
    echo Dependencies not installed!
    echo Please run: install_windows.bat
    echo.
    pause
    exit /b 1
)
echo.

REM Launch Streamlit
echo ========================================
echo Starting dashboard...
echo Dashboard will open at: http://localhost:8501
echo ========================================
echo.
echo If you get a PyTorch DLL error, press Ctrl+C and run:
echo     fix_torch_windows.bat
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause