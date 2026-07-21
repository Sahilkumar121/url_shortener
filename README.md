# URL Shortener API
 
A URL shortening service built with **FastAPI**, featuring user authentication, click analytics, QR code generation, and rate limiting.
 
## Features
 
- 🔗 **URL Shortening** – Convert long URLs into short, shareable links
- 👤 **User Authentication** – Secure signup/login with JWT-based auth
- 📊 **Click Analytics** – Track click events (timestamp, source, etc.) for each shortened URL
- 🧑‍💼 **Admin Controls** – Dedicated admin routes for managing users and URLs
- 📱 **QR Code Generation** – Generate QR codes for shortened URLs
- 🚦 **Rate Limiting** – Prevent abuse with request throttling (via SlowAPI)
- 🔒 **Secure Password Hashing** – Argon2-based hashing via `pwdlib`
## Tech Stack
 
| Component        | Technology                          |
|-------------------|--------------------------------------|
| Framework         | FastAPI                             |
| Database ORM      | SQLAlchemy (async, with `aiosqlite`)|
| Auth              | PyJWT / python-jose, pwdlib (Argon2)|
| Validation        | Pydantic v2 (`pydantic-settings`)   |
| Rate Limiting     | SlowAPI                             |
| QR Codes          | `qrcode[pil]`                       |
| Server            | Uvicorn                             |
 
## Project Structure
 
```
├── core
│   ├── rate_limiting.py     # Rate limiting configuration (SlowAPI)
│   └── security.py          # Password hashing & JWT logic
├── models
│   ├── click_events.py      # Click event ORM model
│   ├── urls.py              # URL ORM model
│   └── users.py             # User ORM model
├── routers
│   ├── admin.py             # Admin-only endpoints
│   ├── auth.py               # Signup/login/token endpoints
│   ├── redirect.py           # Short-code redirection endpoint
│   └── urls.py               # URL creation & management endpoints
├── schemas
│   ├── click_event.py       # Pydantic schemas for click events
│   ├── url.py                # Pydantic schemas for URLs
│   └── user.py               # Pydantic schemas for users
├── services
│   └── shortner.py          # Core URL shortening logic
├── utils
│   └── qrcode.py             # QR code generation helper
├── config.py                 # App settings/config
├── database.py                # DB engine & session setup
├── dependencies.py            # Shared FastAPI dependencies
└── main.py                    # App entry point
```
 
## Getting Started
 
### Prerequisites
 
- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
### Installation
 
Clone the repository and install dependencies:
 
```bash
git clone <your-repo-url>
cd url-shortner
 
# Using uv
uv sync
 
# Or using pip
pip install -e .
```
 
### Environment Variables
 
Create a `.env` file in the project root:
 
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
 
### Running the App
 
```bash
uvicorn main:app --reload
```
 
The API will be available at `http://127.0.0.1:8000`.
 
Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
 
## API Overview
 
| Endpoint Group | Description                                  |
|-----------------|-----------------------------------------------|
| `/auth`         | User registration, login, and token issuance |
| `/urls`         | Create, list, update, and delete short URLs  |
| `/{short_code}` | Redirect to the original long URL             |
| `/admin`        | Admin-level management of users and URLs      |
 
> Refer to the `/docs` endpoint for the complete, auto-generated API reference.
 
## Roadmap / Ideas
 
- [ ] Custom alias support for short URLs
- [ ] Expiring/temporary links
- [ ] Analytics dashboard (clicks over time, geography, device)
- [ ] Bulk URL shortening
## License
 
This project is open source and available under the [MIT License](LICENSE).
