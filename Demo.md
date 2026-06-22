# CorpWatch Demo Guide

## 1. Project Name

**CorpWatch — Enterprise Monitoring and Alerting Platform**

CorpWatch is a Python-based monitoring and alerting platform.

It monitors websites and API endpoints, stores health check results in MariaDB, detects failures, opens and resolves alerts, sends SMTP email notifications, runs background checks, and provides a local AI assistant through Telegram.

---

## 2. Demo Goal

The goal of this demo is to show that CorpWatch can:

* monitor real websites and API endpoints
* run manual checks
* run background checks
* detect failures
* open alerts
* resolve alerts after recovery
* send email notifications
* explain monitoring facts through a local AI assistant
* interact with the user through Telegram

---

## 3. Demo Architecture

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

## 4. Docker Services

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

## 5. Main Demo Target

The main demo target is:

```text
Target 4 — CorpWatch Demo Website
URL: https://spectrdiagnostic.com
Expected HTTP status: 200
```

This target is used to demonstrate failure and recovery.

When the local demo website or tunnel is working, CorpWatch should receive HTTP `200`.

When the demo website is stopped or unavailable behind Cloudflare, CorpWatch may receive an error status such as HTTP `502`, `503`, `504`, or another non-expected status.

---

## 6. Start the System

Run:

```powershell
docker compose up -d --build
```

Check containers:

```powershell
docker ps
```

Expected containers:

```text
corpwatch_db
corpwatch_app
corpwatch_worker
corpwatch_phpmyadmin
corpwatch_ollama
corpwatch_ai_assistant
corpwatch_telegram_bot
```

---

## 7. Check API Health

Run:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/health" |
ConvertTo-Json -Depth 10
```

Expected result:

```text
success: true
status: healthy
```

---

## 8. Check AI Assistant Health

Run:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8010/ai/health" |
ConvertTo-Json -Depth 10
```

Expected result:

```text
success: true
service: corpwatch_ai_assistant
status: healthy
```

---

## 9. Show Monitoring Targets

PowerShell:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/targets" |
ConvertTo-Json -Depth 10
```

Telegram:

```text
/targets
```

Expected behavior:

```text
The Telegram bot shows all monitoring targets.
```

Expected demo targets:

```text
1 — Google Homepage — https://www.google.com
2 — Currency API — https://api.frankfurter.app/latest
3 — Cloudflare Homepage — https://www.cloudflare.com
4 — CorpWatch Demo Website — https://spectrdiagnostic.com
```

---

## 10. Show Target Information Without Running a Check

Telegram message:

```text
target 4
```

or:

```text
4
```

Expected behavior:

```text
The bot shows information about Target 4.
No manual check is started.
No email notification is sent.
```

This demonstrates that the Telegram bot can distinguish between:

```text
target information request
manual check request
```

---

## 11. Run Manual Check

Telegram message:

```text
проверь target 4
```

Expected behavior:

```text
CorpWatch runs a manual health check for Target 4.
The AI assistant explains the result in human-readable language.
Technical fields remain stable and deterministic.
```

Expected successful result:

```text
Status: OK
Expected HTTP: 200
Actual HTTP: 200
Result: SUCCESS
```

---

## 12. Simulate Failure

Stop the local demo website container:

```powershell
docker stop spectr_demo_site
```

Then in Telegram:

```text
проверь target 4
```

Expected result:

```text
Status: ПРОБЛЕМА
Expected HTTP: 200
Actual HTTP: non-200 status
Result: WRONG_STATUS
Alert: OPENED or ALREADY_OPEN
Severity: depends on current severity rules
```

The exact HTTP code may depend on Cloudflare or tunnel behavior.

Typical examples:

```text
502
503
504
530
```

The important point is:

```text
CorpWatch expected HTTP 200 but received a different result.
CorpWatch classified the target as failed.
CorpWatch opened or reused an alert.
The AI assistant explained verified monitoring facts.
```

---

## 13. Check System Summary

Telegram message:

```text
что сейчас с системой?
```

Expected behavior:

```text
The AI assistant gives a monitoring summary based on CorpWatch facts.
If open_alerts > 0, the assistant must not describe the system as fully stable.
```

The system summary is generated in two steps:

```text
Python code decides the system status from summary facts.
Ollama rewrites the verified draft into human-readable language.
```

Important rule:

```text
The LLM does not decide whether the system is healthy.
The Python code makes that decision.
```

---

## 14. Simulate Recovery

Start the local demo website container again:

```powershell
docker start spectr_demo_site
```

Then in Telegram:

```text
проверь target 4
```

Expected result:

```text
Status: OK
Expected HTTP: 200
Actual HTTP: 200
Result: SUCCESS
Alert: NO_ALERT or RESOLVED
Notification: NOT_REQUIRED or SENT
```

This demonstrates alert recovery logic.

---

## 15. Free Chat Demo

Telegram message:

```text
Что такое API?
```

or:

```text
Что ты думаешь о динозаврах?
```

Expected behavior:

```text
The request is routed to free_chat mode.
The assistant answers as a general local AI assistant.
It does not force CorpWatch monitoring context into unrelated questions.
```

This demonstrates that the Telegram bot and AI assistant support different intents:

```text
manual_check
system_summary
free_chat
target_info
```

---

## 16. AI Assistant Modes

```text
manual_check
    Used for: проверь target 4
    Behavior: run check and explain result

system_summary
    Used for: что сейчас с системой?
    Behavior: explain monitoring summary

free_chat
    Used for: general questions
    Behavior: normal Ollama answer without forced monitoring context
```

---

## 17. AI Safety Boundary

CorpWatch does not let the LLM make monitoring decisions.

Python is responsible for:

```text
running checks
classifying result_type
detecting failures
opening alerts
resolving alerts
sending notifications
keeping technical fields stable
```

Ollama is responsible for:

```text
explaining verified facts
rewriting system summary
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

This design keeps the monitoring logic reliable while still showing AI value.

---

## 18. Useful Commands

Check summary report:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/reports/summary" |
ConvertTo-Json -Depth 20
```

Check Ollama directly:

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

Check AI assistant free chat directly:

```powershell
$body = @{
    question = "Что ты думаешь о динозаврах?"
    run_check = $false
    mode = "free_chat"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8010/ai/explain" `
  -Headers @{ "X-API-Key" = "change_me" } `
  -ContentType "application/json" `
  -Body $body |
ConvertTo-Json -Depth 10
```

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

## 19. Demo Checklist

```text
[ ] docker compose up -d --build
[ ] docker ps shows all required containers
[ ] /api/health works
[ ] /ai/health works
[ ] /targets works in Telegram
[ ] target 4 shows target info without running a check
[ ] проверь target 4 runs manual check
[ ] stopping spectr_demo_site creates failure
[ ] failure opens or reuses alert
[ ] email notification works
[ ] system summary reports open alerts correctly
[ ] starting spectr_demo_site recovers target
[ ] free chat works for general questions
```

---

## 20. Final Demo Explanation

CorpWatch is an enterprise-style monitoring and alerting platform.

It checks websites and API endpoints, stores results in MariaDB, detects failures, opens and resolves alerts, sends email notifications, and provides reports through an API.

The project also includes a local AI assistant powered by Ollama and connected to Telegram.

The key design decision is that AI does not make monitoring decisions.

Python code performs checks, classifies results, manages alerts, and stores facts.

The local LLM only explains verified facts in human-readable language.

This makes the system both reliable and user-friendly.
