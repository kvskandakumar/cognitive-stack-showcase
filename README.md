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
uvicorn backend.app.main:app --reload

# Frontend (in another terminal)
npm install
npm run dev
```

The backend persists prompt requests and dummy insights in SQLite at
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
for use in subsequent conversation requests. Vague prompts return
`NEEDS_CLARIFICATION`; sufficiently specific prompts return `SUCCESS` and store
dummy insights locally without calling an LLM.

## Environment variables

VITE_API_BASE_URL=http://localhost:8000
