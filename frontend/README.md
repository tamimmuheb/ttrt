# Research GNN Agent Frontend

A modern React + Vite + Tailwind app to interact with the serverless Research GNN Agent.

## Commands

- Install deps:
  ```bash
  npm install
  ```
- Dev:
  ```bash
  npm run dev
  # http://localhost:5173
  ```
- Build:
  ```bash
  npm run build
  npm run preview
  ```

## Configure API Endpoint
Click the Settings button (bottom-right) and set the API Base URL to your deployed API Gateway base, for example:

- `https://<api-id>.execute-api.us-east-1.amazonaws.com`

The app will POST to `<base>/pipeline`.

## Features
- Upload PDF or enter text
- Run pipeline and see hypothesis, ranked papers, and graph
- Copy/Download LaTeX + BibTeX artifacts