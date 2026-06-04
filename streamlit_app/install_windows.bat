@echo off
echo ========================================
echo Windows Installation Script
echo RAG Evaluation Dashboard
echo ========================================
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ========================================
echo Installing dependencies...
echo This may take a few minutes
echo ========================================
echo.

REM Step 1: Upgrade pip
echo [1/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Step 2: Install PyTorch CPU version first (fixes DLL issues)
echo [2/4] Installing PyTorch (CPU version for Windows)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo.

REM Step 3: Install sentence-transformers and other ML dependencies
echo [3/4] Installing ML libraries...
pip install sentence-transformers==2.2.2 chromadb==0.4.18
echo.

REM Step 4: Install remaining dependencies
echo [4/4] Installing remaining packages...
pip install streamlit==1.31.0 PyMuPDF==1.23.26 pdfplumber==0.10.3 requests==2.31.0 rouge-score==0.1.2 evaluate==0.4.1 datasets==2.14.6 bert-score==0.3.13 plotly==5.18.0 numpy==1.24.3 pandas==2.0.3
echo.

echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To launch the dashboard, run:
echo     run.bat
echo.
echo Or manually:
echo     venv\Scripts\activate.bat
echo     streamlit run app.py
echo.

pause