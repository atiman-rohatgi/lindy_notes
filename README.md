# Lindy Notes

A small notes API built with FastAPI and PostgreSQL. Users register and log in with email and password, receive a JWT, and use it to create, list, delete and summarize their own notes.

## Setup

**Prerequisites:** Python 3, PostgreSQL

1. Clone the repo and create a virtual environment:

   ```bash
   git clone <repo-url>
   cd lindy_notes
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create the database and load the schema:

   ```bash
   createdb notes
   psql -d notes -f schema.sql
   ```

3. Copy the env template and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Generate a `SECRET_KEY` with:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. Run the server:

   ```bash
   python main.py
   ```

   The API runs at `http://localhost:8000`, and interactive docs are at `http://localhost:8000/docs`.

## API

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Create a user with email and password |
| POST | `/auth/login` | No | Returns a bearer access token |
| GET | `/notes` | Yes | List the current user's notes |
| POST | `/notes` | Yes | Create a note (`title`, `content`) |
| DELETE | `/notes/{note_id}` | Yes | Delete one of the current user's notes |
| POST | `/notes/{note_id}/summarize` | Yes | Summarize a note (currently returns a placeholder) |

Authenticated endpoints expect the header `Authorization: Bearer <token>`.

## Project structure

| File | Description |
|------|-------------|
| `main.py` | App entrypoint. Creates the FastAPI app, configures CORS for `localhost:3000`, mounts the routers and starts uvicorn. |
| `security.py` | Auth routes: register (hashes passwords with bcrypt) and login (verifies the password and issues a JWT). |
| `auth.py` | JWT helpers: creates and decodes tokens, and provides the `get_current_user` dependency for protected routes. |
| `notes.py` | Notes routes: list, create, delete and summarize, each scoped to the logged-in user. |
| `database.py` | Reads database settings from the environment and returns PostgreSQL connections. |
| `schema.sql` | Creates the `users` and `notes` tables (UUID primary keys, notes linked to users). |
| `requirements.txt` | Pinned Python dependencies. |
| `.env.example` | Template for the environment variables the app needs. |
