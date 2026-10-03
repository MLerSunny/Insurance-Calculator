# 10. Setup, Configuration and Testing

## 10.1 Prerequisites

| Tool | Version | Needed for |
|------|---------|-----------|
| Python | 3.10 or 3.11 (Dockerfile uses 3.10) | Backend |
| Node.js + npm | 18.x or 20.x | Angular 17 frontend |
| Angular CLI | 17.x (`npx ng` works) | `ng serve` |
| Ollama | recent | K3/K1 LLM calls (optional: everything falls back without it) |
| Disk / RAM | ~20 GB disk and RAM for `deepseek-r1:32b`; use a smaller model (e.g. `deepseek-r1:7b`) on a laptop | LLM |

## 10.2 Run locally (macOS / Linux)

```bash
# Backend
cd GenAI/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt langchain-chroma langchain-huggingface   # B-4: missing deps
mkdir -p logs                                                            # B-3: import fails without it
export OLLAMA_HOST=http://localhost:11434 OLLAMA_MODEL=deepseek-r1:7b    # B-2: .env is read too late
python seed_vector_db.py            # once; re-running inserts duplicates
uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs

# LLM (separate terminal, optional)
ollama serve
ollama pull deepseek-r1:7b

# Frontend (separate terminal)
cd GenAI/frontend/insurance-calculator
npm install
npx ng serve
# → http://localhost:4200
```

On Windows, `GenAI/run_backend.ps1` does the backend steps, using the
committed `GenAI/.venv` (which only works on the original machine).

**Run Uvicorn from `GenAI/backend`.** SQLite (`./app_database.db`) and
Chroma (`./vector_db`) paths are relative to the working directory.

## 10.3 Run with Docker Compose

```bash
cd GenAI
cp backend/.env.example backend/.env
docker compose up --build
docker exec -it insurance-calculator-ollama ollama pull deepseek-r1:7b
```

Caveats (see [01 §1.6](01-system-overview.md#16-deployment-views)): the
backend still uses SQLite inside the bind-mounted `./backend` folder; Postgres
and pgAdmin are unused. Set `FRONTEND_URL` (not `CORS_ALLOW_ORIGINS`) if the UI
origin changes. Raise the Ollama memory limit for larger models.

## 10.4 Configuration reference

| Variable | Default | Read by | Effective? |
|----------|---------|---------|-----------|
| `FRONTEND_URL` | `http://localhost:4200` | `main.py` CORS | ✅ |
| `API_HOST` / `API_PORT` / `DEBUG` | `0.0.0.0` / `8000` / `false` | `main.py` `__main__` only | ✅ when run as `python main.py` |
| `OLLAMA_HOST` | `http://localhost:11434` | `llm_service.py` at import | ⚠️ only from the real environment, not `.env` |
| `OLLAMA_MODEL` | `deepseek-r1:32b` | `llm_service.py` at import, `/api/system-status` | ⚠️ same as above |
| `VECTOR_COLLECTION_NAME` | `insurance_data` | `seed_vector_db.py`, `/api/system-status` (display) | ⚠️ the runtime `VectorStore()` always uses `insurance_data` |
| `VECTOR_DB_PATH` | `./vector_db` | `seed_vector_db.py` | ⚠️ runtime always uses `./vector_db` |
| `DATABASE_URL` | `.env.example`: `sqlite:///./insurance.db` | nobody | ❌ hard-coded `sqlite:///./app_database.db` |
| `RATE_LIMIT_PER_MINUTE`, `BURST_LIMIT` | 60 / 10 | commented-out code | ❌ |
| `VECTOR_PERSIST_DIR`, `LOG_LEVEL`, `LOG_FORMAT` | | nobody | ❌ |
| `CORS_ALLOW_ORIGINS` | (Compose) | nobody | ❌ |

Frontend: the API base URL `http://localhost:8000/api` is hard-coded in
`insurance.service.ts` and `quote.service.ts`; there are no Angular
environment files.

## 10.5 Operational checks

```bash
curl localhost:8000/health              # DB ping
curl localhost:8000/api/system-status   # static; does not probe Ollama/Chroma
curl localhost:11434/api/tags           # is Ollama up and is the model pulled?
python GenAI/backend/check_db.py        # SQLAlchemy connectivity + table listing
python GenAI/backend/test_ollama.py     # ad-hoc LLM round trip
```

Quick functional smoke test of every AI path:

```bash
B=localhost:8000
APP='{"applicant_name":"Jane Doe","applicant_age":42,"email":"jane@example.com","phone":"6145550100",
      "medical_history":{"conditions":["hypertension"]},"risk_factors":{"smoking":false},"coverage_amount":500000}'
curl -s -XPOST $B/api/insurance/applications/      -H 'Content-Type: application/json' -d "$APP"   # H1
curl -s -XPOST $B/api/insurance/calculate-premium/ -H 'Content-Type: application/json' -d "$APP"   # H2+H1
curl -s -XPOST $B/api/complex/apply-underwriting-rules/ -H 'Content-Type: application/json' \
     -d '{"applicant_age":68,"coverage_amount":750000,"risk_score":0.4}'                          # K3 rules
curl -s -XPOST $B/api/evaluate-application -H 'Content-Type: application/json' \
     -d '{"applicant_age":68,"coverage_amount":750000,"risk_score":0.4}'                          # K3 + LLM
curl -s -XPOST $B/api/complex/complex-application/ -H 'Content-Type: application/json' -d "$APP"  # K1
```

Expected outputs today are listed in [06 §6.4](06-use-cases-and-scenarios.md#64-user-scenarios-worked-examples).

To reset browser data, open DevTools → Application → Local Storage and
delete `insurance_accounts` and `insurance_quotes`.

## 10.6 Tests

```bash
cd GenAI/backend && pytest -v          # or .\run_tests.ps1
cd GenAI/frontend/insurance-calculator && npx ng test
```

| Suite | File | What it covers | Known problems |
|-------|------|----------------|----------------|
| API | `tests/test_api_endpoints.py` | `/`, `/health`, `/api/system-status`, calculate premium, submit + get application, list | T-1 (wrong patch target and keys), T-3 |
| DB | `tests/test_database.py` | Connection, ORM insert | Uses `test_insurance.db` |
| LLM | `tests/test_llm_service.py` | Init, generate, structured generation, retry | T-2 (`ScopeMismatch`) |
| Vector | `tests/test_vector_store.py` | Init, add/query, metadata, errors | Needs the embedding model download |
| Frontend | `*.spec.ts` | CLI defaults | T-6 |

See [09 §6](09-gap-analysis.md#6-testing-gaps) for details. Tests to add
first: rule-engine table tests (pure, fast), H1/H2 unit tests, a K1 test with
a stub LLM asserting all three agents run, and a K3 test with a fake LLM
returning `<think>` + JSON.

## 10.7 Viewing these diagrams

All diagrams are Mermaid code blocks. GitHub renders them inline. Locally, use
VS Code with the "Markdown Preview Mermaid Support" extension, or
`npx @mermaid-js/mermaid-cli -i docs/07-system-flows.md -o out.md` to export
SVGs.
