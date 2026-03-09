# Disposable Exec

Disposable Exec is a hosted execution API for AI agents, automations, and developer products.

It runs short-lived Python code inside a restricted Docker sandbox and returns structured execution results instead of running untrusted code on the user's machine or app server.

## What it is

Disposable Exec is built for:

- AI-generated code execution
- agent tool execution
- short-lived remote sandbox jobs
- developer products that need a safe code runtime

## What it is not

Disposable Exec is not:

- a general cloud compute platform
- an AWS Lambda replacement
- an online IDE
- a long-running jobs platform

## Core value

Disposable Exec reduces:

- sandbox setup work
- Docker/runtime maintenance work
- API key and quota implementation work
- subscription and billing skeleton work
- operational risk of running AI-generated code directly on your own host

## Current capabilities

- Run short-lived Python scripts remotely
- Return structured execution results:
  - `stdout`
  - `stderr`
  - `exit_code`
  - `duration`
- Queue-based execution
- Worker-based processing
- Docker sandbox isolation
- API key authentication
- Monthly quota enforcement
- Subscription-aware access control
- API key create/list/disable
- Basic rate limiting
- Billing webhook abstraction
- Admin-protected subscription inspection

## Current architecture

```text
Client / SDK / API caller
        ↓
      FastAPI
        ↓
Auth / Quota / Rate Limit / Subscription Check
        ↓
     Redis Queue
        ↓
       Worker
        ↓
   Docker Sandbox
        ↓
stdout / stderr / exit_code / duration
        ↓
SQLite storage
```

## Current pricing

- Free: 50 executions
- Starter: $9 / month — 3,000 executions
- Pro: $29 / month — 12,000 executions
- Scale: $99 / month — 40,000 executions

## API overview

### `POST /run`

Submit a Python script for execution.

Request:

```json
{
  "script": "print(2 + 2)"
}
```

Example response:

```json
{
  "execution_id": "2f1f8a50-0b70-4af0-b9ba-b9d4b9ef2d56",
  "plan": "Starter",
  "used": 1,
  "quota": 3000
}
```

### `GET /status/{execution_id}`

Returns execution metadata for the current authenticated key/user.

Example response:

```json
{
  "execution_id": "2f1f8a50-0b70-4af0-b9ba-b9d4b9ef2d56",
  "status": "finished",
  "created_at": "2026-03-09T10:00:00Z",
  "updated_at": "2026-03-09T10:00:02Z"
}
```

Possible status values:

- `queued`
- `running`
- `finished`
- `failed`

### `GET /result/{execution_id}`

Returns structured execution output for the current authenticated key/user.

Example response:

```json
{
  "execution_id": "2f1f8a50-0b70-4af0-b9ba-b9d4b9ef2d56",
  "stdout": "4\n",
  "stderr": "",
  "exit_code": 0,
  "duration": 0.12,
  "created_at": "2026-03-09T10:00:02Z"
}
```

### `GET /me`

Returns current API key metadata and latest subscription snapshot.

### API key routes

- `GET /apikey`
- `POST /apikey`
- `DELETE /apikey/{key_id}`

## Billing webhook routes

Current routes:

- `POST /billing/webhook/paddle`
- `POST /billing/webhook/lemon`
- `POST /billing/webhook/polar`
- `POST /billing/webhook/stripe`

These routes normalize provider events into a shared internal subscription model.

## Local development

### 1. Build the sandbox image

```bash
docker build -t disposable-exec-sandbox -f Dockerfile.sandbox .
```

### 2. Prepare environment file

Copy the example file:

```bash
cp .env.example .env
```

Then edit `.env` and set real values for:

- `DISPOSABLE_EXEC_ADMIN_TOKEN`
- `DISPOSABLE_EXEC_PADDLE_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_LEMON_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_POLAR_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_STRIPE_WEBHOOK_SECRET`

### 3. Start Redis

```bash
bash scripts/start_redis.sh
```

You can also run the Redis bootstrap helper first:

```bash
bash scripts/start_all.sh
```

Then start the API server and worker in separate terminals:

```bash
bash scripts/start_server.sh
bash scripts/start_worker.sh
```

### 4. Start the API server

```bash
bash scripts/start_server.sh
```

### 5. Start the worker

```bash
bash scripts/start_worker.sh
```

## Production-style startup order

For a minimal production-like run:

1. Build sandbox image
2. Prepare `.env`
3. Start Redis
4. Start API server
5. Start worker

Recommended startup order:

```text
Docker sandbox image
→ Redis
→ FastAPI server
→ Worker
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"script":"print(7+7)"}'
```

## Example admin request

```bash
curl -H "X-Admin-Token: YOUR_REAL_ADMIN_TOKEN" \
http://127.0.0.1:8000/admin/subscriptions
```

## Example webhook request

```bash
curl -X POST http://127.0.0.1:8000/billing/webhook/paddle \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_PADDLE_WEBHOOK_SECRET" \
  -d '{"user_id":"user_001","subscription_id":"sub_001","plan":"Pro","status":"active"}'
```

## Current storage model

Current MVP storage is SQLite-based.

Stored in SQLite:

- users
- api_keys
- subscriptions
- usage_counters
- execution_status
- execution_results
- rate_limits

Current local storage directory:

- `storage/app.db`
- `storage/execution_logs.jsonl`

## Environment variables

Main required environment variables:

- `DISPOSABLE_EXEC_ADMIN_TOKEN`
- `DISPOSABLE_EXEC_PADDLE_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_LEMON_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_POLAR_WEBHOOK_SECRET`
- `DISPOSABLE_EXEC_STRIPE_WEBHOOK_SECRET`

Optional runtime variables:

- `DISPOSABLE_EXEC_HOST`
- `DISPOSABLE_EXEC_PORT`
- `DISPOSABLE_EXEC_REDIS_HOST`
- `DISPOSABLE_EXEC_REDIS_PORT`
- `DISPOSABLE_EXEC_SANDBOX_IMAGE`

## Security notes

Disposable Exec is intended for short-lived execution workloads only.

Current sandbox direction includes:

- Docker-based isolation
- memory limits
- CPU limits
- PID limits
- read-only filesystem
- no outbound network
- timeout enforcement

This project should still be treated as an early hosted execution skeleton, not a finished enterprise sandbox product.

## Current project stage

Disposable Exec is no longer in the 0 to 1 idea stage.

Current stage:

- launch cleanup
- security hardening
- billing closure
- deployment preparation
- docs and distribution preparation

## Current validated areas

Validated so far:

- admin token protection
- webhook secret gate
- webhook subscription writes
- active subscription enforcement
- canceled subscription enforcement
- past_due subscription enforcement
- paused subscription enforcement
- plan quota switching
- `/me` subscription visibility

## Current priorities

High priority:

- stable startup flow
- deployment cleanup
- log and storage path cleanup
- production run documentation
- webhook signature verification upgrade

Later:

- stronger billing lifecycle
- observability
- stronger abuse controls
- Postgres migration
- more SDK examples
- agent framework integrations

## License

MIT