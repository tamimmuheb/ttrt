# Research GNN Agent (Serverless)

This project provides a fully serverless AI agent that:

- Ingests research-related text or PDFs
- Searches for relevant papers (using Semantic Scholar Graph API; built from S2 data)
- Builds a graph and subgraphs capturing correlations (similarity, citations, authors) and ranks papers
- Summarizes each paper
- Generates a hypothesis from the graph with an LLM
- Outputs LaTeX for the hypothesis and BibTeX citations; includes an optional LLM-powered LaTeX polishing step

Built as a single containerized AWS Lambda function exposed via HTTP API Gateway.


## High-level Architecture

- AWS API Gateway (HTTP) → AWS Lambda (container image)
- Lambda pipeline steps:
  1. Input handling: text input or base64 PDF → text
  2. Paper search: Semantic Scholar Graph API for top-K relevant papers and metadata
  3. Graph construction: NetworkX for similarity + citation graph; Louvain communities; PageRank
  4. Optional GNN: hook for GraphSAGE embeddings ranking (no training by default)
  5. Summarization: LLM (OpenAI/OpenRouter via LiteLLM) or extractive fallback
  6. Hypothesis generation: LLM based on graph evidence
  7. LaTeX + BibTeX generation; optional LLM polish pass for LaTeX stylization
- No persistent servers; all compute is in Lambda


## Endpoints

- POST `/pipeline`
  - Request JSON:
    ```json
    {
      "query": "graph neural networks for citation recommendation",
      "text": "optional free text from user",
      "pdf_base64": "optional base64-encoded PDF",
      "top_k": 20,
      "llm_provider": "openai",
      "polish_latex": true
    }
    ```
  - Response JSON:
    ```json
    {
      "query": "...",
      "paper_count": 20,
      "graph": { "nodes": [...], "edges": [...], "communities": [...] },
      "papers": [{
        "paperId": "...",
        "title": "...",
        "authors": ["..."],
        "year": 2024,
        "venue": "...",
        "url": "...",
        "rank": 0.023,
        "summary": "...",
        "bibtex_key": "..."
      }],
      "hypothesis": "...",
      "latex": "\\documentclass{article}...",
      "bibtex": "@article{...}...",
      "artifacts": {
        "latex_filename": "hypothesis.tex",
        "bib_filename": "references.bib"
      }
    }
    ```


## Setup

### Prerequisites
- Docker
- Node.js + Serverless Framework (optional but recommended)
- AWS account with permissions for ECR, Lambda, API Gateway

### Environment Variables
- `SEMANTIC_SCHOLAR_API_KEY` (optional, improves rate limits)
- LLM options via LiteLLM:
  - `OPENAI_API_KEY` or `OPENROUTER_API_KEY` etc.
  - `LLM_MODEL` (default: `gpt-4o-mini`)

### Build & Deploy (Serverless Framework)

1. Install Serverless Framework if not installed:
   ```bash
   npm i -g serverless
   ```
2. Deploy:
   ```bash
   sls deploy
   ```

This builds the container, pushes to ECR, and provisions the API endpoint.


## Local Testing

You can run the handler locally with the AWS Lambda Runtime Interface Emulator or simply `docker run` the container and invoke with a payload file.

Example payload `event.json`:
```json
{
  "query": "causal representation learning in multi-modal RL",
  "text": "We explore disentangled factors...",
  "top_k": 10,
  "polish_latex": false
}
```

Invoke locally via Docker (example):
```bash
# Build
docker build -t research-gnn-agent .

# Run the Lambda runtime interface emulator (RIE) automatically by image
docker run -p 9000:8080 \
  -e SEMANTIC_SCHOLAR_API_KEY=$SEMANTIC_SCHOLAR_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  research-gnn-agent

# Invoke
curl -s -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d @event.json | jq
```


## Implementation Notes

- PDF extraction uses PyMuPDF (`fitz`)
- Search uses Semantic Scholar Graph API (`/graph/v1/paper/search`) and detail fetch for citations
- Graph analysis uses NetworkX, PageRank, and Louvain (python-louvain)
- Optional GNN hooks are provided via PyTorch and can be enabled with weights
- LLM abstraction via LiteLLM supports multiple providers; falls back to extractive summaries if no key
- Outputs include both LaTeX document and `.bib` with BibTeX entries generated from metadata


## Cost and Limits
- API calls to Semantic Scholar may be rate-limited; API key recommended
- LLM usage depends on provider and model
- Lambda container image keeps all dependencies bundled; allocate sufficient memory and timeout


## Security
- No data is persisted by default; redact secrets from logs
- You may integrate S3 for artifact storage if desired


## License
MIT

## Notes on S2ORC vs Semantic Scholar API
- This project queries the Semantic Scholar Graph API, which is built on the S2 corpus. Direct S2ORC bulk data is not queried from Lambda to keep architecture serverless and responsive. If you need direct S2ORC access, integrate an offline pre-processing job to index in an external vector DB, then query that index from the Lambda.

## Serverless
- All compute runs inside Lambda using a container image; no EC2 or managed servers.
- Optional artifacts (PDF outputs, compiled PDFs) can be stored in S3 via an additional integration, but are not required.

## Frontend (Modern React + Vite)

A modern single-page app is included in `frontend/` to upload PDFs or enter text, run the pipeline, browse papers, explore the graph, and view/copy/download LaTeX + BibTeX.

- Dev:
  ```bash
  cd frontend
  npm install
  npm run dev
  # Open http://localhost:5173
  ```
- Configure API endpoint in the app using the Settings button (bottom-right). Set it to your deployed API base URL, e.g. `https://<api-id>.execute-api.us-east-1.amazonaws.com`.
- Build:
  ```bash
  npm run build
  npm run preview
  ```

In Cursor, you can open `frontend/index.html` with the dev server, or run the dev task to get a live preview.
