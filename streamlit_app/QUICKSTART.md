# Quick Start Guide - RAG Evaluation Dashboard

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (First Time Only)
```bash
cd streamlit_app
pip install -r requirements.txt
```

### Step 2: Start Ollama (Keep Running)
```bash
# In a separate terminal
ollama serve

# Then pull the model (one time)
ollama pull gemma3:1b
```

### Step 3: Launch Dashboard
```bash
streamlit run app.py
```

## 🎯 Using the Dashboard

### Basic Workflow
1. **Upload PDF** (sidebar) → Choose your document
2. **Enter Query** → What do you want to know?
3. **Add Reference** → Ground truth for comparison
4. **Click "Run Pipeline"** → Watch the magic happen!
5. **Explore Tabs** → Analyze results across 5 views

### Example Query
```
Query: "What is the VaR confidence interval and current portfolio allocation strategy?"

Reference: "The portfolio tracks a 95% confidence interval VaR that potential weekly downside variance will not exceed 2.1%..."
```

## 📊 What You'll See

### Tab 1: PDF Analysis
- How many pages, tables, images
- Preview of extracted text
- Tables as DataFrames

### Tab 2: Vector Store
- All document chunks
- Which chunks were retrieved
- Similarity scores

### Tab 3: Summaries
- **RAG** - Answer using retrieved context
- **Non-RAG** - Answer using full document
- **Multi-view** - Bull/Bear/Neutral perspectives

### Tab 4: Metrics
- ROUGE, BLEU, BERTScore scores
- RAGAS faithfulness metrics
- Beautiful charts and graphs

### Tab 5: Export
- Download JSON results
- Get formatted report

## ⚙️ Advanced Options

### Adjust Settings (Sidebar Expanders)
- **Chunk Size** - Bigger chunks = more context per piece
- **Top K** - More chunks = more information retrieved
- **Models** - Change Ollama model if needed

### Test Before Running
Click "Test Ollama Connection" to verify setup

## 🐛 Common Issues

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# Check if model exists
ollama list
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Dashboard won't load
```bash
# Try a different port
streamlit run app.py --server.port 8502
```

## 💡 Tips

- **Start small** - Test with a 2-3 page PDF first
- **Save time** - Results are cached, re-runs are faster
- **Play with settings** - See how chunk size affects results
- **Export often** - Download your findings

## 📝 Example Documents

Works best with:
- Financial reports
- Research papers
- Technical documentation
- Any structured PDF with clear sections

## 🎓 Learn More

- **ROUGE/BLEU** - Traditional metrics (fail to catch hallucinations)
- **BERTScore** - Semantic similarity (better but incomplete)
- **RAGAS** - RAG-specific metrics (catches hallucinations!)

## 🆘 Need Help?

1. Check the README.md for detailed docs
2. Look at browser console (F12) for errors
3. Check terminal output for backend errors

---

**Ready to evaluate some RAG pipelines? Let's go! 🚀**