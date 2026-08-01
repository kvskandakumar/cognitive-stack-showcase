# AI Middleware Client

## Features

- Prompt submission with target language selection
- Zod schema-based form validation
- Submit button disabled until the form is valid
- Redux Toolkit global request and response state
- Success, clarification and structured error handling
- Request cancellation support
- Responsive and accessible UI

## Architecture

The project uses a feature-based architecture. Prompt-related components,
state, schemas and API functions are grouped under `features/prompt`.

Form state remains local because it is only required by the form. Submitted
request data and backend responses are stored globally because they may be
required by other pages or future features.

## Run locally

npm install
npm run dev

## Environment variables

VITE_API_BASE_URL=http://localhost:8080