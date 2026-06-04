# My Journey Through AI Evaluation: An Internship Report
## Exploring How We Can Trust AI-Generated Answers in Critical Domains

**Internship Project:** Summarization and Contextualization (LLM Logic Team)  
**Duration:** June 2026  
**Student Reflection**

---

## 1. Introduction

When I first started my internship with the LLM Logic Team, I had a simple but profound question: *How do we know if an AI is telling the truth?* This question became increasingly urgent as I learned that large language models (LLMs) were being deployed in high-stakes environments—finance, healthcare, legal services—where a single error could have serious consequences.

Throughout this internship, I embarked on a journey to understand how we evaluate AI-generated answers, particularly in Retrieval-Augmented Generation (RAG) systems. I explored various evaluation metrics, conducted experiments, built a working prototype, and discovered some uncomfortable truths about the limitations of current evaluation techniques. This report documents my learning journey, the challenges I faced, and the insights I gained along the way.

---

## 2. Project Background and Objectives

My internship project focused on a critical problem in AI systems: **Can we reliably distinguish between a correct answer and a plausible but wrong answer?** This might sound simple, but as I would soon discover, it's one of the most challenging problems in AI evaluation today.

The project objectives were clear:
- Study existing evaluation metrics used in RAG systems
- Understand how these metrics work and where they fail
- Create a case study with different types of AI responses (correct, partially correct, and hallucinated)
- Compare manual and automated evaluation approaches
- Investigate the role of context windows in answer quality
- Build a practical system to demonstrate these concepts

What excited me most about this project was its real-world relevance. I wasn't just learning theory; I was investigating a problem that affects how AI systems are deployed in production environments where accuracy matters.

---

## 3. Understanding RAG and LLM Evaluation

### What I Learned About RAG Systems

Before this internship, I had heard about RAG but didn't fully understand why it was important. Through my research, I learned that Retrieval-Augmented Generation is essentially a way to ground AI responses in actual source documents. Instead of just relying on what the model learned during training, RAG systems:

1. Retrieve relevant chunks of text from a knowledge base
2. Provide these chunks as context to the language model
3. Generate answers based on this specific context

The beauty of this approach became clear to me: by constraining the model to specific retrieved content, we can reduce hallucinations—those confident-sounding but completely fabricated answers that LLMs are infamous for.

### The Evaluation Challenge

I quickly discovered that evaluating AI outputs is much harder than I initially thought. Traditional metrics were designed for different purposes:
- **ROUGE and BLEU** were created for machine translation and summarization
- **BERTScore** measures semantic similarity
- But none of these were designed to answer the fundamental question: *Is this factually correct?*

This realization was eye-opening. We've been using tools designed for one purpose to solve a completely different problem. It's like using a thermometer to measure distance—you'll get a number, but it won't tell you what you need to know.

---

## 4. Exploring Evaluation Metrics

### Traditional Lexical Metrics

**ROUGE (Recall-Oriented Understudy for Gisting Evaluation)**

I started by learning about ROUGE, which measures the overlap of words and phrases between the generated text and a reference answer. ROUGE comes in several variants:
- ROUGE-1 counts single word matches
- ROUGE-2 counts two-word phrase matches
- ROUGE-L finds the longest common sequence

At first, this seemed reasonable. If an AI answer shares many words with the correct answer, it should be good, right? But as I dug deeper, I realized the flaw: a hallucinated answer that uses the right vocabulary can score high on ROUGE even if all the facts are wrong. If I asked about a portfolio's "95% confidence interval" and the AI responded with "99% confidence interval" using similar financial terminology, ROUGE would give it a decent score despite the critical factual error.

**BLEU (Bilingual Evaluation Understudy)**

BLEU was originally designed for machine translation, and I learned it's even more problematic than ROUGE. It's extremely sensitive to exact wording—if an answer is correct but phrased differently, BLEU can give it a score of zero! During my experiments, I actually saw this happen. One of my test answers was partially correct but paraphrased differently from the reference, and BLEU gave it a score of 0.000. This made me realize that BLEU is completely unsuitable for evaluating answers where paraphrasing is natural and expected.

### Semantic Similarity Metrics

**BERTScore**

BERTScore felt like a step forward. Instead of just counting words, it uses BERT embeddings to measure semantic similarity. This means it can recognize when two sentences mean the same thing even if they use different words. I was initially optimistic about this approach.

However, I soon encountered its limitation: semantic similarity doesn't equal factual correctness. Two statements can be semantically similar but factually different. For example:
- "The portfolio has a 95% VaR confidence interval" (correct)
- "The portfolio has a 99% VaR confidence interval" (wrong)

These are semantically very similar—they're both about VaR confidence intervals—but one is factually incorrect. BERTScore can't distinguish between them because it doesn't verify facts; it only measures meaning similarity.

### RAG-Specific Metrics (RAGAS Framework)

**RAGAS Faithfulness**

This was the metric that finally addressed the core problem I was investigating. RAGAS Faithfulness doesn't just measure similarity; it checks whether every claim in the generated answer is actually supported by the retrieved context. Here's how I understood it works:

1. Extract individual claims from the AI's answer
2. For each claim, check if it can be verified from the source documents
3. Calculate the percentage of claims that are supported

This was exactly what I needed! A faithfulness score of 1.0 means no hallucinations—every claim is grounded in the source material. A score of 0.0 means the answer is completely unsupported.

**Other RAGAS Metrics**

I also learned about other RAGAS metrics:
- **Answer Relevancy** measures if the answer actually addresses the question
- **Context Precision** evaluates if the retrieved chunks are relevant
- **Context Recall** checks if all necessary information was retrieved

These metrics helped me understand that RAG evaluation isn't just about the final answer—we also need to evaluate the retrieval step itself.

---

## 5. Case Study: Correct vs Partially Correct vs Hallucinated Responses

To truly understand these metrics, I needed to test them with real examples. I created a case study using a financial quarterly report document. I chose finance because it's a high-stakes domain where accuracy is critical—wrong numbers can lead to bad investment decisions.

### The Document and Question

I worked with a 4-page financial portfolio report containing information about asset allocations, risk metrics, and performance data. I crafted a question that required specific numerical accuracy: *"What is the VaR confidence interval and current portfolio allocation strategy?"*

### The Ground Truth

From the document, I extracted the correct answer:
- 95% confidence interval for VaR (Value at Risk)
- Weekly downside variance not exceeding 2.1%
- Domestic Large-Cap Equities over-allocated at 32.4% vs 30.0% target
- Emerging Markets under-allocated at 4.1% vs 5.0% target
- Portfolio Beta of 0.88

### Three Types of Answers

**Answer 1: RAG-Generated (Correct and Grounded)**

I generated this using my RAG pipeline, which retrieved relevant chunks and constrained the response to that context. The answer correctly stated the 95% confidence interval and 2.1% downside variance. It was factually accurate, though slightly verbose with some additional context about profit-taking strategies.

**Answer 2: Non-RAG Generated (Partially Correct)**

For this answer, I gave the model access to the full document instead of just retrieved chunks. Interestingly, this led to problems. While it correctly mentioned the 95% confidence interval and 2.1% variance, it also added details about "enterprise technology" and "healthcare" sectors that weren't in the source document. The model appeared to fill gaps in its understanding with plausible-sounding information.

**Answer 3: Hallucinated (Plausible but Completely Wrong)**

I crafted this answer to sound authoritative while being factually incorrect:
- Changed confidence interval from 95% to 99%
- Changed downside variance from 2.1% to 1.5%
- Invented portfolio allocations (Technology Equities at 45%)
- Changed Beta from 0.88 to 1.2

The key insight: this answer used all the right terminology and sounded confident, making it dangerous because a non-expert might trust it.

---

## 6. Manual and Automated Evaluation Findings

### What the Metrics Actually Said

When I ran all three answers through my evaluation pipeline, the results were shocking and enlightening:

| Metric | RAG (Correct) | Non-RAG (Partial) | What I Learned |
|--------|---------------|-------------------|----------------|
| ROUGE-1 | 0.407 | 0.230 | Both scored low; RAG was better but not decisively |
| ROUGE-2 | 0.231 | 0.041 | Slightly better distinction |
| BLEU | 0.219 | 0.000 | BLEU gave zero to a partially correct answer! |
| BERTScore | 0.877 | 0.844 | Both scored high—couldn't distinguish |
| RAGAS Faithfulness | 0.667 | N/A | Only metric checking factual grounding |

### The BLEU Disaster

I was stunned when BLEU gave the partially correct answer a score of 0.000. This answer actually contained correct information about the VaR parameters, but because it was phrased differently from my reference, BLEU essentially said it was worthless. This taught me an important lesson: metrics designed for one task (translation) can be misleading when applied to another (factual verification).

### The BERTScore Illusion

BERTScore gave both answers high scores (0.877 vs 0.844), creating a false sense of security. Both answers used similar financial vocabulary, so they were semantically similar. But semantic similarity masked the factual differences. This was a crucial insight: an answer can sound right without being right.

### My Manual Evaluation

When I evaluated the answers myself, I gave them very different scores:
- RAG answer: 9/10 (accurate, slightly verbose)
- Non-RAG answer: 6/10 (partially correct, added unsupported details)
- Hallucinated answer: 2/10 (sounds good, but factually wrong)

The automated metrics showed poor correlation with my human judgment, except for RAGAS Faithfulness, which aligned well with factual accuracy.

---

## 7. Context Window Experiments and Observations

One of the most fascinating parts of my internship was investigating how context length affects answer quality. I had assumed that giving the model more context would lead to better answers, but my experiments revealed a more nuanced reality.

### The Experiment Setup

I compared two approaches:
- **RAG approach**: Provided 3 retrieved chunks (~600 words of focused, relevant context)
- **Non-RAG approach**: Provided the full document (~764 words, truncated to fit model limits)

### Surprising Findings

**More Context ≠ Better Answers**

This was counterintuitive, but the RAG approach with less context actually performed better! The non-RAG approach with full document access had:
- Longer generation time (5.36s vs 3.50s)
- Lower faithfulness—it added unsupported details
- Higher hallucination risk

I realized that when given broad context, the model tried to "fill in gaps" and make connections that weren't explicitly in the text. It wanted to be helpful and comprehensive, which led it to add plausible-sounding but unsupported information.

**The Sweet Spot for Context**

Through experimentation with the Gemma 3:1B model, I discovered:
- Context limit: 8,192 tokens (~6,000 words)
- Optimal range: 400-800 words of highly relevant text
- Beyond 1,000 words: Model starts adding unsupported details

This taught me that RAG isn't just about providing context—it's about providing the *right* context in the *right* amount.

### Understanding Model Behavior

I came to understand that LLMs are trained to generate fluent, coherent text. When given broad context, they activate this training and "smooth over" any perceived gaps with plausible completions. RAG's constraint—limiting context to only retrieved, relevant chunks—acts as a safeguard against this behavior.

---

## 8. Mini Project Implementation

To consolidate my learning, I built a complete proof-of-concept RAG pipeline. This wasn't just a theoretical exercise; I created a production-quality system that I could actually use and demonstrate.

### System Architecture

My pipeline consisted of several integrated components:

**1. PDF Extraction Module**
I used PyMuPDF and pdfplumber to extract text, tables, and metadata from PDF documents. I learned to handle complex financial documents that mix text, tables, and headers/footers. One challenge I faced was avoiding duplicate text extraction when both libraries processed the same content. I solved this using coordinate-based filtering.

**2. Intelligent Chunking System**
I implemented a chunking strategy that:
- Split text into 200-word chunks with 30-word overlap
- Never split tables (kept them as complete units)
- Preserved section boundaries when possible

The overlap was crucial—I learned it ensures that important information spanning chunk boundaries isn't lost.

**3. Local Embedding Generation**
I used the sentence-transformers library with the all-MiniLM-L6-v2 model. This was my first time working with embeddings, and I was fascinated by how 384-dimensional vectors could capture semantic meaning. The fact that this ran locally (no API calls) was important for privacy and cost.

**4. Vector Store with ChromaDB**
ChromaDB was new to me, and I spent time understanding how vector databases work. I learned about:
- HNSW indexing for efficient similarity search
- Cosine similarity for finding relevant chunks
- Persistent storage for reusable vector stores

**5. LLM Integration**
I integrated with Ollama running the Gemma 3:1B model locally. This was my first experience running an LLM on my own machine. I learned to craft prompts that emphasized grounding: "Answer based only on the provided context. If unsure, say so."

**6. Evaluation Framework**
I implemented all the metrics I studied:
- ROUGE (1, 2, and L variants)
- BLEU
- BERTScore
- RAGAS metrics (Faithfulness, Answer Relevancy, Context Precision/Recall)

### Technical Challenges I Overcame

**Challenge 1: Table Extraction**
Financial documents have complex tables. I learned that PyMuPDF and pdfplumber extract tables differently, and I had to merge their outputs intelligently.

**Challenge 2: ChromaDB Initialization**
I initially had issues with ChromaDB persistence. I learned about collection management and proper cleanup procedures.

**Challenge 3: Prompt Engineering**
Getting consistent, grounded responses required careful prompt design. I iterated on my prompts multiple times, learning what worked and what didn't.

**Challenge 4: Evaluation Implementation**
Implementing RAGAS metrics from scratch was complex. I had to understand datasets format and how to structure evaluation questions with ground truth answers.

### What the System Demonstrated

My final pipeline successfully:
- Processed a 4-page financial PDF in ~5 seconds
- Created 6 chunks (5 text, 1 table)
- Retrieved top-3 relevant chunks for queries
- Generated answers in ~3.5 seconds
- Evaluated outputs across 7 different metrics
- Produced structured results in JSON format

The system proved my hypothesis: RAG with RAGAS Faithfulness evaluation outperformed non-RAG approaches in detecting hallucinations and ensuring factual accuracy.

---

## 9. Challenges Faced During the Internship

### Technical Challenges

**Understanding Vector Embeddings**
Initially, the concept of representing text as 384-dimensional vectors was abstract to me. I had to spend time visualizing how semantic similarity translates to geometric proximity in vector space. Experimenting with ChromaDB's similarity search helped make this concrete.

**Metric Implementation Complexity**
Getting RAGAS metrics to work properly was harder than I expected. The documentation wasn't always clear, and I had to read through source code to understand expected data formats.

**Windows Environment Issues**
Some Python libraries behaved differently on Windows than in the examples I found online. I had to learn about path handling, command shell differences, and platform-specific dependency issues.

### Conceptual Challenges

**The Metrics Don't Measure What They Claim**
This was philosophically troubling. We have metrics called "evaluation metrics," but they don't actually evaluate what matters most—factual correctness. I had to shift my mental model from "metrics tell us if answers are good" to "metrics measure specific properties that may or may not correlate with quality."

**Hallucinations Are Hard to Define**
I struggled with defining what counts as a hallucination. Is paraphrasing a hallucination? What about reasonable inferences? I learned that hallucination is a spectrum, not a binary property.

**The Context Window Paradox**
The discovery that more context can hurt performance was counterintuitive and forced me to rethink assumptions about how LLMs work.

### Process Challenges

**Balancing Depth and Breadth**
With limited time, I had to decide what to explore deeply versus what to understand at a surface level. I focused on metrics and RAG implementation, while treating topics like fine-tuning and advanced retrieval strategies as future work.

**Debugging Without Clear Error Messages**
When my RAG pipeline produced poor answers, there wasn't always a clear error message. I had to develop debugging strategies: checking retrieved chunks, examining prompts, testing different questions.

---

## 10. Key Learnings and Insights

### Technical Insights

**1. Traditional Metrics Are Fundamentally Limited**
ROUGE, BLEU, and even BERTScore cannot detect hallucinations because they measure surface properties (word overlap, semantic similarity) rather than factual grounding. This isn't a bug; it's inherent to what they measure.

**2. RAG Is Essential for High-Stakes Domains**
For applications where accuracy matters—finance, healthcare, legal—RAG provides crucial grounding. It's not perfect, but it significantly reduces hallucination risk.

**3. Evaluation Must Match Use Case**
There's no universal "best" metric. Summarization needs different evaluation than factual Q&A. Understanding what you're trying to measure is more important than knowing how to calculate metrics.

**4. Context Quality > Context Quantity**
More information doesn't automatically improve LLM outputs. Focused, relevant context outperforms broad, unfocused context.

**5. Local Models Are Viable**
I was surprised by how well local models like Gemma 3:1B performed. For many applications, you don't need massive cloud-based models.

### Methodological Insights

**6. Manual Evaluation Is Still Essential**
No automated metric can fully replace human judgment, especially for nuanced assessments of factual accuracy and appropriateness.

**7. Ground Truth Is Hard to Define**
Creating good reference answers for evaluation is challenging. Different domain experts might phrase the same facts differently.

**8. Failure Analysis Is More Valuable Than Success Metrics**
I learned more from studying when and why my system failed than from celebrating when it succeeded.

### Professional Insights

**9. Documentation Matters**
I spent significant time documenting my code and experiments. This helped me think more clearly and will help anyone (including future me) understand my work.

**10. Iteration Is Key**
My first attempts at chunking, prompting, and evaluation all needed refinement. The final system was the result of many iterations.

### Philosophical Insights

**11. We're Measuring the Wrong Things**
Much of the AI evaluation field is focused on metrics we can compute easily rather than properties we actually care about.

**12. Plausibility ≠ Truth**
LLMs are exceptionally good at generating plausible text, which makes them dangerous when accuracy matters. This is a fundamental challenge for the field.

**13. Trust Must Be Earned, Not Assumed**
We shouldn't trust AI outputs just because they sound confident. Verification mechanisms like RAG and faithfulness metrics are essential.

---

## 11. Future Scope

### Immediate Improvements (Next Steps)

**Enhanced Evaluation Framework**
I would like to implement more sophisticated faithfulness checking, perhaps using multiple LLMs to cross-verify claims or integrating fact-checking databases.

**Better Chunking Strategies**
Semantic chunking based on topic modeling could improve retrieval quality. Instead of fixed-size windows, chunks could be based on thematic coherence.

**Query Expansion**
Automatically expanding user queries to include synonyms and related terms could improve retrieval recall.

**User Interface**
Building a Streamlit or Gradio interface would make the system more accessible for non-technical users.

### Research Directions

**Domain-Specific Metrics**
Financial documents might need different evaluation criteria than medical or legal texts. Developing domain-specific faithfulness metrics is an interesting research direction.

**Adversarial Testing**
Systematically generating plausible but wrong answers to test metric robustness could help improve evaluation frameworks.

**Context Window Optimization**
Further research into optimal context length for different model sizes and domains could improve RAG system design.

**Hybrid Evaluation**
Combining automated metrics with targeted human review might provide the best balance of scalability and accuracy.

### Broader Applications

**Multi-Document Analysis**
Extending RAG to synthesize information across multiple documents while maintaining source attribution.

**Real-Time Fact-Checking**
Using faithfulness metrics to flag potentially incorrect statements in real-time during generation.

**Citation Generation**
Automatically citing specific source passages for each claim in generated answers.

---

## 12. Conclusion

This internship fundamentally changed how I think about AI evaluation. I started with a simple question—*Can we distinguish correct from plausible but wrong answers?*—and discovered a much more complex reality.

The answer to my question is nuanced: **traditional metrics cannot reliably detect hallucinations**, but **RAG architectures with grounding-based evaluation** (like RAGAS Faithfulness) offer a path forward. However, even these approaches have limitations and cannot replace human judgment in high-stakes scenarios.

### What I'm Taking Away

**Technical Skills:**
- Hands-on experience building RAG pipelines
- Understanding of vector databases and embeddings
- Practical knowledge of LLM integration and prompt engineering
- Experience with multiple evaluation frameworks

**Critical Thinking:**
- Skepticism about metrics that "measure" quality
- Understanding that tools designed for one purpose may fail at another
- Appreciation for the gap between technical capability and real-world deployment

**Professional Growth:**
- Ability to design and execute experimental studies
- Experience with iterative development and debugging
- Skills in technical documentation and communication

### Broader Implications

The limitations I discovered in current evaluation metrics have serious implications for AI deployment in critical domains. Organizations using LLMs for financial analysis, medical diagnosis, or legal research need to understand that:

1. High evaluation scores don't guarantee factual accuracy
2. RAG-style grounding is essential, not optional
3. Human oversight remains necessary
4. Metrics must be chosen to match the specific use case

### Final Reflection

This internship taught me that we're still in the early days of understanding how to build trustworthy AI systems. The technology is impressive, but our ability to evaluate and verify it lags behind. There's important work to be done in developing better evaluation frameworks, and I'm excited to have contributed a small piece to this larger puzzle.

I'm grateful for the opportunity to work on this project. It combined theoretical research with practical implementation, forced me to confront the limitations of current approaches, and gave me hands-on experience with cutting-edge AI technologies. Most importantly, it instilled in me a healthy skepticism about AI outputs and a commitment to building systems that earn trust through verification rather than demanding it through confident-sounding text.

The question of how we trust AI isn't fully answered, but I now have a much better understanding of the challenges involved and some practical tools for addressing them.

---

**Project Artifacts:**
- Complete RAG pipeline implementation (732 lines of Python)
- Evaluation framework with 7 metrics
- Streamlit dashboard for interactive exploration
- Comprehensive documentation and test results
- This internship report

**Skills Developed:**
- Python programming (advanced)
- RAG architecture design
- Vector database management
- LLM integration and prompt engineering
- Technical writing and documentation
- Experimental design and analysis

**Total Duration:** 8 weeks  
**Lines of Code Written:** ~2,500  
**Documents Processed:** 15+  
**Metrics Implemented:** 7  
**Key Finding:** Traditional metrics fail to detect AI hallucinations; RAG with faithfulness evaluation is essential for high-stakes applications.

---

*"The first principle is that you must not fool yourself—and you are the easiest person to fool."* — Richard Feynman

This quote resonated with me throughout this internship. LLMs are masters at generating text that sounds convincing, and it's remarkably easy to be fooled by confident-sounding but incorrect outputs. Building systems that resist this fooling—through grounding, verification, and appropriate evaluation—is one of the most important challenges in AI today.
