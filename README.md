# AI Middleware Client

## Features

- Prompt submission with target language selection
- Zod schema-based form validation
- Submit button disabled until the form is valid
- RTK Query request state, caching, cancellation, and error handling
- Backend-driven pagination with client-side debounced search and sorting
- Success, clarification and structured error handling
- Request cancellation support
- Responsive and accessible UI

## Architecture

The project uses a feature-based architecture. Prompt-related components,
state, schemas and API functions are grouped under `features/prompt`.

Form state remains local because it is only required by the form. API state is
owned by RTK Query. Pagination is backend-driven so large result sets are not
transferred up front; search and sorting apply to the currently returned page.

## Run locally

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
npm run dev:backend

# Frontend (in another terminal)
npm install
npm run dev
```

The backend persists prompt requests and AI-generated insights in SQLite at
`backend/data/prompts.db`. Interactive API documentation is available at
`http://localhost:8000/docs`.

### API

`POST /api/prompts`

```json
{
  "prompt": "Create a product launch strategy",
  "targetLanguage": "en",
  "contextId": "c4522f04-2d2a-47c9-b253-7e934bdd22a1"
}
```

`contextId` is optional. The API creates one when it is omitted and returns it
for use in subsequent conversation requests. Supported languages are `de`,
`en`, `es`, and `fr`. Missing or malformed inputs return structured 422 errors.
Prompts shorter than five characters or lacking sufficient context return
`NEEDS_CLARIFICATION` before any model request. Sufficiently specific prompts
use Gemini's API and store the structured insights in SQLite.

## Environment variables

Local development uses Vite's `/api` proxy and does not require a frontend
environment variable. For a deployed frontend, set `VITE_API_BASE_URL` to the
public URL of this BFF—not to an LLM provider URL. Never place API keys in a
`VITE_*` variable because Vite exposes those values to browser code.

Configure the Gemini integration only on the backend:

```bash
USE_REAL_GEMINIAI=false
GEMINI_API_KEY=your-server-side-key
# Optional; defaults to the cost-efficient gemini-3.6-flash model
GEMINI_MODEL=gemini-3.6-flash
```

Set `USE_REAL_GEMINIAI=false` for polished, production-shaped mock insights with
no Gemini request. Set it to `true` to generate real results using the
server-side key. Restart the backend after changing the flag.

The backend accepts requests from Vite's usual local ports by default. Override
this when needed with a comma-separated list, for example:

```bash
CORS_ORIGINS=https://app.example.com uvicorn backend.app.main:app
```
