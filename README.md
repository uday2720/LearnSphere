# 🧠 LearnSphere
## Privacy-First Adaptive AI Learning Companion for Snapdragon PCs

> LearnSphere doesn't just answer questions. It builds a learner model, identifies knowledge gaps, and recommends what to learn next — with a local-first architecture designed for Snapdragon-powered PCs.

### Working MVP
- Local PDF ingestion and text extraction
- Concept extraction with TF-IDF/NLP
- SQLite persistence
- Knowledge Map
- Diagnostic assessment generation
- Evidence-based concept mastery updates
- Next-best-topic recommendation
- Local TF-IDF retrieval / RAG foundation
- Source-grounded local tutor response
- Device/runtime information panel
- No cloud/API dependency for the MVP

### Snapdragon path
The architecture is prepared for a local ONNX/QNN model deployment. Qualcomm AI Hub/QNN integration and NPU benchmarking must be performed on supported Snapdragon hardware; this repository does **not** fabricate NPU results.

### Install
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

### Demo
1. Add a text-based study PDF.
2. Review the Knowledge Map.
3. Generate the Diagnostic.
4. Answer questions; mastery updates.
5. Open Tutor and ask a question grounded in the PDF.
6. Open System to view local runtime information.

### Architecture
```text
PDF → Local extraction → Concepts → Knowledge Map
                         ↓
                   Diagnostic
                         ↓
               Student Knowledge Model
                         ↓
                Adaptive Recommendation
                         ↓
                  Local Retrieval/Tutor
                         ↓
              Future ONNX/QNN → NPU
```

### Roadmap
- Local SLM for grounded explanations
- Better question generation
- Bayesian/IRT-inspired mastery model
- Forgetting-aware revision
- Voice/OCR
- Qualcomm AI Hub compilation
- ONNX Runtime/QNN execution
- Measured Snapdragon NPU benchmarks

## License
MIT
