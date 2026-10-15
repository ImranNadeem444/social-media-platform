# Social Media Manager

A FastAPI + React platform for managing Facebook Pages and Instagram professional accounts from one dashboard: connect accounts through Meta OAuth, then publish images to one or many of them.

> **Developed for Pexdel Solution.** Social Media Manager is a feature module of the ViewRec platform.

> **Status:** Work in progress. Account connection through the admin's own login is implemented. Connecting a receiver's account through a shared invitation link is **not yet complete**. See [Current Status and Limitations](#current-status-and-limitations).

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Facebook and Instagram Integration](#facebook-and-instagram-integration)
- [Authentication and Security](#authentication-and-security)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database and Migrations](#database-and-migrations)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [API Overview](#api-overview)
- [Rate Limits](#rate-limits)
- [Testing](#testing)
- [Deployment](#deployment)
- [Current Status and Limitations](#current-status-and-limitations)
- [Roadmap](#roadmap)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Overview

Social Media Manager lets a logged-in user:

1. Create an account and log in.
2. Connect Facebook Pages and Instagram professional accounts through Meta's OAuth flows.
3. Upload an image and publish it to all connected accounts for a chosen platform.
4. See the result for each target, and disconnect accounts.

The backend stores provider tokens encrypted at rest and never returns them to the browser.

---

## Features

### Implemented in the code

| Area | Feature |
|---|---|
| Auth | User registration, login with a JWT bearer token, and `/auth/me` |
| Accounts | List connected accounts; disconnect an account you own |
| Facebook | Connect via Facebook Login for Business (`config_id`); pick one or more Pages from the list returned by Meta |
| Instagram | Connect a professional account via Instagram Login (`instagram_business_basic`, `instagram_business_content_publish`) |
| Publishing | Multipart image upload with optional caption; publish to Instagram, Facebook, or both |
| Publishing | Per-target status and error message; a failure on one target does not stop the others |
| Uploads | Extension allowlist (`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`), magic-byte validation, 10 MB limit |
| Security | Encrypted tokens (Fernet), single-use OAuth state, rate limiting, security headers, audit logging |
| Frontend | Login, registration, dashboard, accounts, create-post, Facebook page selector, OAuth success and error pages |

### Partially implemented

- **Delegated authorization (receiver connects their own account via a link).** The backend can generate an authorization URL for the admin and save the account under the admin's user. The Instagram callback works without a logged-in receiver. The Facebook page-selection step **requires the admin's login**, so a receiver cannot complete it. See [Current Status and Limitations](#current-status-and-limitations).

---

## Technology Stack

**Backend**
- Python 3.12 (Docker image), FastAPI, Uvicorn
- SQLAlchemy 2.x with `psycopg` (PostgreSQL)
- Alembic for migrations
- Pydantic 2 and `pydantic-settings`
- PyJWT (HS256), `pwdlib` for password hashing, `cryptography` (Fernet) for token encryption
- `httpx` for Meta Graph API calls
- `slowapi` for rate limiting

**Frontend**
- React 18, TypeScript, Vite 5
- React Router 6, Axios
- Tailwind CSS 3, `react-icons`
- ESLint

**Database:** PostgreSQL

---

## Architecture

```
┌──────────────┐    JWT (Bearer)     ┌─────────────────────────┐
│  React SPA   │ ──────────────────▶ │  FastAPI backend        │
│  (Vite)      │ ◀────────────────── │  /api/v1/...            │
└──────┬───────┘   JSON / redirects  └──────┬─────────┬────────┘
       │                                    │         │
       │ OAuth redirects                    │         │ Graph API calls
       ▼                                    ▼         ▼
┌──────────────────────┐          ┌──────────────┐  ┌────────────────────────┐
│ Meta OAuth dialogs   │          │ PostgreSQL   │  │ Facebook Graph API     │
│ (Facebook, Instagram)│          │ users, states│  │ Instagram Graph API    │
└──────────────────────┘          │ accounts,    │  └────────────────────────┘
                                  │ posts, logs  │
                                  └──────────────┘
                                          ▲
                        Uploaded images   │  served from /public/uploads
                        (publicly fetched by Meta)
```

### Connection flow (summary)

1. The user clicks **Connect** and the backend returns a Meta authorization URL with a random `state` stored in the database.
2. The user approves on Meta. Meta redirects to the backend callback with `code` and `state`.
3. The backend validates and consumes the `state`, exchanges the code for tokens, fetches account details, encrypts the token, and stores a `SocialAccount` row.
4. Facebook only: the backend redirects to a page selector in the frontend. The user picks Pages, and the backend stores each Page's token.

### Publishing flow (summary)

1. `POST /api/v1/posts` receives the image and caption, validates the file, and saves it to `backend/public/uploads/`.
2. The backend publishes to each eligible connected account for the target platform. Instagram publishing creates a media container, waits for it to finish processing, and then publishes it.
3. A `Post` row and one `PostTarget` row per account record the outcome.

---

## Facebook and Instagram Integration

### Facebook (Login for Business)

- Authorization URL: `https://www.facebook.com/v{GRAPH_API_VERSION}/dialog/oauth`, using `client_id`, `config_id`, `redirect_uri`, `response_type=code`, and `state`. Permissions come from the Facebook Login for Business configuration, not from a `scope` parameter.
- Code exchange and Page discovery use `graph.facebook.com` (`/oauth/access_token` and `/me/accounts`).
- The stored token for each Page is that Page's access token. Publishing uses the Page token.
- Requires a **Business-type** Meta app with a Login for Business configuration.

### Instagram (Instagram API with Instagram Login)

- Authorization URL: `https://www.instagram.com/oauth/authorize` with scopes `instagram_business_basic` and `instagram_business_content_publish`.
- Code exchange: `api.instagram.com/oauth/access_token`. Long-lived token: `graph.instagram.com/access_token` (`ig_exchange_token`). Account identity: `graph.instagram.com/{user_id}`.
- Publishing: `graph.instagram.com` media container, status polling, then `media_publish`.
- Only **professional** Instagram accounts are supported.

### Meta configuration checklist

Meta's requirements are set in the Meta App Dashboard, not in this repository. Confirm the current rules in Meta's documentation before you go live.

- A Meta app with the **Facebook Login for Business** product and a configuration ID (`FACEBOOK_CONFIG_ID`).
- An **Instagram** product with the Instagram Login setup, and the redirect URI registered (`INSTAGRAM_REDIRECT_URI`).
- Redirect URIs registered for Facebook (`FACEBOOK_REDIRECT_URI`) and Instagram.
- For users who do not hold a role on the app (Admin, Developer, or Tester), the app needs **Advanced Access** for the permissions used. This requires App Review and, in Meta's current rules, Business Verification.

---

## Authentication and Security

| Concern | Implementation |
|---|---|
| Passwords | Hashed with `pwdlib` using its recommended hasher (`PasswordHash.recommended()`) |
| Sessions | JWT (HS256) in the `Authorization: Bearer` header; expires after `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default 60) |
| Provider tokens | Encrypted with Fernet (`ENCRYPTION_KEY`) before storage; never returned by the API |
| OAuth CSRF | 64-character random `state` from `secrets.token_hex(32)`; single use; expires after 10 minutes |
| Ownership | Account lookups and deletes are filtered by the current user's ID; other users' accounts return 404 |
| Rate limiting | `slowapi` on login, registration, OAuth start and callback, Facebook page listing, and posting |
| Uploads | Extension allowlist, magic-byte check, 10 MB limit |
| Headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-XSS-Protection` |
| CORS | Allows the configured frontend origins only (see `backend/app/main.py`) |
| Audit | Login, registration, OAuth start and outcome, account disconnect, and post success or failure are written to an `audit_logs` table |

**Security notes for operators**
- Use strong, unique values for `JWT_SECRET_KEY` and `ENCRYPTION_KEY`. Rotating `ENCRYPTION_KEY` makes existing stored tokens unreadable.
- Never commit `.env` files. `.gitignore` excludes them, and only `.env.example` is tracked.

---

## Project Structure

```
social-media-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # Routers: auth, social_accounts, facebook, instagram, posts
│   │   ├── core/             # config, security, rate limiting, security/audit logger
│   │   ├── db/               # SQLAlchemy engine and session
│   │   ├── models/           # User, SocialAccount, OAuthState, FacebookOAuthSession, Post, PostTarget, AuditLog
│   │   ├── schemas/          # Pydantic request and response models
│   │   ├── services/         # Meta OAuth, publishing, encryption, file storage
│   │   └── main.py           # FastAPI app, CORS, middleware, routers
│   ├── alembic/              # Database migrations
│   ├── public/uploads/       # Uploaded images (not tracked)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Layout, dashboard, social-account and UI components
│   │   ├── context/          # Auth context
│   │   ├── pages/            # Dashboard, Accounts, CreatePost, OAuth pages, login, register
│   │   ├── router/           # Protected route wrapper
│   │   └── services/         # Axios client and API services
│   ├── package.json
│   └── vite.config.ts
├── .github/workflows/
│   └── deploy-frontend.yml   # Builds and deploys the frontend (GitHub Pages)
└── *.md                      # Design notes for the OAuth and delegated-authorization work
```

---

## Getting Started

### Prerequisites

- Python 3.12 (matches the Dockerfile)
- Node.js 18 or newer (matches the CI workflow)
- PostgreSQL 14 or newer (recommended; not verified in this repository)
- Meta developer apps for Facebook and Instagram, configured as described above

### Clone

```bash
git clone https://github.com/<your-org>/social-media-platform.git
cd social-media-platform
```

---

## Environment Variables

### Backend (`backend/.env`)

The backend loads `.env` from the directory it runs in (`backend/`). Copy the example and fill in your own values:

```bash
cd backend
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_HOST` | Yes | PostgreSQL host |
| `DATABASE_PORT` | Yes | PostgreSQL port, for example `5432` |
| `DATABASE_NAME` | Yes | Database name |
| `DATABASE_USER` | Yes | Database user |
| `DATABASE_PASSWORD` | Yes | Database password |
| `JWT_SECRET_KEY` | Yes | Long random string used to sign JWTs |
| `JWT_ALGORITHM` | No | Defaults to `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Defaults to `60` |
| `INSTAGRAM_APP_ID` | Yes | Instagram app ID |
| `INSTAGRAM_APP_SECRET` | Yes | Instagram app secret |
| `INSTAGRAM_REDIRECT_URI` | Yes | Backend callback URL, for example `https://api.example.com/api/v1/social-accounts/instagram/callback` |
| `FACEBOOK_APP_ID` | Yes | Facebook app ID |
| `FACEBOOK_APP_SECRET` | Yes | Facebook app secret |
| `FACEBOOK_REDIRECT_URI` | Yes | Backend callback URL, for example `https://api.example.com/api/v1/social-accounts/facebook/callback` |
| `FACEBOOK_CONFIG_ID` | Yes | Facebook Login for Business configuration ID |
| `GRAPH_API_VERSION` | No | Defaults to `v26.0` in code |
| `ENCRYPTION_KEY` | Yes | Fernet key: 44 characters, base64-encoded 32 bytes |
| `PUBLIC_BASE_URL` | Yes | Public HTTPS base URL of this backend. Meta fetches uploaded images from `{PUBLIC_BASE_URL}/public/uploads/...` |
| `FRONTEND_BASE_URL` | Yes | Frontend origin, used for OAuth redirects, for example `http://localhost:5173` |
| `RATE_LIMIT_LOGIN` | No | Defaults to `5/15min` |
| `RATE_LIMIT_REGISTER` | No | Defaults to `3/hour` |
| `RATE_LIMIT_OAUTH` | No | Defaults to `3/10min` (declared; the routes currently use hard-coded limits) |
| `RATE_LIMIT_FACEBOOK_PAGES` | No | Defaults to `2/hour` (declared; the routes currently use hard-coded limits) |
| `RATE_LIMIT_UPLOAD` | No | Defaults to `10/hour` (declared; not wired to a route in the reviewed code) |

Generate an encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Example (placeholders only):

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=social_media_manager
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
JWT_SECRET_KEY=replace-with-a-long-random-string
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret
INSTAGRAM_REDIRECT_URI=http://localhost:8000/api/v1/social-accounts/instagram/callback
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/social-accounts/facebook/callback
FACEBOOK_CONFIG_ID=your-login-for-business-config-id
ENCRYPTION_KEY=replace-with-a-44-character-fernet-key
PUBLIC_BASE_URL=https://your-public-tunnel-or-domain
FRONTEND_BASE_URL=http://localhost:5173
```

> `PUBLIC_BASE_URL` must be reachable from the internet, because Meta downloads uploaded images from it. A local-only address will not work for publishing.

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

If unset, the frontend defaults to `http://127.0.0.1:8000/api/v1`.

---

## Database and Migrations

The repository contains Alembic migrations in `backend/alembic/versions/`. Create the database, configure `backend/.env`, and run:

```bash
cd backend
alembic upgrade head
```

Migrations exist for `users`, `oauth_states`, `social_accounts`, `facebook_oauth_sessions`, `posts`, `post_targets`, `audit_logs`, and a column added to `posts` for the Facebook post ID. Confirm the migration history with `alembic heads` before deploying.

Tables are defined in `backend/app/models/`.

---

## Running the Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API root: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- Interactive API docs: `http://127.0.0.1:8000/docs` (FastAPI default; not disabled in the reviewed code)

Docker:

```bash
cd backend
docker build -t social-media-manager-api .
docker run --env-file .env -p 8000:8000 social-media-manager-api
```

The container listens on `${PORT:-8000}`.

---

## Running the Frontend

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173
```

Other scripts:

```bash
npm run build      # TypeScript check, then production build to dist/
npm run preview    # Serve the production build locally
npm run lint       # ESLint with zero warnings allowed
```

CORS allows origins on ports 5173 to 5177 for `localhost` and `127.0.0.1`.

---

## API Overview

All routes are under `/api/v1`. Protected routes need `Authorization: Bearer <token>`.

### Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create a user (`email`, `password`) |
| `POST` | `/auth/login` | No | OAuth2 password form (`username`, `password`); returns `access_token` |
| `GET` | `/auth/me` | Yes | Current user |

### Social accounts

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/social-accounts` | Yes | List the current user's connected accounts |
| `DELETE` | `/social-accounts/{social_account_id}` | Yes | Disconnect an account the user owns (returns 204) |

### Facebook

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/social-accounts/facebook/authorize` | Yes | Returns `authorization_url` for the logged-in user |
| `GET` | `/social-accounts/facebook/callback` | No (state-validated) | Meta redirect target; redirects to the frontend |
| `GET` | `/social-accounts/facebook/pages?selection_token=...` | Yes | Lists Pages in the pending selection session |
| `POST` | `/social-accounts/facebook/connect` | Yes | Body: `selection_token`, `selected_page_ids`; stores the chosen Pages |

### Instagram

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/social-accounts/instagram/authorize` | Yes | Returns `authorization_url` for the logged-in user |
| `GET` | `/social-accounts/instagram/callback` | No (state-validated) | Meta redirect target; stores the account and redirects to the frontend |

### Posts

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/posts` | Yes | `multipart/form-data`: `target` (`instagram`, `facebook`, or `all`), optional `caption`, `image` file |

Publishing targets **every** connected account for the chosen platform. The reviewed code does not offer per-account selection for posts.

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Status message |
| `GET` | `/health` | `{"status": "healthy"}` |

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| `POST /auth/register` | 3 per hour |
| `POST /auth/login` | 5 per 15 minutes |
| Facebook and Instagram `authorize` | 3 per 10 minutes |
| Facebook and Instagram `callback` | 3 per 10 minutes |
| `GET /social-accounts/facebook/pages` | 2 per hour |
| `POST /posts` | 10 per hour |

Limits are per client IP address. Clients behind a shared network share one limit.

---

## Testing

**There is no automated test suite in this repository yet.**

- `backend/tests/` contains only `__init__.py`.
- The Python files at the root of `backend/` (for example `test_file_validation.py`, `test_rate_limit.py`, `test_delegated_authorization.py`) are **manual scripts**. They print results and do not use a test runner. Some need a configured `.env`, a reachable database, or a running server, and some create or modify database rows. Review a script before running it against any shared environment.
- The `check_*.py`, `diagnose_*.py`, and `debug_*.py` scripts are troubleshooting helpers for Meta and database issues.
- The frontend has no test runner. Use `npm run lint` and `npm run build` to check it.

Example manual run:

```bash
cd backend
python test_file_validation.py
```

Recommended next step: add `pytest` tests for the OAuth state handling, token encryption, file validation, and the publishing orchestration.

---

## Deployment

### Frontend

- `.github/workflows/deploy-frontend.yml` builds `frontend/` with Node 18 and deploys `frontend/dist` to **GitHub Pages**. It runs on pushes to `main` that change `frontend/**`.
- `frontend/vercel.json` rewrites all routes to `/`, so the React Router app works on Vercel.
- The backend CORS list includes a Vercel domain, so the frontend has been served from Vercel at least at some point.

The repository does not confirm which frontend host is current. Choose one and remove the other configuration.

### Backend

- The `backend/Dockerfile` builds a `python:3.12-slim` image and runs Uvicorn on `${PORT:-8000}`.
- The repository contains no backend hosting configuration. Set all environment variables on the host.
- Set `PUBLIC_BASE_URL` to the backend's public HTTPS URL, and register the backend callback URLs in the Meta apps.
- Uploaded files are stored on the local disk at `backend/public/uploads/`. On platforms with ephemeral file systems, uploads disappear on restart. Move uploads to durable storage before production use.

---

## Current Status and Limitations

### Implemented, and reported working by the maintainer

- Connecting an account through the logged-in user's own Meta authorization, and publishing from it. The maintainer reports this path as tested. The repository contains no automated test that proves it.

### Not complete

- **Receiver-authorized connection through a shared link (no Meta tester role):**
  - The Facebook page-selection step requires the admin's JWT. A receiver's browser cannot complete it, and the admin's browser never receives the selection token.
  - The authorization link's state expires after 10 minutes and is single use. There is no persistent invitation record that can be revoked, limited in use count, or extended.
  - Non-role users can only log in after Meta approves **Advanced Access** for the permissions used, which requires App Review and, under Meta's current rules, Business Verification.
  - No end-to-end test with a non-role receiver is recorded in this repository.
- **Token refresh:** Instagram long-lived tokens are stored with an expiry time, but no refresh job or refresh endpoint was found in the reviewed code. Facebook Page tokens are stored without a refresh path.
- **Per-account publishing:** `POST /posts` publishes to all accounts for the platform. Choosing specific accounts is not implemented.
- **Media types:** Images only. No video, carousels, or scheduling.
- **Scheduling and analytics:** not implemented.

### Operational issues to fix before production

- `backend/.env.example` does not list the Facebook variables (`FACEBOOK_*`), `FRONTEND_BASE_URL`, or the `RATE_LIMIT_*` settings, but `app/core/config.py` requires some of them to start the app.
- The repository has no tracked `.dockerignore`. Because the Dockerfile uses `COPY . .`, a local `.env` or `venv/` could end up in the image if they are present when building. Add a `.dockerignore` that excludes `.env`, `venv/`, `__pycache__/`, and `public/uploads/`.
- No formal automated tests (see [Testing](#testing)).
- The repository has no `LICENSE` file.

---

## Roadmap

Suggested next steps, in priority order:

1. **Invitation-based receiver connections:** a persistent invitation record (hashed token, expiry, use limit, revocation), a public receiver page that starts OAuth, and a receiver-facing Facebook page-selection step that does not require the admin's login.
2. **Meta App Review and Business Verification** for Advanced Access, so non-role users can connect.
3. **Token refresh** for Instagram long-lived tokens, and a plan for Facebook Page tokens.
4. **Per-account publishing**, so a user can choose which accounts receive a post.
5. **Durable media storage** (for example object storage with signed URLs) instead of local disk.
6. **Automated tests** with `pytest` for the backend and a test runner for the frontend, with CI checks on pull requests.
7. **Dockerfile hardening:** add `.dockerignore`, and run the container as a non-root user.
8. **Documentation alignment:** complete `.env.example`, and choose one frontend hosting target.

---

## Acknowledgements

- Developed for **Pexdel Solution**.
- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [Vite](https://vite.dev/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/), and [Tailwind CSS](https://tailwindcss.com/).
- Integrates with the [Meta Graph API](https://developers.facebook.com/docs/graph-api/) and [Instagram API with Instagram Login](https://developers.facebook.com/docs/instagram-platform/).

Meta, Facebook, and Instagram are trademarks of their respective owners. This project is not affiliated with or endorsed by Meta.

---

## License

No license file is present in this repository. Add a `LICENSE` file and update this section before publishing the repository publicly.
