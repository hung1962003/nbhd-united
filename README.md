# NBHD United — Managed OpenClaw Platform

**Control plane for managed OpenClaw instances.** Each subscriber gets a private AI assistant (Telegram, LINE, iOS) powered by OpenClaw running in isolated Azure containers.

> For agent/developer onboarding, prefer [`CLAUDE.md`](CLAUDE.md) and [`docs/agents/`](docs/agents/) — they track production reality more closely than this overview.

## Architecture

This is **NOT** an AI runtime — [OpenClaw](https://github.com/nichochar/openclaw) is the runtime. This repo is the orchestration layer:

```
┌─────────────────┐
│  Channel Users   │  (Telegram / LINE / iOS)
└────────┬────────┘
         │
┌────────▼────────┐     ┌──────────────┐     ┌──────────────┐
│  Message Router  │────▶│  OpenClaw A   │     │  OpenClaw N   │
│  (this service)  │     │  (container)  │ ... │  (container)  │
└────────┬────────┘     └──────┬───────┘     └──────┬───────┘
         │                     │                     │
┌────────▼────────┐     ┌──────▼─────────────────────▼──────┐
│  Stripe Billing  │     │         Azure Key Vault           │
│  (dj-stripe)    │     │  (tenant-scoped OAuth tokens)     │
└─────────────────┘     └───────────────────────────────────┘
```

### Components

| Component | What it does |
|-----------|-------------|
| **Tenants** | User accounts, subscription status, container mapping |
| **Billing** | Stripe subscription, webhook → provisioning triggers |
| **Orchestrator** | Azure Container Apps SDK — create/delete OpenClaw instances |
| **Router** | Channel routers — map users to the correct OpenClaw container |
| **Integrations** | OAuth flows → tokens stored in Azure Key Vault |
| **Dashboard** | DRF API for the Next.js subscriber console |
| **Cron** | QStash-signed scheduled jobs (not Celery) |

### Key Design Decisions

- **One container per user** — true isolation, no shared state
- **Scale-to-zero** — Azure Container Apps idles inactive containers
- **Shared channel bots** — router maps `chat_id → container` and forwards
- **Key Vault for secrets** — Azure RBAC enforces tenant isolation at platform level
- **OpenClaw config template** — generated per tenant with locked `allowFrom`

## Tech Stack

- **Django 6.1** + DRF — REST API / control plane
- **QStash** — all scheduling (never Celery)
- **PostgreSQL 16** — tenant registry, usage tracking
- **Redis** — caching
- **dj-stripe** — Stripe billing integration
- **Azure Container Apps** — OpenClaw instance hosting
- **Azure Key Vault** — tenant-scoped secret storage
- **Next.js 16** — subscriber console (`frontend/`)

## Quick Start

```bash
# Clone and enter
cd nbhd-united

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt

# Configure
cp .env.example .env
# Edit .env — set AZURE_MOCK=true for local dev
# Leave QSTASH_TOKEN empty for sync fallback in local/CI

# Start services
docker compose up -d  # PostgreSQL + Redis

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver
```

Or use the Makefile:
```bash
make setup       # venv + deps
make docker-up   # postgres + redis
make migrate     # run migrations
make run         # dev server
make test        # run tests
```

Frontend:
```bash
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

## Management Commands

```bash
# List all tenants
python manage.py list_tenants
python manage.py list_tenants --status active

# Check container health
python manage.py check_health

# Manual provisioning
python manage.py provision_tenant <tenant-uuid>
python manage.py deprovision_tenant <tenant-uuid>
```

## Project Structure

```
config/              Django settings (base/development/production)
apps/
  tenants/           User model, tenant model, registration
  billing/           Stripe webhooks, usage tracking, budget caps
  orchestrator/      Azure Container Apps lifecycle, config generation
  router/            Channel message routing to OpenClaw instances
  integrations/      OAuth flows, Key Vault token storage
  dashboard/         DRF API for frontend
  cron/              QStash task publishing + signed triggers
  journal/ finance/ fuel/ friends/ lessons/ insights/ …
  pii/ crypto/ evals/ steward/ …
templates/openclaw/  OpenClaw workspace templates (AGENTS.md, etc.)
runtime/openclaw/    Runtime plugins + helpers
frontend/            Next.js subscriber console
docs/                Agents, security, runbooks, reference
infra/               IaC placeholder (prod is Azure-managed — see docs)
```

## Environment Variables

See [`.env.example`](.env.example) for all configuration. Key ones:

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Shared Telegram bot token |
| `TELEGRAM_WEBHOOK_SECRET` | Required non-empty webhook secret for Telegram webhook validation |
| `QSTASH_TOKEN` | Upstash QStash token (empty → sync fallback for local/CI) |
| `QSTASH_CURRENT_SIGNING_KEY` | Verify inbound QStash signatures |
| `QSTASH_NEXT_SIGNING_KEY` | Next key during QStash key rotation |
| `STRIPE_TEST_SECRET_KEY` | Stripe test key when `STRIPE_LIVE_MODE=False` |
| `STRIPE_LIVE_SECRET_KEY` | Stripe live key when `STRIPE_LIVE_MODE=True` |
| `STRIPE_PRICE_STARTER` | Stripe price ID for the starter tier |
| `DJSTRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `ANTHROPIC_API_KEY` | Shared API key for OpenClaw instances |
| `OPENAI_API_KEY` | Shared OpenAI key for Whisper/transcription |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription for Container Apps |
| `AZURE_KEY_VAULT_NAME` | Key Vault for tenant secrets |
| `FRONTEND_URL` | Subscriber console URL |
| `AZURE_MOCK` | Set `true` for local dev without Azure |

## License

Proprietary — NBHD United
"# nbhd-united" 
