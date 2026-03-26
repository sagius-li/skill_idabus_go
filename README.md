# Idabus Chat App

This repository now contains:

- `idabus-go/`: the existing Idabus skill and request scripts
- `backend/`: a Python chat service that calls OpenAI and exposes `idabus-go` as a tool
- `web/`: a simple browser chat interface

## Local Setup

1. Copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`.
2. Copy `idabus-go/.env.example` to `idabus-go/.env` and fill in the Idabus OAuth/API settings.
3. Install backend dependencies:

```bash
cd backend
python3 -m pip install -r requirements.txt
```

4. Start the service:

```bash
cd backend
python3 -m uvicorn app:app --reload
```

5. Open `http://127.0.0.1:8000`.

## Notes

- The model decides when to use the Idabus tool.
- The backend supports multi-turn tool use per user request.
- Session state is stored in memory in v1.
- For Azure App Service later, deploy `backend/`, `web/`, and `idabus-go/` together in one app package.
