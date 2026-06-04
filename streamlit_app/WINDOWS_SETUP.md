# Windows Setup Guide - PyTorch DLL Fix

## 🔧 The Issue

You're encountering a PyTorch DLL initialization error on Windows. This is a common issue with PyTorch installations that include CUDA libraries when you only need CPU support.

**Error:** `OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed`

## ✅ Solution: Install CPU-Only PyTorch

### Option 1: Automated Fix (Recommended)

Run the installation script that handles PyTorch correctly:

```batch
cd streamlit_app
install_windows.bat
```

This script will:
1. Create virtual environment
2. Install PyTorch CPU version (no CUDA)
3. Install all other dependencies in correct order

### Option 2: Manual Fix

If you already have the virtual environment:

```batch
cd streamlit_app
fix_torch_windows.bat
```

This will:
1. Uninstall existing PyTorch
2. Install CPU-only version
3. Reinstall sentence-transformers

### Option 3: Completely Fresh Start

```batch
# Remove existing virtual environment
rmdir /s /q venv

# Run installation script
install_windows.bat
```

## 🔍 Why This Happens

The default PyTorch installation includes CUDA libraries (for GPU support) which require specific Visual C++ redistributables. When these DLLs are missing or incompatible, you get the initialization error.

**The fix:** Install PyTorch with CPU-only wheels, which don't require CUDA DLLs.

## 📦 Manual Installation Steps

If scripts don't work, follow these manual steps:

### 1. Create Virtual Environment
```batch
python -m venv venv
venv\Scripts\activate.bat
```

### 2. Upgrade pip
```batch
python -m pip install --upgrade pip
```

### 3. Install PyTorch CPU-only (IMPORTANT!)
```batch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 4. Verify PyTorch Installation
```batch
python -c "import torch; print(torch.__version__)"
```

Should output something like: `2.1.0+cpu`

### 5. Install Remaining Dependencies
```batch
pip install streamlit==1.31.0
pip install sentence-transformers==2.2.2
pip install chromadb==0.4.18
pip install PyMuPDF==1.23.26 pdfplumber==0.10.3
pip install requests==2.31.0
pip install rouge-score==0.1.2 evaluate==0.4.1 datasets==2.14.6
pip install bert-score==0.3.13
pip install plotly==5.18.0
pip install numpy==1.24.3 pandas==2.0.3
```

### 6. Test Installation
```batch
python -c "from sentence_transformers import SentenceTransformer; print('Success!')"
```

### 7. Launch Dashboard
```batch
streamlit run app.py
```

## 🚀 Quick Commands Summary

```batch
# Fresh installation
cd streamlit_app
install_windows.bat

# Fix existing installation
cd streamlit_app
fix_torch_windows.bat

# Run dashboard
cd streamlit_app
run.bat

# Or manually
cd streamlit_app
venv\Scripts\activate.bat
streamlit run app.py
```

## 🐛 Alternative Solutions

### If Scripts Don't Work

#### Check Python Version
```batch
python --version
```
Requires Python 3.8 or higher

#### Check pip Version
```batch
python -m pip --version
```
Should be pip 20.0 or higher

#### Install Visual C++ Redistributables
If CPU-only PyTorch still fails, install Microsoft Visual C++ Redistributables:
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart computer
- Re-run installation

#### Use Conda Instead (Alternative)
```batch
conda create -n rag_env python=3.10
conda activate rag_env
conda install pytorch torchvision cpuonly -c pytorch
pip install -r requirements.txt
streamlit run app.py
```

## ✅ Verification Checklist

After installation, verify each component:

```batch
# Activate environment
venv\Scripts\activate.bat

# Test PyTorch
python -c "import torch; print('PyTorch:', torch.__version__)"

# Test SentenceTransformers
python -c "from sentence_transformers import SentenceTransformer; print('SentenceTransformers: OK')"

# Test ChromaDB
python -c "import chromadb; print('ChromaDB: OK')"

# Test Streamlit
python -c "import streamlit; print('Streamlit: OK')"

# Test PDF libraries
python -c "import fitz, pdfplumber; print('PDF libraries: OK')"

# Test evaluation libraries
python -c "from rouge_score import rouge_scorer; import evaluate; print('Eval libraries: OK')"
```

If all tests pass, you're ready to run the dashboard!

## 🎯 Expected Output

After successful installation:

```
PyTorch: 2.1.0+cpu
SentenceTransformers: OK
ChromaDB: OK
Streamlit: OK
PDF libraries: OK
Eval libraries: OK
```

## 📝 Common Errors and Fixes

### Error: "No module named 'torch'"
**Fix:** Run `pip install torch --index-url https://download.pytorch.org/whl/cpu`

### Error: "DLL load failed while importing _C"
**Fix:** Uninstall and reinstall PyTorch CPU version (see Option 2 above)

### Error: "Cannot find specified module"
**Fix:** Install Visual C++ Redistributables (see Alternative Solutions)

### Error: "Permission denied"
**Fix:** Run Command Prompt as Administrator

## 🔄 Clean Reinstall Procedure

If nothing works, start completely fresh:

```batch
# 1. Delete everything
cd streamlit_app
rmdir /s /q venv
rmdir /s /q chroma_store

# 2. Fresh install
install_windows.bat

# 3. Verify
venv\Scripts\activate.bat
python -c "import torch, streamlit, sentence_transformers; print('All OK!')"

# 4. Run
streamlit run app.py
```

## 💡 Tips

1. **Always use CPU version** - You don't need GPU for this application
2. **Install PyTorch first** - Before sentence-transformers
3. **Use scripts** - They handle installation order correctly
4. **Keep environment clean** - Don't mix conda and pip environments
5. **Update Windows** - Some DLLs require recent Windows updates

## 🆘 Still Having Issues?

If the error persists after trying all solutions:

1. **Check Python installation**
   ```batch
   where python
   python --version
   ```

2. **Try different Python version** (3.9 or 3.10 work best)
   ```batch
   py -3.9 -m venv venv
   ```

3. **Use the working original environment**
   - If your original pipeline.py works, use that environment
   ```batch
   # From RAG root directory
   .venv\Scripts\activate.bat
   cd streamlit_app
   streamlit run app.py
   ```

4. **Copy working packages**
   ```batch
   # If .venv works, copy torch files
   xcopy /E /I .venv\Lib\site-packages\torch streamlit_app\venv\Lib\site-packages\torch
   ```

## ✅ Success Indicators

You'll know it worked when:
1. No DLL errors appear
2. Streamlit dashboard opens in browser
3. Can load embedding model
4. Can run complete pipeline

---

**Need immediate fix?** Run `install_windows.bat` - it's tested and works on Windows 10/11!