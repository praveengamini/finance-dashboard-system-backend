# Zorvyn Finance API

A production-grade, role-based finance data processing and access control backend. Built to handle financial records, user roles, and dashboard analytics for a company's internal finance team.

**Stack:** FastAPI · SQLAlchemy 2.0 async · PostgreSQL · Supabase Auth · Python 3.11+ · uv

[![GitHub](https://img.shields.io/badge/GitHub-praveengamini%2Ffinance--dashboard--system--backend-blue)](https://github.com/praveengamini/finance-dashboard-system-backend)

---

## 📋 Table of Contents

- [What This Does](#-what-this-does)
- [Tech Stack](#-tech-stack--why)
- [Quick Start](#-quick-start-5-minutes)
- [Admin Account Setup](#-admin-account-setup-critical)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Role Access Matrix](#-role-access-matrix)
- [Data Models](#-data-models)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 What This Does

An internal finance dashboard backend with strict role-based access control. Different team members interact with financial data based on their assigned role:

| Role | Real-world equivalent | Can do |
|---|---|---|
| **👨‍💼 Admin** | Finance Manager | Full CRUD on records, manage users/roles, view audit trail |
| **📊 Analyst** | Financial Analyst | Read all records, access detailed breakdowns and trends |
| **👀 Viewer** | Executive / Stakeholder | See summary totals and recent transactions only |

### Example Workflow
1. **Admin** logs in, creates a financial record (expense invoice) → system records who created it and when
2. **Analyst** logs in, runs a report on all Q2 expenses by category → sees full breakdowns
3. **Viewer** logs in, checks the dashboard → sees only total balance and last 10 transactions (no details)

---

## 🛠️ Tech Stack & Why

| Concern | Choice | Why |
|---|---|---|
| **Framework** | FastAPI | Async-native, auto-generates Swagger UI, clean dependency injection |
| **Package manager** | **uv** | 10–100x faster than pip/poetry, deterministic lockfile, zero-config Python version |
| **ORM** | SQLAlchemy 2.0 async | Type-safe queries, never blocks event loop, composable filters |
| **DB driver** | asyncpg | Fastest async PostgreSQL driver for Python |
| **Auth** | Supabase Auth | Managed JWTs, no password hashing in backend, email/OAuth ready |
| **JWT verify** | PyJWT + JWKS (ES256) | Cryptographic verification using Supabase's public key; no shared secrets |
| **Validation** | Pydantic v2 | Field-level validators, enum enforcement, human-readable errors |
| **Config** | pydantic-settings | Type-safe `.env` loading with validation |

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

- **Python 3.11+** ([download](https://www.python.org/downloads/))
- **uv** package manager (`pip install uv`)
- **Supabase account** (free tier works — [sign up](https://app.supabase.com))
- **PostgreSQL database** (Supabase provides one for free)

### Step 1: Clone & Install

```bash
git clone https://github.com/praveengamini/finance-dashboard-system-backend.git
cd finance-dashboard-system-backend
uv sync
```

The `uv sync` command reads `pyproject.toml`, resolves all dependencies, and creates a lockfile. Takes ~5 seconds.

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your Supabase credentials:

```env
# Supabase credentials (from https://app.supabase.com)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key

# PostgreSQL connection (Supabase auto-provides one)
DATABASE_URL=postgresql+asyncpg://postgres:password@host:5432/postgres

# Admin account credentials (you'll create this next)
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=SecurePassword123!
```

> **Where to find Supabase credentials:**
> - Go to [app.supabase.com](https://app.supabase.com) → Select your project
> - **Settings** → **API** → Copy `Project URL` and `anon public key`
> - **Settings** → **Database** → Copy connection string

### Step 3: Prepare Supabase for Local Development

Email confirmation must be **disabled** for local testing (you'll re-enable it for production):

1. Go to Supabase Dashboard → **Authentication** → **Providers** → **Email**
2. Toggle **Confirm email** to OFF
3. Click **Save**

> ⚠️ This allows instant email registration without confirmation links. **Re-enable for production.**

### Step 4: Create Admin Account (Critical!)

Run the admin bootstrap script:

```bash
python seed_admin.py
```

**What this does:**
1. Creates a Supabase auth user with the email/password from `.env`
2. Creates a `profiles` record in the database with `role=admin` and `status=active`
3. Prints confirmation: `✅ Admin profile ready — email: admin@yourcompany.com, role: admin`

**Expected output:**
```
✅ Supabase user created: 550e8400-e29b-41d4-a716-446655440000
✅ Admin profile ready — email: admin@yourcompany.com, role: admin
```

If the admin already exists (ran script twice), it will log:
```
ℹ️  Using existing user: 550e8400-e29b-41d4-a716-446655440000
✅ Admin profile ready — email: admin@yourcompany.com, role: admin
```

> **⚠️ This script must run exactly once before starting the server.**

### Step 5: Start the Server

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 6: Test It Out

#### Option A: Browser (Recommended)
Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** → Swagger UI opens with every endpoint

#### Option B: Test Login with curl
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@yourcompany.com",
  "access_token": "eyJhbGciOiJFUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin"
}
```

Copy the `access_token`. You now have admin access to all endpoints.

---

## 🔐 Admin Account Setup (Critical)

This section explains **exactly** how the admin account is created and why it's essential.

### What Happens When You Run `seed_admin.py`

```mermaid
graph LR
    A["1. Read ADMIN_EMAIL/PASSWORD from .env"] 
    B["2. Create Supabase auth user"]
    C["3. Create profiles record with role=admin"]
    D["✅ Ready to log in"]
    A --> B
    B --> C
    C --> D
```

### Why This Approach?

**Supabase handles authentication**, the backend handles authorization:
- ✅ Passwords are hashed and stored in Supabase (you don't manage passwords)
- ✅ JWTs are signed by Supabase (you verify tokens, don't issue them)
- ✅ The backend only reads the `role` from the `profiles` table

**All new users start as `viewer`** and must be promoted by an admin:
```bash
# Only an admin can run this
PATCH /users/{user_id}/role
{ "role": "analyst" }
```

### If You Need to Reset the Admin Account

**Option 1: Delete and recreate**
```bash
# In Supabase Dashboard → Authentication → Users:
# 1. Find the admin user
# 2. Click the menu (⋯) → Delete user
# 3. Then run: python seed_admin.py
```

**Option 2: Update credentials**
```bash
# Edit .env with new credentials
ADMIN_EMAIL=newadmin@yourcompany.com
ADMIN_PASSWORD=NewPassword123!

# Then run:
python seed_admin.py
```

### Common Admin Setup Issues

| Problem | Solution |
|---|---|
| `seed_admin.py` fails with "Invalid email" | Edit `.env` — use a valid email format |
| "User already exists" | Already ran the script; it's fine. Log in normally. |
| Can't log in with admin credentials | Check `.env` matches what you used in `seed_admin.py` |
| Admin user exists but `role` is `viewer` | Run `seed_admin.py` again to correct the role |
| Email confirmation required in Supabase | Go to Auth → Email → toggle **Confirm email** OFF |

---

## 📁 Project Structure

```
zorvyn-backend/
│
├── main.py                      # FastAPI app, lifespan, CORS setup
├── seed_admin.py                # ⭐ One-time admin bootstrap (run once!)
├── pyproject.toml               # uv dependencies + Python version
├── .env.example                 # Copy to .env and fill in credentials
│
├── auth/                        # Login & registration
│   ├── router.py                # POST /auth/login, POST /auth/register
│   ├── service.py               # Supabase integration
│   └── schemas.py               # Request/response models
│
├── users/                       # User + role management (Admin only)
│   ├── router.py                # CRUD operations on users
│   ├── service.py               # Role promotion, status updates
│   └── schemas.py               # User schemas
│
├── records/                     # Financial records CRUD
│   ├── router.py                # Create, list, update, delete records
│   ├── service.py               # Query filters, soft deletes
│   └── schemas.py               # Record validation
│
├── dashboard/                   # Aggregated analytics
│   ├── router.py                # Summary, categories, trends, recent
│   └── service.py               # SQL aggregations
│
├── core/                        # Cross-cutting concerns
│   ├── config.py                # Settings from .env (pydantic-settings)
│   ├── security.py              # JWT verification + JWKS caching
│   ├── rbac.py                  # require_roles() dependency
│   └── startup.py               # DB health check + table auto-creation
│
└── db/                          # Data layer
    ├── database.py              # Async engine + session factory
    ├── models.py                # SQLAlchemy ORM models (Profile, Record)
    ├── dependencies.py          # get_db() FastAPI dependency
    └── supabase.py              # Supabase client (auth only)
```

---

## 🔌 API Reference

### Authentication

All protected routes require:
```
Authorization: Bearer <access_token>
```

#### POST `/auth/register`
Create a new user account. All new users start with `role=viewer`.

**Request:**
```json
{
  "email": "analyst@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "analyst@example.com",
  "access_token": "eyJhbGciOiJFUzI1NiIs...",
  "token_type": "bearer",
  "role": "viewer"
}
```

**Password requirements:**
- At least 8 characters
- Mix of uppercase, lowercase, numbers (Supabase default policy)

#### POST `/auth/login`
Authenticate and get an access token.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "access_token": "eyJhbGciOiJFUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin"
}
```

---

### Financial Records (Analyst, Admin)

#### POST `/records/create` — Admin only
Create a new financial record.

**Request:**
```json
{
  "amount": 50000.00,
  "type": "income",
  "category": "Client Payment",
  "date": "2024-06-01T00:00:00Z",
  "notes": "Q2 invoice from Acme Corp"
}
```

**Validation:**
- `amount`: Must be > 0
- `type`: Must be `income` or `expense`
- `category`: Required, cannot be empty
- `date`: Defaults to now if omitted

**Response (201):**
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 50000.00,
  "type": "income",
  "category": "Client Payment",
  "date": "2024-06-01T00:00:00Z",
  "notes": "Q2 invoice from Acme Corp",
  "created_at": "2024-06-15T10:30:00Z",
  "updated_at": "2024-06-15T10:30:00Z"
}
```

#### GET `/records/list` — Analyst, Admin
List all financial records with optional filters.

**Query Parameters (all optional):**
```
?type=income                              # Filter by type
?category=Salary                          # Exact category match
?search=invoice                           # Fuzzy search in category + notes
?date_from=2024-01-01T00:00:00Z          # Include from this date
?date_to=2024-12-31T23:59:59Z            # Include until this date
?page=1&page_size=20                      # Pagination
```

**Example:**
```bash
GET /records/list?type=expense&date_from=2024-01-01T00:00:00Z&page_size=10
```

**Response (200):**
```json
{
  "records": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "amount": 5000.00,
      "type": "expense",
      "category": "Office Rent",
      "date": "2024-06-01T00:00:00Z",
      "notes": null,
      "created_at": "2024-06-01T10:00:00Z"
    }
  ],
  "total_records": 42,
  "total_pages": 5
}
```

#### GET `/records/get/{id}` — Analyst, Admin
Get a single record by ID.

**Response (200):**
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "amount": 50000.00,
  "type": "income",
  "category": "Client Payment",
  "date": "2024-06-01T00:00:00Z",
  "notes": "Q2 invoice",
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2024-06-01T10:00:00Z"
}
```

#### PUT `/records/update/{id}` — Admin only
Update a record (send only fields you want to change).

**Request:**
```json
{
  "notes": "Updated notes",
  "category": "Client Payments - Updated"
}
```

**Response (200):** Updated record object

#### DELETE `/records/delete/{id}` — Admin only
Soft-delete a record (hidden from queries, kept in DB for audit).

**Response (204):** No content

#### GET `/records/deleted` — Admin only
View all soft-deleted records.

**Query Parameters:** Same as `/records/list`

**Response (200):**
```json
{
  "records": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "amount": 1000.00,
      "type": "expense",
      "category": "Old Entry",
      "is_deleted": true,
      "deleted_at": "2024-06-15T12:00:00Z"
    }
  ],
  "total_records": 3,
  "total_pages": 1
}
```

---

### Dashboard & Analytics

#### GET `/dashboard/summary` — All roles
Get total income, expenses, and net balance.

**Query Parameters (optional):**
```
?date_from=2024-01-01T00:00:00Z
?date_to=2024-12-31T23:59:59Z
```

**Response (200):**
```json
{
  "total_income": 150000.00,
  "total_expense": 42000.00,
  "net_balance": 108000.00
}
```

**What each role sees:**
- **Viewer**: Full summary (totals only, no details)
- **Analyst**: Same as Viewer
- **Admin**: Same as Viewer

#### GET `/dashboard/recent` — All roles
Get the 10 most recent non-deleted records.

**Response (200):**
```json
[
  {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "amount": 5000.00,
    "type": "expense",
    "category": "Office Rent",
    "date": "2024-06-15T00:00:00Z",
    "created_at": "2024-06-15T10:00:00Z"
  }
]
```

#### GET `/dashboard/categories` — Analyst, Admin
Breakdown of spending/income by category.

**Query Parameters (optional):**
```
?date_from=2024-01-01T00:00:00Z
?date_to=2024-12-31T23:59:59Z
```

**Response (200):**
```json
[
  {
    "category": "Salary",
    "type": "expense",
    "total": 30000.00,
    "count": 3
  },
  {
    "category": "Client Payment",
    "type": "income",
    "total": 120000.00,
    "count": 5
  }
]
```

#### GET `/dashboard/trends` — Analyst, Admin
Monthly income and expense totals (useful for charts).

**Query Parameters (optional):**
```
?date_from=2024-01-01T00:00:00Z
?date_to=2024-12-31T23:59:59Z
```

**Response (200):**
```json
[
  {
    "month": "2024-06",
    "income": 100000.00,
    "expense": 25000.00
  },
  {
    "month": "2024-07",
    "income": 50000.00,
    "expense": 17000.00
  }
]
```

---

### User Management (Admin only)

#### GET `/users/` — Admin only
List all users in the system.

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@example.com",
    "role": "admin",
    "status": "active",
    "created_at": "2024-06-01T10:00:00Z"
  },
  {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "analyst@example.com",
    "role": "analyst",
    "status": "active",
    "created_at": "2024-06-02T10:00:00Z"
  }
]
```

#### GET `/users/{id}` — Admin only
Get a single user.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "role": "admin",
  "status": "active",
  "created_at": "2024-06-01T10:00:00Z"
}
```

#### PATCH `/users/{id}/role` — Admin only
Promote/demote a user's role.

**Request:**
```json
{
  "role": "analyst"
}
```

**Valid values:** `admin`, `analyst`, `viewer`

**Response (200):** Updated user object

#### PATCH `/users/{id}/status` — Admin only
Activate or deactivate a user.

**Request:**
```json
{
  "status": "inactive"
}
```

**Valid values:** `active`, `inactive`

When `inactive`, the user gets a `403 Forbidden` on all protected routes.

**Response (200):** Updated user object

---

## 📊 Role Access Matrix

### Auth & User Management

| Endpoint | Method | Viewer | Analyst | Admin |
|---|---|:---:|:---:|:---:|
| `/auth/register` | POST | ✅ | ✅ | ✅ |
| `/auth/login` | POST | ✅ | ✅ | ✅ |
| `/users/` | GET | ❌ | ❌ | ✅ |
| `/users/{id}` | GET | ❌ | ❌ | ✅ |
| `/users/{id}/role` | PATCH | ❌ | ❌ | ✅ |
| `/users/{id}/status` | PATCH | ❌ | ❌ | ✅ |

### Financial Records

| Endpoint | Method | Viewer | Analyst | Admin |
|---|---|:---:|:---:|:---:|
| `/records/create` | POST | ❌ | ❌ | ✅ |
| `/records/list` | GET | ❌ | ✅ | ✅ |
| `/records/get/{id}` | GET | ❌ | ✅ | ✅ |
| `/records/update/{id}` | PUT | ❌ | ❌ | ✅ |
| `/records/delete/{id}` | DELETE | ❌ | ❌ | ✅ |
| `/records/deleted` | GET | ❌ | ❌ | ✅ |

### Dashboard & Analytics

| Endpoint | Method | Viewer | Analyst | Admin |
|---|---|:---:|:---:|:---:|
| `/dashboard/summary` | GET | ✅ | ✅ | ✅ |
| `/dashboard/recent` | GET | ✅ | ✅ | ✅ |
| `/dashboard/categories` | GET | ❌ | ✅ | ✅ |
| `/dashboard/trends` | GET | ❌ | ✅ | ✅ |

---

## 💾 Data Models

### Profile (User Account)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Supabase auth user ID |
| `email` | VARCHAR | Unique, from Supabase |
| `role` | ENUM | `viewer` \| `analyst` \| `admin` |
| `status` | ENUM | `active` \| `inactive` |
| `created_at` | TIMESTAMPTZ | Auto-set on creation |

### Record (Financial Entry)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Auto-generated primary key |
| `user_id` | UUID | FK → profiles.id (who created it) |
| `amount` | NUMERIC | Must be > 0 |
| `type` | ENUM | `income` \| `expense` |
| `category` | VARCHAR | Required, searchable |
| `date` | TIMESTAMPTZ | Defaults to now() |
| `notes` | TEXT | Optional, searchable |
| `is_deleted` | BOOLEAN | Soft delete flag |
| `created_at` | TIMESTAMPTZ | Auto-set |
| `updated_at` | TIMESTAMPTZ | Auto-updated on modify |

---

## 🔍 Troubleshooting

### Installation & Setup

**Q: `uv command not found`**
```bash
pip install uv
```

**Q: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Make sure you ran:
uv sync
```

**Q: `.env: No such file or directory`**
```bash
cp .env.example .env
# Then fill in your Supabase credentials
```

### Admin Account Issues

**Q: `seed_admin.py` fails with auth error**

Check that:
1. `SUPABASE_URL` and `SUPABASE_KEY` are correct (from [app.supabase.com](https://app.supabase.com))
2. Email confirmation is disabled in Supabase (Auth → Email → toggle **Confirm email** OFF)
3. The password meets requirements (8+ chars, mixed case/numbers)

**Q: `seed_admin.py` succeeded but I can't log in**

1. Check that `.env` credentials match what `seed_admin.py` used
2. Verify the `profiles` table has a row with your email and `role=admin`:
   ```bash
   # In Supabase SQL editor:
   SELECT * FROM profiles WHERE email = 'admin@yourcompany.com';
   ```
   Should show `role: admin`, `status: active`

3. If role is `viewer`, run `seed_admin.py` again to correct it

**Q: Can't find Supabase credentials**

1. Go to [app.supabase.com](https://app.supabase.com)
2. Click your project
3. **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY`

### Runtime Issues

**Q: `401 Unauthorized` on a protected endpoint**

The JWT token in your `Authorization` header is invalid or missing.

**Solution:**
1. Make sure header is: `Authorization: Bearer <access_token>`
2. Re-login to get a fresh token: `POST /auth/login`
3. Check token expiry (Supabase JWTs expire after ~1 hour)

**Q: `403 Forbidden` even with admin account**

The user exists but:
1. `role` is not `admin` — run `seed_admin.py` again
2. `status` is `inactive` — promote via `PATCH /users/{id}/status`

**Q: Records not appearing in list**

Check if they're soft-deleted:
```bash
GET /records/deleted
```

**Q: `422 Validation Error` on record creation**

Verify:
- `amount` > 0
- `type` is exactly `"income"` or `"expense"` (case-sensitive)
- `category` is not empty
- `date` is ISO 8601 format: `2024-06-01T00:00:00Z`

### Database Issues

**Q: `ERROR: database "postgres" does not exist`**

The PostgreSQL database is not set up. Supabase provides one for free — get the `DATABASE_URL` from your Supabase project settings.

**Q: `tables don't exist` error**

Tables are auto-created on startup. Restart the server:
```bash
# Stop the server (Ctrl+C)
# Then:
uvicorn main:app --reload
```

Check the startup logs for:
```
INFO: Creating tables...
✅ Tables created
```

---

## 🚢 Deployment

### Environment Variables for Production

Before deploying, update `.env` (or your secrets manager) with production values:

```env
# Use production Supabase project
SUPABASE_URL=https://prod-project.supabase.co
SUPABASE_KEY=prod-anon-key

# Use production PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@prod-host:5432/dbname

# Secure admin password
ADMIN_EMAIL=admin@company.com
ADMIN_PASSWORD=VerySecurePassword123!
```

### Re-enable Email Confirmation

In production, re-enable email verification:

1. Supabase Dashboard → **Authentication** → **Providers** → **Email**
2. Toggle **Confirm email** to ON
3. Users will receive confirmation links

### Recommended Hosting

- **Backend:** Railway, Render, Fly.io (all support FastAPI + PostgreSQL)
- **Database:** Supabase (included free tier or upgrade as needed)

---

## 📝 Key Technical Decisions

### Why uv over pip/poetry?

uv is 10–100x faster. `uv sync` resolves all dependencies and creates a lockfile in seconds instead of minutes. For CI/CD pipelines, this saves significant time.

### JWT Verification via JWKS

Supabase now issues EC-signed tokens (ES256). The backend fetches Supabase's public keys from `/.well-known/jwks.json`, matches the token's `kid` (key ID), and verifies the signature. No shared secrets in the codebase — if Supabase rotates keys, the backend automatically picks up the new ones (cached with TTL).

### Role as a Database Column

Roles are stored in the `profiles` table, not in the JWT. This allows admins to change a user's role instantly without waiting for token refresh. Trade-off: every protected request hits the database. For enterprise scale, consider caching roles with a short TTL.

### Soft Deletes

Records are never hard-deleted. `is_deleted=True` hides them from normal queries but preserves them for audit trails. Admins can review deletions via `GET /records/deleted`.

### Viewer is Intentionally Limited

Viewers can only see summary totals and recent transactions. They cannot:
- Access the full record list
- See detailed breakdowns by category
- View trends

This meaningfully differentiates roles and models a real executive stakeholder who needs high-level visibility, not granular details.

---

