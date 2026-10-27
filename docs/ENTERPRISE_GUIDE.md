# Enterprise Deployment Guide

## 1. On-Premise and Air-Gapped Setup

OmniResearch can run completely disconnected from cloud AI providers by pairing with an on-premise Ollama or vLLM server.

### Local Ollama Setup

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull your chosen enterprise model:
   ```bash
   ollama pull llama3.3:70b
   # Or for lightweight setups:
   ollama pull qwen2.5:7b
   ```

3. Configure OmniResearch `.env`:
   ```env
   LLM_PROVIDER=ollama
   LLM_MODEL=llama3.3:70b
   OLLAMA_BASE_URL=http://localhost:11434
   SEARCH_PROVIDER=duckduckgo
   ```

## 2. Ingesting Enterprise Data Repositories

When conducting due diligence or market reviews with confidential internal files, pass file paths directly via the CLI:

```bash
python -m omniresearch.cli run "Merger and Acquisition Risk Analysis" \
  --docs /srv/data/audit_2025.pdf \
  --docs /srv/data/balance_sheet.csv \
  --export md,pdf,docx \
  --out /srv/reports
```

All uploaded documents are processed entirely in local memory using PyMuPDF and python-docx. No local files are transmitted to external vector databases.
