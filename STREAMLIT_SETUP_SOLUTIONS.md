# Streamlit Dashboard - Setup Solutions for Windows

## 🎯 Choose Your Solution

You have **3 options** to fix the PyTorch DLL error and run the dashboard:

---

## ✅ SOLUTION 1: Use Your Existing Working Environment (EASIEST!)

**Best if:** Your original `pipeline.py` already works

### Steps:
```batch
# From project root (D:\V3_Internship\Code\RAG)
.venv\Scripts\activate.bat
pip install streamlit==1.31.0 plotly==5.18.0
cd streamlit_app
streamlit run app.py
```

### Or use the shortcut:
```batch
run_streamlit_dashboard.bat
```

**Time:** 2 minutes  
**Pros:** No new environment, uses working PyTorch  
**Cons:** None

---

## ✅ SOLUTION 2: Automated Windows Installation (RECOMMENDED FOR NEW ENV)

**Best if:** You want a separate environment for Streamlit

### Steps:
```batch
cd streamlit_app
install_windows.bat
```

Wait for installation (5-10 minutes), then:
```batch
run.bat
```

**Time:** 10 minutes  
**Pros:** Clean separate environment, automated  
**Cons:** Takes longer

---

## ✅ SOLUTION 3: Fix Existing Streamlit Environment

**Best if:** You already tried installing in `streamlit_app/venv`

### Steps:
```batch
cd streamlit_app
fix_torch_windows.bat
```

**Time:** 5 minutes  
**Pros:** Fixes current environment  
**Cons:** Requires existing venv

---

## 🚀 Quick Decision Guide

```
Do you have .venv working? 
  ├─ YES → Use SOLUTION 1 (run_streamlit_dashboard.bat)
  └─ NO
      ├─ Want new environment? → Use SOLUTION 2 (install_windows.bat)
      └─ Have streamlit_app/venv? → Use SOLUTION 3 (fix_torch_windows.bat)
```

---

## 📋 Detailed Instructions

### SOLUTION 1: Using Existing .venv (FASTEST)

#### Why This Works
Your `.venv` already has all the heavy dependencies working:
- PyTorch ✅
- sentence-transformers ✅
- ChromaDB ✅
- All evaluation libraries ✅

You only need to add Streamlit!

#### Complete Commands
```batch
# 1. Navigate to project root
cd D:\V3_Internship\Code\RAG

# 2. Activate working environment
.venv\Scripts\activate.bat

# 3. Install Streamlit (only if not already installed)
pip install streamlit==1.31.0 plotly==5.18.0

# 4. Verify
python -c "import streamlit, torch, sentence_transformers; print('✅ Ready!')"

# 5. Launch dashboard
cd streamlit_app
streamlit run app.py
```

#### Permanent Shortcut
Just double-click: `run_streamlit_dashboard.bat` (in root folder)

---

### SOLUTION 2: Fresh Installation (CLEAN START)

#### Why This Works
Installs PyTorch CPU version first, which doesn't have DLL dependencies.

#### Complete Commands
```batch
# 1. Navigate to streamlit app
cd streamlit_app

# 2. Run automated installation
install_windows.bat

# Wait for installation to complete (5-10 minutes)

# 3. Launch dashboard
run.bat
```

#### What the Script Does
1. Creates virtual environment
2. Installs PyTorch CPU-only (no CUDA DLLs)
3. Installs sentence-transformers
4. Installs all other dependencies in correct order

---

### SOLUTION 3: Fix Existing Environment

#### When to Use
If you already have `streamlit_app/venv` but it has the DLL error.

#### Complete Commands
```batch
# 1. Navigate to streamlit app
cd streamlit_app

# 2. Run fix script
fix_torch_windows.bat

# Wait for PyTorch reinstallation

# 3. Launch dashboard
run.bat
```

#### What the Script Does
1. Uninstalls problematic PyTorch
2. Installs PyTorch CPU version
3. Reinstalls sentence-transformers

---

## 🔍 Verification

After installation, test each component:

```batch
# Activate your environment
# (either .venv\Scripts\activate.bat or streamlit_app\venv\Scripts\activate.bat)

# Test PyTorch
python -c "import torch; print('PyTorch:', torch.__version__)"

# Test SentenceTransformers
python -c "from sentence_transformers import SentenceTransformer; print('SentenceTransformers: ✅')"

# Test Streamlit
python -c "import streamlit; print('Streamlit: ✅')"

# Test All Together
python -c "import torch, streamlit, sentence_transformers, chromadb; print('✅ All systems ready!')"
```

---

## 🐛 Troubleshooting

### Still Getting DLL Error?

#### Check 1: Python Version
```batch
python --version
```
Should be 3.8, 3.9, 3.10, or 3.11

#### Check 2: PyTorch Version
```batch
python -c "import torch; print(torch.__version__)"
```
Should end with `+cpu` (e.g., `2.1.0+cpu`)

#### Check 3: Install Visual C++ Redistributables
Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 💡 Recommended Approach

**For fastest setup:**

1. Try SOLUTION 1 first (use existing .venv)
2. If that doesn't work, use SOLUTION 2 (fresh install)
3. Read `streamlit_app/WINDOWS_SETUP.md` for detailed troubleshooting

---

## 🎯 Expected Success

After successful setup, you should see:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Dashboard will open automatically in your browser!

---

## 📚 Additional Resources

- **Full Windows Guide:** `streamlit_app/WINDOWS_SETUP.md`
- **Use Existing Environment:** `streamlit_app/USE_EXISTING_ENV.md`
- **Quick Start:** `streamlit_app/QUICKSTART.md`
- **Complete README:** `streamlit_app/README.md`

---

## ✅ Summary

**Fastest:** Use existing `.venv` → `run_streamlit_dashboard.bat`  
**Cleanest:** New environment → `cd streamlit_app && install_windows.bat`  
**Fix existing:** DLL error → `cd streamlit_app && fix_torch_windows.bat`

**All three solutions work - choose based on your preference!**