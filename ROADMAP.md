# Enterprise Monitoring and Alerting Platform

## CorpWatch Roadmap / Дорожная карта проекта

---

## 0. Project Goal (Цель проекта)

**CorpWatch** is an enterprise-style monitoring and alerting platform.

**CorpWatch** — это платформа мониторинга и оповещений enterprise-уровня.

The system monitors websites and API endpoints, stores health check results in MariaDB, detects failures, opens and resolves alerts, sends SMTP email notifications, writes logs, runs scheduled background checks, and provides a local AI assistant through Telegram.

Система отслеживает сайты и API endpoints, сохраняет результаты проверок в MariaDB, обнаруживает сбои, открывает и закрывает alerts, отправляет SMTP email notifications, ведёт logs, запускает фоновые проверки и предоставляет локального AI assistant через Telegram.

---

## 1. Project Scope (Границы проекта)

### In Scope (Входит в проект)

* Python HTTP API (HTTP API на Python)
* REST-like endpoints (REST-подобные endpoints)
* MariaDB database (база данных MariaDB)
* Monitoring target management (управление monitoring targets)
* Manual health checks (ручные проверки доступности)
* Scheduled background checks (автоматические фоновые проверки)
* Failure threshold logic (логика порога повторных ошибок)
* Alert lifecycle: open / resolve (жизненный цикл alert: open / resolve)
* SMTP email notifications (SMTP email notifications)
* Notification history (история notifications)
* Summary reports (сводные reports)
* Application logging (логирование приложения)
* Basic API key protection (базовая защита через API key)
* Dockerfile (Dockerfile)
* Docker Compose deployment (развёртывание через Docker Compose)
* PowerShell automation scripts (PowerShell scripts)
* Local LLM with Ollama (локальная LLM через Ollama)
* AI assistant API service (AI assistant API service)
* Telegram bot integration (интеграция Telegram bot)
* GitHub workflow (работа через GitHub)
* Live demonstration (живая демонстрация)

### Out of Scope for Version 1 (Не входит в первую версию)

* Full user authentication system (полная система авторизации)
* Role-based access control (ролевая модель доступа)
* Complex frontend dashboard (сложная frontend panel)
* Kubernetes deployment (развёртывание в Kubernetes)
* Prometheus/Grafana integration (интеграция Prometheus/Grafana)
* Real vulnerability scanning (реальное сканирование уязвимостей)
* Advanced CI/CD pipeline (сложный CI/CD pipeline)
* Production-grade distributed scheduler (production-grade scheduler)
* Long-term Telegram conversation memory (долгосрочная память Telegram-переписки)

---

## 2. Functional Requirements (Функциональные требования)

* **FR-1:** Add monitoring target (добавить monitoring target)
* **FR-2:** View all monitoring targets (просмотреть все monitoring targets)
* **FR-3:** View one monitoring target by ID (просмотреть один target по ID)
* **FR-4:** Update monitoring target settings (обновить настройки target)
* **FR-5:** Deactivate monitoring target using soft delete (деактивировать target через soft delete)
* **FR-6:** Run manual health check (запустить manual health check)
* **FR-7:** Run scheduled background checks (запускать background checks)
* **FR-8:** Store check results in MariaDB (сохранять check results в MariaDB)
* **FR-9:** Detect failures and downtime (обнаруживать failures и downtime)
* **FR-10:** Use failure threshold before opening an alert (использовать failure threshold перед opening alert)
* **FR-11:** Open alert when failure threshold is reached (открывать alert при достижении threshold)
* **FR-12:** Resolve alert after successful recovery check (закрывать alert после successful recovery check)
* **FR-13:** Send SMTP email when alert is opened (отправлять SMTP email при opening alert)
* **FR-14:** Send SMTP email when alert is resolved (отправлять SMTP email при resolving alert)
* **FR-15:** Store notification history (сохранять историю notifications)
* **FR-16:** Provide summary report endpoint (предоставлять summary report endpoint)
* **FR-17:** Provide Telegram access to monitoring state (предоставлять Telegram-доступ к состоянию мониторинга)
* **FR-18:** Provide AI explanation for manual checks (предоставлять AI explanation для manual checks)
* **FR-19:** Provide AI explanation for system summary (предоставлять AI explanation для system summary)
* **FR-20:** Support free chat mode for general questions (поддерживать free chat mode для обычных вопросов)
* **FR-21:** Log API calls, background checks, errors, alerts, and notifications (логировать API calls, checks, errors, alerts и notifications)

---

## 3. Non-Functional Requirements (Нефункциональные требования)

* **NFR-1:** The system must run with `docker compose up` (система должна запускаться через `docker compose up`)
* **NFR-2:** The system must not require local Python installation (система не должна требовать локальной установки Python)
* **NFR-3:** Database data must persist after container restart (данные БД должны сохраняться после restart containers)
* **NFR-4:** Application logs should be stored in a persistent log file (logs должны сохраняться в persistent log file)
* **NFR-5:** The backend must return JSON responses (backend должен возвращать JSON responses)
* **NFR-6:** The application must handle external errors without crashing (приложение должно обрабатывать внешние ошибки без падения)
* **NFR-7:** SMTP credentials must be configured through environment variables (SMTP credentials должны настраиваться через environment variables)
* **NFR-8:** Real secrets must not be committed to GitHub (реальные secrets нельзя коммитить в GitHub)
* **NFR-9:** The project must use layered architecture (проект должен использовать layered architecture)
* **NFR-10:** Business logic must stay outside API handlers (business logic не должна находиться в API handlers)
* **NFR-11:** The LLM must not make monitoring decisions (LLM не должна принимать monitoring decisions)
* **NFR-12:** The AI assistant must explain verified facts only (AI assistant должен объяснять только verified facts)

---

## 4. Technology Stack (Технологический стек)

* Python 3.12
* `http.server` / `BaseHTTPRequestHandler`
* `requests`
* `smtplib`
* `logging`
* MariaDB
* PyMySQL
* Docker
* Docker Compose
* phpMyAdmin
* Ollama
* `qwen2.5:3b` local LLM model
* Telegram Bot API
* PowerShell
* GitHub

---

## 5. Current Architecture (Текущая архитектура)

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

## 6. Docker Compose Services (Docker Compose сервисы)

* `db` / `corpwatch_db` — MariaDB database
* `app` / `corpwatch_app` — Python HTTP API server, port `8000`
* `worker` / `corpwatch_worker` — background monitoring worker
* `phpmyadmin` / `corpwatch_phpmyadmin` — database UI
* `ollama` / `corpwatch_ollama` — local LLM runtime, port `11434`
* `ai_assistant` / `corpwatch_ai_assistant` — AI assistant API, port `8010`
* `telegram_bot` / `corpwatch_telegram_bot` — Telegram bot, long polling

---

## 7. API Endpoints (API endpoints)

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

`POST /ai/explain` supports modes:

```text
manual_check
system_summary
free_chat
```

Example request:

```json
{
  "question": "проверь target 4",
  "run_check": true,
  "mode": "manual_check"
}
```

---

## 8. Database Design (Структура базы данных)

Main tables:

```text
monitoring_targets
check_results
alerts
notifications
```

### monitoring_targets

Stores monitored websites and API endpoints.

Хранит сайты и API endpoints, которые мониторит CorpWatch.

Important fields:

```text
id
user_id
name
url
expected_status
timeout_seconds
max_response_time_ms
check_interval_seconds
failure_threshold
consecutive_failures
is_active
created_at
updated_at
```

### check_results

Stores every health check result.

Хранит результаты каждой проверки.

Important fields:

```text
id
target_id
status_code
response_time_ms
result_type
error_message
checked_at
```

`result_type` can be:

```text
SUCCESS
SLOW_RESPONSE
WRONG_STATUS
TIMEOUT
CONNECTION_ERROR
```

### alerts

Stores opened and resolved alerts.

Хранит открытые и закрытые alerts.

Important fields:

```text
id
target_id
severity
opened_at
resolved_at
status
```

### notifications

Stores notification history.

Хранит историю notifications.

Important fields:

```text
id
alert_id
notification_type
sent_at
status
```

---

## 9. Monitoring Logic (Логика мониторинга)

CorpWatch checks each active target and classifies the result deterministically.

CorpWatch проверяет каждый active target и классифицирует результат детерминированно.

Classification rules:

```text
SUCCESS
    HTTP status matches expected status
    response time is within allowed threshold

SLOW_RESPONSE
    HTTP status is correct
    response time is above max_response_time_ms

WRONG_STATUS
    HTTP status does not match expected status

TIMEOUT
    target does not respond before timeout

CONNECTION_ERROR
    connection failed
```

Alert lifecycle:

```text
failure detected
    ↓
increase consecutive_failures
    ↓
if failure_threshold reached
    ↓
open alert or keep existing alert open
    ↓
send notification

successful check
    ↓
reset consecutive_failures
    ↓
resolve open alert if exists
    ↓
send recovery notification
```

---

## 10. AI Assistant Design (Дизайн AI Assistant)

The AI assistant has three modes.

AI assistant имеет три режима.

### 10.1 manual_check

Used for:

```text
проверь target 4
check target 4
```

Flow:

```text
Telegram bot
    ↓
AI assistant API
    ↓
CorpWatch API manual check
    ↓
Python deterministic diagnosis
    ↓
Ollama human explanation
    ↓
Python stable technical details
    ↓
Telegram answer
```

Important boundary:

```text
Python decides:
- result_type
- HTTP status
- alert status
- severity
- notification status

Ollama explains:
- what happened
- why it matters
- what the user should understand
```

### 10.2 system_summary

Used for:

```text
что сейчас с системой?
статус системы
system status
summary
```

Flow:

```text
CorpWatch summary report
    ↓
Python decides system status
    ↓
Python builds verified summary draft
    ↓
Ollama rewrites draft
    ↓
Telegram answer
```

Important rule:

```text
If open_alerts > 0, the system must not be described as stable.
```

### 10.3 free_chat

Used for general questions:

```text
что такое API?
какой сегодня день?
что ты думаешь о динозаврах?
```

Flow:

```text
Telegram user question
    ↓
free_chat mode
    ↓
Ollama answer
```

Free chat does not force CorpWatch context into unrelated questions.

Free chat не притягивает CorpWatch context к обычным вопросам.

---

## 11. Telegram Bot Behavior (Поведение Telegram bot)

### Commands

```text
/start
/help
/targets
```

### Target info without check

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

### Manual check

```text
проверь target 4
check target 4
manual check target 4
```

Expected behavior:

```text
Run manual check.
Explain result through AI assistant.
Show stable technical details.
```

### System summary

```text
что сейчас с системой?
что с системой?
статус системы
summary
```

Expected behavior:

```text
Show current monitoring summary.
Mention open alerts if they exist.
Do not hide failures.
```

### Free chat

```text
что такое API?
какой сегодня день?
```

Expected behavior:

```text
Answer as a normal local AI assistant.
Do not force CorpWatch monitoring context.
```

---

## 12. AI Safety Boundary (Граница ответственности AI)

CorpWatch does not let the LLM make monitoring decisions.

CorpWatch не позволяет LLM принимать monitoring decisions.

The LLM must not change:

```text
HTTP status codes
result_type
alert status
severity
notification status
target name
target URL
```

The LLM can only:

```text
explain verified facts
rewrite summary draft
answer free chat questions
```

This design keeps monitoring reliable and still demonstrates AI value.

Такой дизайн сохраняет надёжность мониторинга и одновременно показывает ценность AI.

---

## 13. Demo Targets (Demo targets)

Current targets after reset:

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

## 14. Demo Scenario (Сценарий демонстрации)

### Step 1: Start system

```powershell
docker compose up -d --build
```

### Step 2: Show targets

Telegram:

```text
/targets
```

### Step 3: Show target info

Telegram:

```text
target 4
```

Expected:

```text
Target information is shown.
No check is started.
```

### Step 4: Manual check while site is working

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

### Step 5: Simulate failure

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

### Step 6: System summary

Telegram:

```text
что сейчас с системой?
```

Expected:

```text
System is not fully stable if open_alerts > 0.
```

### Step 7: Recovery

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

### Step 8: Free chat

Telegram:

```text
что такое API?
```

Expected:

```text
The assistant answers as a normal AI assistant.
```

---

## 15. Project Structure (Структура проекта)

```text
corpwatch/
│
├── api/
│   └── handlers
│
├── config/
│   └── demo_targets.json
│
├── logs/
│
├── models/
│
├── repositories/
│
├── scripts/
│   ├── Build.ps1
│   ├── Start.ps1
│   ├── Stop.ps1
│   ├── Deploy.ps1
│   └── ResetDB.ps1
│
├── services/
│   ├── ai_assistant_service.py
│   ├── monitoring_service.py
│   ├── notification_service.py
│   └── report_service.py
│
├── sql/
│   └── init.sql
│
├── tests/
│
├── utils/
│   └── logger.py
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

## 16. Completed Work (Что уже сделано)

* Docker Compose infrastructure
* MariaDB schema
* Python API server
* Health endpoint
* Targets API
* Manual check endpoint
* Background worker
* Alert open / resolve lifecycle
* SMTP notifications
* Summary report endpoint
* Logging
* phpMyAdmin support
* Ollama service
* AI assistant API
* Telegram bot
* Telegram `/targets`
* Telegram target info without check
* Telegram manual check
* Telegram system summary
* Telegram free chat mode
* AI safety boundary between Python and LLM
* GitHub commits and push

---

## 17. Remaining Work (Что осталось)

### Required before final defense

* Create or update `DEMO.md`
* Update `README.md` with AI assistant and Telegram sections
* Final demo testing
* Check `.env` is not committed
* Check GitHub repository is clean
* Prepare short defense explanation

### Optional improvements

* Add `/health` command to Telegram bot
* Add `/summary` command to Telegram bot
* Add short conversation memory for Telegram
* Rename AI identity from model name to project name, for example Jarvis
* Improve README diagrams
* Add screenshots for defense

---

## 18. Final Defense Explanation (Объяснение для защиты)

CorpWatch is an enterprise-style monitoring and alerting platform.

CorpWatch checks websites and API endpoints, stores results in MariaDB, detects failures, opens and resolves alerts, sends email notifications, and exposes reports through an API.

The project also includes a local AI assistant powered by Ollama and connected to Telegram.

The important design decision is that AI does not make monitoring decisions. Python code performs checks, classifies results, manages alerts, and stores facts. The local LLM only explains verified facts in human-readable language.

This makes the system both reliable and user-friendly.

---
