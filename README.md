# CorpWatch — Enterprise Monitoring and Alerting Platform

CorpWatch is a Python-based enterprise monitoring and alerting platform.

CorpWatch monitors websites and API endpoints, stores health check results in MariaDB, detects failures, opens and resolves alerts, sends SMTP email notifications, writes logs, runs background checks, and provides a local AI assistant through Telegram.

---

## Main Features

* Python HTTP API
* REST-like API endpoints
* MariaDB database
* Monitoring targets CRUD
* Manual health checks
* Scheduled background health checks
* Failure threshold logic
* Alert lifecycle: open / resolve
* SMTP email notifications
* Notification history
* Summary reports
* Application logging
* Docker Compose multi-container deployment
* phpMyAdmin for database inspection
* Local LLM through Ollama
* AI assistant API
* Telegram bot integration
* Telegram intent routing:

  * manual check
  * system summary
  * free chat
  * target info without check

---

## Architecture

```text
Telegram User
    ↓
corpwatch_telegram_bot
    ↓ HTTP
corpwatch_ai_assistant
    ↓ HTTP
corpwatch_app
    ↓
MariaDB

corpwatch_ai_assistant
    ↓ HTTP
Ollama local LLM
```

Background monitoring:

```text
corpwatch_worker
    ↓
checks active targets
    ↓
writes check_results / alerts / notifications
    ↓
MariaDB
```

---

## Docker Services

```text
db              MariaDB database
app             Python HTTP API server
worker          Background monitoring worker
phpmyadmin      Database web UI
ollama          Local LLM runtime
ai_assistant    Local AI assistant API
telegram_bot    Telegram bot with long polling
```

---

## Technology Stack

* Python 3.12
* MariaDB
* PyMySQL
* Docker
* Docker Compose
* phpMyAdmin
* Ollama
* qwen2.5:3b local LLM model
* Telegram Bot API
* SMTP email
* PowerShell
* GitHub

---

## Project Structure

```text
corpwatch/
│
├── api/
├── config/
├── logs/
├── models/
├── repositories/
├── scripts/
├── services/
├── sql/
├── tests/
├── utils/
│
├── ai_assistant.py
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
├── ROADMAP.md
├── telegram_bot.py
└── worker.py
```

---

## API Endpoints

### CorpWatch API

```text
GET  /api/health
GET  /api/targets
GET  /api/targets/{id}
POST /api/targets
PUT  /api/targets/{id}
DELETE /api/targets/{id}
POST /api/targets/{id}/check
GET  /api/reports/summary
```

Protected endpoints require:

```text
X-API-Key: <API_KEY>
```

### AI Assistant API

```text
GET  /ai/health
POST /ai/explain
```

Example request:

```json
{
  "question": "проверь target 4",
  "run_check": true,
  "mode": "manual_check"
}
```

Supported AI modes:

```text
manual_check
system_summary
free_chat
```

---

## AI Assistant Design

CorpWatch uses a local AI assistant powered by Ollama.

The AI assistant does not replace deterministic monitoring logic.

Python code is responsible for:

```text
running checks
classifying result_type
opening alerts
resolving alerts
sending notifications
keeping technical fields stable
```

Ollama is responsible for:

```text
explaining verified monitoring facts
rewriting system summary into human language
answering free chat questions
```

The LLM does not change:

```text
HTTP status codes
result_type
alert status
severity
notification status
target name
target URL
```

---

## Telegram Bot Behavior

### Show all targets

```text
/targets
```

### Show target info without running a check

```text
4
target 4
цель 4
таргет 4
id 4
```

Expected behavior:

```text
Show target information.
Do not run manual check.
Do not send email notification.
```

### Run manual check

```text
проверь target 4
check target 4
```

Expected behavior:

```text
Run manual check.
Explain result through AI assistant.
Show stable technical details.
```

### Show system summary

```text
что сейчас с системой?
что с системой?
статус системы
summary
```

Expected behavior:

```text
Show monitoring summary.
If open_alerts > 0, the system must not be described as stable.
```

### Free chat

```text
что такое API?
какой сегодня день?
что ты думаешь о динозаврах?
```

Expected behavior:

```text
Answer as a normal local AI assistant.
Do not force CorpWatch monitoring context into unrelated questions.
```

---

## Demo Targets

Current demo targets:

```text
1 — Google Homepage — https://www.google.com
2 — Currency API — https://api.frankfurter.app/latest
3 — Cloudflare Homepage — https://www.cloudflare.com
4 — CorpWatch Demo Website — https://spectrdiagnostic.com
```

Main demo target:

```text
target 4 — CorpWatch Demo Website
```

---

## Running the Project

Start all services:

```powershell
docker compose up -d --build
```

Check running containers:

```powershell
docker ps
```

Check API health:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/health" |
ConvertTo-Json -Depth 10
```

Check targets:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/targets" |
ConvertTo-Json -Depth 10
```

Check summary report:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/reports/summary" |
ConvertTo-Json -Depth 20
```

---

## Ollama Check

```powershell
$body = @{
    model = "qwen2.5:3b"
    prompt = "say ok"
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:11434/api/generate" `
  -ContentType "application/json" `
  -Body $body
```

---

## Demo Scenario

### 1. Show targets

Telegram:

```text
/targets
```

### 2. Show target info

Telegram:

```text
target 4
```

Expected:

```text
Target information is shown.
No check is started.
```

### 3. Manual check while site is working

Telegram:

```text
проверь target 4
```

Expected:

```text
Status: OK
Result: SUCCESS
Actual HTTP: 200
```

### 4. Simulate failure

Stop local demo site container:

```powershell
docker stop spectr_demo_site
```

Telegram:

```text
проверь target 4
```

Expected:

```text
Status: ПРОБЛЕМА
Result: WRONG_STATUS
Actual HTTP: 502
Alert: OPENED or ALREADY_OPEN
Severity: HIGH
```

### 5. System summary

Telegram:

```text
что сейчас с системой?
```

Expected:

```text
System is not fully stable if open_alerts > 0.
```

### 6. Recovery

Start local demo site container:

```powershell
docker start spectr_demo_site
```

Telegram:

```text
проверь target 4
```

Expected:

```text
Status: OK
Result: SUCCESS
Alert: NO_ALERT or RESOLVED
```

### 7. Free chat

Telegram:

```text
что такое API?
```

Expected:

```text
The assistant answers as a general local AI assistant.
```

---

## Useful Commands

Restart AI services:

```powershell
docker compose up -d --build ai_assistant telegram_bot
```

View logs:

```powershell
docker logs corpwatch_ai_assistant
docker logs corpwatch_telegram_bot
docker logs corpwatch_app
docker logs corpwatch_worker
```

Stop project:

```powershell
docker compose down
```

---

## Security Note

The project uses basic API key protection for unsafe operations such as POST, PUT and DELETE.

Real secrets must not be committed to GitHub.

The repository should contain:

```text
.env.example
```

The repository must not contain:

```text
.env
SMTP passwords
Telegram bot token
real API keys
```

---

## Current Status

CorpWatch is almost ready for final defense.

Completed:

```text
API
Database
Worker
Alerts
Notifications
Reports
Ollama
AI Assistant
Telegram bot
Manual check
System summary
Free chat
Roadmap update
```

Remaining:

```text
Final DEMO.md
Final testing
Final documentation commit
```
