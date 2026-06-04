@echo off
echo ========================================
echo PyTorch DLL Fix for Windows
echo ========================================
echo.

call venv\Scripts\activate.bat

echo Uninstalling existing PyTorch...
pip uninstall torch torchvision torchaudio -y
echo.

echo Installing PyTorch CPU version (no CUDA)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo.

echo Reinstalling sentence-transformers...
pip uninstall sentence-transformers -y
pip install sentence-transformers==2.2.2
echo.

echo ========================================
echo Fix applied!
echo ========================================
echo.
echo Try running the app again:
echo     streamlit run app.py
echo.

pause