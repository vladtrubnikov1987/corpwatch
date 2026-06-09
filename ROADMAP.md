# CorpWatch Roadmap
## Enterprise Monitoring and Alerting Platform
### Дорожная карта проекта: English first + русский перевод

---

## 0. Project Goal (Цель проекта)

**CorpWatch** is an enterprise-style monitoring and alerting platform.

**CorpWatch** — это платформа мониторинга и оповещений enterprise-уровня.

The system monitors websites and API endpoints, stores health check results in MariaDB, detects failures, opens and resolves alerts, sends SMTP email notifications, writes logs, and runs as a Docker Compose multi-container system.

Система отслеживает сайты и API endpoints, сохраняет результаты проверок в MariaDB, обнаруживает сбои, открывает и закрывает alerts, отправляет SMTP email notifications, ведёт logs и запускается как multi-container system через Docker Compose.

---

## 1. Project Scope (Границы проекта)

### In Scope (Входит в проект)

- Python HTTP API (HTTP API на Python)
- REST-like endpoints (REST-подобные эндпоинты)
- MariaDB database (база данных MariaDB)
- Monitoring target management (управление целями мониторинга)
- Manual health checks (ручные проверки доступности)
- Scheduled background checks (автоматические фоновые проверки)
- Failure threshold logic (логика порога повторных ошибок)
- Alert lifecycle: open / resolve (жизненный цикл alert: открыть / закрыть)
- SMTP notifications through a real project email account (SMTP-уведомления через реальный проектный email)
- Optional MailHog support for local testing (опциональная поддержка MailHog для локального тестирования)
- Notification history (история уведомлений)
- Summary reports (сводные отчёты)
- Application logging (логирование приложения)
- Basic API key protection (базовая защита через API key)
- Dockerfile (файл сборки Docker-образа)
- Docker Compose deployment (развёртывание через Docker Compose)
- PowerShell automation scripts (PowerShell-скрипты автоматизации)
- GitHub repository workflow (работа через GitHub-репозиторий)
- Technical report (технический отчёт)
- Live demonstration (живая демонстрация)

### Out of Scope for Version 1 (Не входит в первую версию)

- Full user authentication system (полная система авторизации)
- Role-based access control (ролевая модель доступа)
- Complex frontend dashboard (сложная веб-панель)
- Kubernetes deployment (развёртывание в Kubernetes)
- Celery or APScheduler production scheduler (production-планировщик Celery или APScheduler)
- Prometheus/Grafana integration (интеграция с Prometheus/Grafana)
- Real vulnerability scanning (реальное сканирование уязвимостей)
- Advanced CI/CD pipeline (сложный CI/CD pipeline)

---

## 2. Functional Requirements (Функциональные требования)

- **FR-1:** Add monitoring target (добавить цель мониторинга)
- **FR-2:** View all monitoring targets (просмотреть все цели мониторинга)
- **FR-3:** View one monitoring target by ID (просмотреть одну цель по ID)
- **FR-4:** Update monitoring target settings (обновить настройки цели)
- **FR-5:** Deactivate monitoring target using soft delete (деактивировать цель через soft delete)
- **FR-6:** Run manual health check (запустить ручную проверку)
- **FR-7:** Run scheduled background checks (запускать фоновые проверки по расписанию)
- **FR-8:** Store check results in MariaDB (сохранять результаты проверок в MariaDB)
- **FR-9:** Detect failures and downtime (обнаруживать сбои и недоступность)
- **FR-10:** Use failure threshold before opening an alert (использовать порог повторных ошибок перед открытием alert)
- **FR-11:** Open alert when failure threshold is reached (открывать alert при достижении порога ошибок)
- **FR-12:** Resolve alert after successful recovery check (закрывать alert после успешной проверки восстановления)
- **FR-13:** Send SMTP email notification when alert is opened (отправлять SMTP email при открытии alert)
- **FR-14:** Send SMTP email notification when alert is resolved (отправлять SMTP email при закрытии alert)
- **FR-15:** Store notification history (сохранять историю уведомлений)
- **FR-16:** Provide check history per target (предоставлять историю проверок по каждой цели)
- **FR-17:** Provide summary report endpoint (предоставлять endpoint сводного отчёта)
- **FR-18:** Log API calls, background checks, errors, and notifications (логировать API calls, фоновые проверки, ошибки и уведомления)

---

## 3. Non-Functional Requirements (Нефункциональные требования)

- **NFR-1:** The system must run with `docker compose up` (система должна запускаться через `docker compose up`)
- **NFR-2:** The system must not require local Python installation (система не должна требовать локальной установки Python)
- **NFR-3:** Database data must persist after container restart (данные БД должны сохраняться после перезапуска контейнеров)
- **NFR-4:** Application logs should be stored in a persistent log file (логи приложения должны сохраняться в постоянный log-файл)
- **NFR-5:** The backend must return JSON responses (backend должен возвращать JSON-ответы)
- **NFR-6:** The application must handle external errors without crashing (приложение должно обрабатывать внешние ошибки без падения)
- **NFR-7:** SMTP credentials must be configured through environment variables (SMTP credentials должны настраиваться через переменные окружения)
- **NFR-8:** Real secrets must not be committed to GitHub (реальные secrets нельзя коммитить в GitHub)
- **NFR-9:** The project must use a layered architecture (проект должен использовать слоистую архитектуру)
- **NFR-10:** No SQL in service layer; no business logic in API layer (никакого SQL в service layer; никакой бизнес-логики в API layer)

---

## 4. Technology Stack (Технологический стек)

- Python 3.12 (язык программирования)
- `http.server` / `BaseHTTPRequestHandler` or `ThreadingHTTPServer` (HTTP-сервер из стандартной библиотеки Python)
- `requests` (библиотека для HTTP-запросов)
- `smtplib` (библиотека для SMTP-отправки email)
- `logging` (стандартное логирование Python)
- `threading` (параллельное выполнение через потоки)
- `queue.Queue` optional for email queue (опциональная очередь для email)
- MariaDB (реляционная база данных)
- PyMySQL (подключение Python к MariaDB)
- Docker (контейнеризация)
- Docker Compose (управление несколькими контейнерами)
- phpMyAdmin (веб-интерфейс для MariaDB)
- Real SMTP account (реальный SMTP-аккаунт для проекта)
- MailHog optional for local SMTP testing (MailHog опционально для локального SMTP-теста)
- PowerShell (скрипты автоматизации)
- GitHub (хранение кода и истории изменений)

---

## 5. Project Structure (Структура проекта)

```text
corpwatch/
│
├── api/                      # HTTP endpoints (HTTP-эндпоинты)
├── services/                 # Business logic (бизнес-логика)
├── repositories/             # Database access layer (слой доступа к БД)
├── models/                   # Domain models (доменные модели)
├── utils/                    # Helper functions (вспомогательные функции)
├── config/                   # Configuration (конфигурация)
├── tests/                    # Tests (тесты)
├── logs/                     # Application logs (логи приложения)
├── sql/                      # SQL scripts (SQL-скрипты)
├── scripts/                  # PowerShell scripts (PowerShell-скрипты)
│
├── main.py                   # Application entry point (точка входа)
├── requirements.txt          # Python dependencies (зависимости Python)
├── Dockerfile                # Docker image definition (описание Docker-образа)
├── docker-compose.yml        # Multi-container deployment (развёртывание контейнеров)
├── .env.example              # Environment variables example (пример переменных окружения)
├── .gitignore                # Git ignored files (исключения для Git)
├── README.md                 # Project overview (обзор проекта)
└── ROADMAP.md                # Project roadmap (дорожная карта проекта)
```

---

## 6. Database Design (Проектирование базы данных)

### Tables (Таблицы)

1. `users` — system users / default admin (пользователи системы / default admin)
2. `monitoring_targets` — monitored services (сервисы для мониторинга)
3. `check_results` — health check history (история проверок)
4. `alerts` — opened and resolved failures (открытые и закрытые сбои)
5. `notifications` — email notification history (история email-уведомлений)

### Relationships (Связи)

```text
users 1 → many monitoring_targets

monitoring_targets 1 → many check_results

monitoring_targets 1 → many alerts

alerts 1 → many notifications

notifications.alert_id can be NULL for REPORT notifications
```

### Important Fields (Важные поля)

#### monitoring_targets

- `id`
- `user_id`
- `name`
- `url`
- `expected_status`
- `timeout_seconds`
- `max_response_time_ms`
- `check_interval_seconds`
- `failure_threshold`
- `consecutive_failures`
- `is_active`
- `created_at`
- `updated_at`

#### check_results

- `id`
- `target_id`
- `status_code`
- `response_time_ms`
- `result_type`
- `error_message`
- `checked_at`

`result_type` values:

```text
SUCCESS
SLOW_RESPONSE
WRONG_STATUS
TIMEOUT
CONNECTION_ERROR
```

#### alerts

- `id`
- `target_id`
- `check_result_id`
- `severity`
- `message`
- `is_resolved`
- `created_at`
- `resolved_at`

#### notifications

- `id`
- `alert_id`
- `notification_type`
- `recipient_email`
- `subject`
- `body`
- `status`
- `error_message`
- `sent_at`

`notification_type` values:

```text
FAILURE
SLOW_RESPONSE
RECOVERY
REPORT
```

### Database Indexes (Индексы базы данных)

- `idx_targets_active` for background worker target selection (для выбора активных targets фоновым worker)
- `idx_check_results_target_time` for target history queries (для запросов истории по target)
- `idx_check_results_response_time` for worst response time report (для отчёта по худшему response time)
- `idx_alerts_target_resolved` for active/resolved alerts (для активных и закрытых alerts)
- `idx_notifications_alert` for notification history by alert (для истории уведомлений по alert)

### Transaction Note (Примечание по транзакциям)

`consecutive_failures` is a mutable state field and must be updated through repository-level transaction logic.

`consecutive_failures` — это изменяемое поле состояния, поэтому оно должно обновляться через transaction logic в repository layer.

Manual checks and background checks must use the same repository method for updating failure state.

Manual checks и background checks должны использовать один и тот же repository method для обновления состояния ошибок.

---

## 7. Docker Infrastructure (Docker-инфраструктура)

### Services (Сервисы)

- `app` — Python backend service (Python backend-сервис)
- `db` — MariaDB database service (сервис базы данных MariaDB)
- `phpmyadmin` — database web UI (веб-интерфейс для БД)
- `mailhog` — optional test SMTP service (опциональный тестовый SMTP-сервис)

### Required Files (Обязательные файлы)

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### Docker Goals (Цели Docker-этапа)

- Build Python application image (собрать Docker-образ Python-приложения)
- Start all services with one command (запустить все сервисы одной командой)
- Connect containers by service names (соединять контейнеры по именам сервисов)
- Store MariaDB data in Docker volume (хранить данные MariaDB в Docker volume)
- Store logs in persistent volume or mounted folder (хранить логи в постоянном volume или папке)
- Expose backend API port (открыть порт backend API)

---

## 8. Backend Architecture (Архитектура backend)

The application follows a layered architecture:

Приложение использует слоистую архитектуру:

```text
Client
  |
HTTP request
  |
API Layer
  |
Service Layer
  |
Repository Layer
  |
MariaDB Database
```

### API Layer (Слой API)

- Parse HTTP requests (разбирать HTTP-запросы)
- Validate JSON input (проверять JSON-вход)
- Check API key for unsafe operations (проверять API key для опасных операций)
- Call service layer (вызывать service layer)
- Return JSON responses (возвращать JSON-ответы)

### Service Layer (Слой бизнес-логики)

- Manage monitoring workflow (управлять логикой мониторинга)
- Evaluate check results (оценивать результаты проверок)
- Open and resolve alerts (открывать и закрывать alerts)
- Send notifications (отправлять уведомления)
- Generate reports (создавать отчёты)

### Repository Layer (Слой доступа к данным)

- Execute SQL queries (выполнять SQL-запросы)
- Read and write database records (читать и записывать данные)
- Hide SQL from service layer (скрывать SQL от service layer)

---

## 9. HTTP API Endpoints (HTTP API эндпоинты)

### Health Endpoint (Эндпоинт проверки приложения)

```text
GET /api/health
```

### Monitoring Targets API (API целей мониторинга)

```text
GET    /api/targets
POST   /api/targets
GET    /api/targets/{id}
PUT    /api/targets/{id}
DELETE /api/targets/{id}
```

`DELETE` performs soft delete by setting `is_active = FALSE`.

`DELETE` выполняет soft delete через установку `is_active = FALSE`.

### Health Checks API (API проверок доступности)

```text
POST /api/targets/{id}/check
GET  /api/targets/{id}/checks
GET  /api/checks
```

### Alerts API (API alerts)

```text
GET /api/alerts
GET /api/alerts/{id}
PUT /api/alerts/{id}/resolve
```

### Notifications API (API уведомлений)

```text
GET /api/notifications
```

### Reports API (API отчётов)

```text
GET /api/reports/summary
```

---

## 10. Basic API Key Protection (Базовая защита через API key)

Unsafe operations require an API key.

Опасные операции требуют API key.

### Protected Methods (Защищённые методы)

```text
POST
PUT
DELETE
```

### Header (Заголовок)

```text
X-API-Key: value-from-env
```

### Environment Variable (Переменная окружения)

```text
API_KEY=change_me
```

### Expected Behavior (Ожидаемое поведение)

- Missing API key → `401 Unauthorized` (API key отсутствует → `401 Unauthorized`)
- Invalid API key → `403 Forbidden` (неверный API key → `403 Forbidden`)
- Valid API key → request is processed (верный API key → запрос выполняется)

---

## 11. Monitoring Service (Сервис мониторинга)

- Load monitoring target from database (загружать цель мониторинга из БД)
- Send HTTP request using `requests` (отправлять HTTP-запрос через `requests`)
- Measure response time (измерять время ответа)
- Compare actual status with expected status (сравнивать фактический и ожидаемый статус)
- Compare response time with max allowed time (сравнивать response time с максимальным допустимым временем)
- Detect timeout or connection error (обнаруживать timeout или ошибку подключения)
- Save result to `check_results` (сохранять результат в `check_results`)

### Result Types (Типы результата)

- `SUCCESS` — target is healthy (цель работает нормально)
- `SLOW_RESPONSE` — target is too slow (цель отвечает слишком медленно)
- `WRONG_STATUS` — unexpected status code (неожиданный status code)
- `TIMEOUT` — request timeout (истекло время ожидания)
- `CONNECTION_ERROR` — connection failed (ошибка подключения)

---

## 12. Alert Service (Сервис alerts)

- Track consecutive failures (отслеживать повторные ошибки подряд)
- Compare failures with failure threshold (сравнивать количество ошибок с порогом)
- Open alert when threshold is reached (открывать alert при достижении порога)
- Resolve alert after successful recovery check (закрывать alert после успешной проверки восстановления)
- Assign severity level (назначать уровень серьёзности)
- Pass alert to notification service (передавать alert в notification service)

### Severity Levels (Уровни серьёзности)

- `LOW` — slow response (медленный ответ)
- `MEDIUM` — wrong status code (неверный status code)
- `HIGH` — timeout (превышение времени ожидания)
- `CRITICAL` — connection error or repeated failure (ошибка подключения или повторный сбой)

---

## 13. Notification Service (Сервис уведомлений)

- Send email through real SMTP provider (отправлять email через реальный SMTP provider)
- Optionally support MailHog for local testing (опционально поддерживать MailHog для локального тестирования)
- Store notification history in database (сохранять историю уведомлений в БД)
- Log successful and failed email sending (логировать успешную и неудачную отправку)
- Avoid committing real SMTP credentials to GitHub (не коммитить реальные SMTP credentials в GitHub)

### Email Types (Типы email)

- `FAILURE` — alert opened (alert открыт)
- `SLOW_RESPONSE` — slow response alert (alert из-за медленного ответа)
- `RECOVERY` — alert resolved (alert закрыт после восстановления)
- `REPORT` — monitoring summary report (сводный отчёт мониторинга)

---

## 14. Background Worker (Фоновый worker)

### Version 1 Approach (Подход первой версии)

Use one background worker thread.

Использовать один фоновый поток.

### Responsibilities (Ответственности)

The background worker periodically:

Фоновый worker периодически:

- loads active targets (загружает активные targets)
- selects targets whose next check is due (выбирает targets, у которых наступило время следующей проверки)
- checks each target through MonitoringService (проверяет каждую цель через MonitoringService)
- stores check results (сохраняет результаты)
- opens or resolves alerts if needed (открывает или закрывает alerts при необходимости)
- sends SMTP notifications (отправляет SMTP-уведомления)
- writes logs (пишет logs)

### Future Improvement (Будущее улучшение)

Replace the single worker with scheduler + worker pool + email queue.

Заменить один worker на scheduler + worker pool + email queue.

---

## 15. Reporting (Отчётность)

### Endpoint (Эндпоинт)

```text
GET /api/reports/summary
```

### Report Data (Данные отчёта)

- Total monitoring targets (общее количество целей)
- Active targets (активные цели)
- Total checks (общее количество проверок)
- Successful checks (успешные проверки)
- Failed checks (неуспешные проверки)
- Average response time (среднее время ответа)
- Worst response time (худшее время ответа)
- Active alerts (активные alerts)
- Resolved alerts (закрытые alerts)
- Last check time (время последней проверки)

---

## 16. Logging Strategy (Стратегия логирования)

### Log Levels (Уровни логирования)

- `INFO` — normal system operations (обычные операции системы)
- `WARNING` — slow response or suspicious state (медленный ответ или подозрительное состояние)
- `ERROR` — failure, exception, unavailable service (сбой, исключение, недоступный сервис)

### Logged Events (Логируемые события)

- Application started (приложение запущено)
- Database connected (подключение к БД выполнено)
- API request received (API request получен)
- Monitoring target created (цель мониторинга создана)
- Health check completed (проверка выполнена)
- Alert opened (alert открыт)
- Alert resolved (alert закрыт)
- Email sent (email отправлен)
- Email sending failed (отправка email не удалась)
- Database error (ошибка БД)
- HTTP request error (ошибка HTTP-запроса)
- Unauthorized API request (неавторизованный API-запрос)

---

## 17. Error Handling Strategy (Стратегия обработки ошибок)

The system must handle:

Система должна обрабатывать:

- Invalid JSON body (невалидное JSON-тело запроса)
- Missing required fields (отсутствующие обязательные поля)
- Invalid API key (неверный API key)
- Target not found (цель не найдена)
- Database connection error (ошибка подключения к БД)
- Request timeout (timeout HTTP-запроса)
- Connection error (ошибка подключения)
- SMTP sending error (ошибка отправки SMTP)
- Unknown internal error (неизвестная внутренняя ошибка)

---

## 18. PowerShell Automation Scripts (PowerShell-скрипты автоматизации)

```text
build.ps1      # Build Docker images (собрать Docker-образы)
start.ps1      # Start the system (запустить систему)
stop.ps1       # Stop the system (остановить систему)
redeploy.ps1   # Rebuild and restart the system (пересобрать и перезапустить систему)
```

Optional:

```text
logs.ps1        # View logs (посмотреть логи)
status.ps1      # Show containers status (показать статус контейнеров)
reset-db.ps1    # Reset database volume (сбросить volume базы данных)
healthcheck.ps1 # Check API health (проверить здоровье API)
```

---

## 19. GitHub Implementation (Реализация проекта на GitHub)

### Repository (Репозиторий)

```text
https://github.com/vladtrubnikov1987/corpwatch
```

### Repository Rules (Правила репозитория)

- Keep `README.md` in English (вести `README.md` на английском)
- Keep `ROADMAP.md` with English + Russian translation (вести `ROADMAP.md` на английском с русским переводом)
- Commit `.env.example` (коммитить `.env.example`)
- Never commit real `.env` (никогда не коммитить настоящий `.env`)
- Use clear English commit messages (использовать понятные commit messages на английском)

### Branching Strategy (Стратегия веток)

```text
main        # stable version (стабильная версия)
dev         # development version (версия для разработки)
feature/*   # feature branches (ветки для отдельных функций)
```

### Suggested Feature Branches (Рекомендуемые feature-ветки)

```text
feature/database-schema
feature/docker-compose
feature/backend-skeleton
feature/api-key-protection
feature/targets-api
feature/manual-checks
feature/alerts
feature/smtp-notifications
feature/background-worker
feature/reports
feature/powershell-scripts
feature/tests-and-docs
```

### Commit Style (Стиль коммитов)

```text
init: create project structure
db: add initial MariaDB schema
docker: add docker compose configuration
api: add health endpoint
security: add API key protection
api: add monitoring targets CRUD
service: add manual health check logic
service: add alert lifecycle logic
smtp: add real SMTP notification service
worker: add background monitoring thread
docs: update README with deployment steps
```

---

## 20. Testing Strategy (Стратегия тестирования)

Testing must happen during every phase, not only at the end.

Тестирование должно выполняться на каждом этапе, а не только в конце.

### Test Types (Типы тестов)

- Unit tests (модульные тесты)
- Integration tests (интеграционные тесты)
- Manual API tests (ручные API-тесты)
- Docker deployment tests (тесты Docker-развёртывания)

### Testing Evidence (Доказательства тестирования)

- API request screenshots (скриншоты API-запросов)
- phpMyAdmin screenshots (скриншоты phpMyAdmin)
- Real email screenshot or mailbox proof (скриншот реального email или подтверждение в почте)
- Docker containers status screenshot (скриншот статуса контейнеров)
- Application logs screenshot (скриншот логов приложения)
- Test command output (вывод команды тестирования)

---

## 21. Demo Scenario (Сценарий демонстрации)

### Live Demo Steps (Шаги живой демонстрации)

1. Open GitHub repository (открыть GitHub-репозиторий)
2. Show project structure (показать структуру проекта)
3. Run `start.ps1` (запустить `start.ps1`)
4. Show running containers (показать запущенные контейнеры)
5. Open `GET /api/health` (открыть `GET /api/health`)
6. Add working monitoring target (добавить рабочую цель мониторинга)
7. Add broken monitoring target (добавить нерабочую цель мониторинга)
8. Run manual health check (запустить ручную проверку)
9. Show check history (показать историю проверок)
10. Show alert opened after threshold (показать alert после достижения порога ошибок)
11. Show email notification (показать email-уведомление)
12. Show database tables in phpMyAdmin (показать таблицы в phpMyAdmin)
13. Show application logs (показать логи приложения)
14. Show summary report (показать сводный отчёт)
15. Run `stop.ps1` (запустить `stop.ps1`)

### Demo Notes (Примечания для демонстрации)

For the broken target, set `failure_threshold = 1` so that the alert opens after the first failed manual check.

Для нерабочей цели установить `failure_threshold = 1`, чтобы alert открылся после первой неуспешной ручной проверки.

Alternatively, run several manual checks to reach the configured threshold.

Или запустить несколько manual checks, чтобы достичь установленного threshold.

---

## 22. Development Order (Порядок разработки)

### Phase 1 — Planning and GitHub (Планирование и GitHub)

- Define project scope (определить границы проекта)
- Create GitHub repository (создать GitHub-репозиторий)
- Add README and ROADMAP (добавить README и ROADMAP)
- Add `.gitignore` and `.env.example` (добавить `.gitignore` и `.env.example`)

### Phase 2 — Database Design (Проектирование БД)

- Create `sql/init.sql` (создать `sql/init.sql`)
- Add tables and relationships (добавить таблицы и связи)
- Add indexes (добавить индексы)
- Commit database schema to GitHub (закоммитить схему БД в GitHub)

### Phase 3 — Docker Infrastructure (Docker-инфраструктура)

- Create Dockerfile (создать Dockerfile)
- Create docker-compose.yml (создать docker-compose.yml)
- Add MariaDB service (добавить MariaDB service)
- Add phpMyAdmin service (добавить phpMyAdmin service)
- Configure volumes and environment variables (настроить volumes и environment variables)

### Phase 4 — Backend Core (Ядро backend)

- Create backend skeleton (создать каркас backend)
- Add database connection (добавить подключение к БД)
- Add logging configuration (добавить настройку logging)
- Add health endpoint (добавить health endpoint)

### Phase 5 — API Security and Targets CRUD (API security и CRUD targets)

- Add API key validation (добавить проверку API key)
- Add targets CRUD endpoints (добавить CRUD endpoints для targets)
- Add soft delete logic (добавить soft delete logic)
- Add tests for CRUD operations (добавить тесты для CRUD)

### Phase 6 — Monitoring Logic (Логика мониторинга)

- Add manual health checks (добавить ручные проверки)
- Save check results (сохранять результаты проверок)
- Add result type classification (добавить классификацию result type)
- Add tests for successful and failed checks (добавить тесты успешных и неуспешных проверок)

### Phase 7 — Alert Lifecycle (Жизненный цикл alerts)

- Add consecutive failure tracking (добавить отслеживание повторных ошибок)
- Add transaction-safe failure counter updates (добавить transaction-safe обновление failure counter)
- Add failure threshold logic (добавить failure threshold logic)
- Open alerts on repeated failures (открывать alerts при повторных сбоях)
- Resolve alerts after recovery (закрывать alerts после восстановления)

### Phase 8 — SMTP Notifications (SMTP-уведомления)

- Add real SMTP configuration (добавить конфигурацию real SMTP)
- Add notification service (добавить notification service)
- Store notification history (сохранять историю уведомлений)
- Add `.env.example` SMTP section (добавить SMTP-раздел в `.env.example`)

### Phase 9 — Background Worker (Фоновый worker)

- Add background worker thread (добавить фоновый поток)
- Select targets whose next check is due (выбирать targets, у которых наступило время проверки)
- Run scheduled checks (запускать проверки по расписанию)
- Log background operations (логировать фоновые операции)

### Phase 10 — Reports and Automation (Отчёты и автоматизация)

- Add summary report endpoint (добавить endpoint сводного отчёта)
- Add PowerShell scripts (добавить PowerShell-скрипты)
- Test scripted deployment (проверить запуск через скрипты)
- Update README instructions (обновить инструкции в README)

### Phase 11 — Final Testing and Documentation (Финальное тестирование и документация)

- Run final manual tests (запустить финальные ручные тесты)
- Prepare screenshots and logs (подготовить скриншоты и логи)
- Write technical report (написать технический отчёт)
- Prepare presentation (подготовить презентацию)
- Tag final version `v1.0` (поставить тег финальной версии `v1.0`)

---

## 23. Definition of Done (Критерии готовности)

The project is ready when:

Проект готов, когда:

- GitHub repository is clean and documented (GitHub-репозиторий чистый и документированный)
- The system starts with `docker compose up` (система запускается через `docker compose up`)
- `start.ps1` starts all services (скрипт `start.ps1` запускает все сервисы)
- Backend API is available (backend API доступен)
- MariaDB stores application data (MariaDB хранит данные приложения)
- Monitoring targets CRUD works (CRUD целей мониторинга работает)
- API key protection works for POST, PUT, DELETE (API key protection работает для POST, PUT, DELETE)
- Manual health checks work (ручные проверки работают)
- Background checks work (фоновые проверки работают)
- Failure threshold logic works (failure threshold logic работает)
- Failure counter updates are transaction-safe (обновления failure counter защищены transaction logic)
- Alerts are opened and resolved correctly (alerts корректно открываются и закрываются)
- SMTP notifications are sent through real SMTP (SMTP notifications отправляются через real SMTP)
- Notification history is stored (история уведомлений сохраняется)
- Logs contain INFO, WARNING, ERROR events (логи содержат события INFO, WARNING, ERROR)
- Summary report endpoint works (endpoint сводного отчёта работает)
- README explains how to run the project (README объясняет, как запустить проект)
- Technical report is completed (технический отчёт готов)
- Live demo scenario is tested (сценарий живой демонстрации проверен)

---

## 24. Known Limitations (Известные ограничения)

- `BaseHTTPRequestHandler` is used because the course focuses on low-level Python HTTP implementation (используется `BaseHTTPRequestHandler`, потому что курс требует низкоуровневую HTTP-реализацию на Python)
- `threading` is used for educational concurrency requirements (используется `threading` для учебного требования по параллелизму)
- Version 1 is not intended to replace production systems like Zabbix (первая версия не предназначена для замены production-систем вроде Zabbix)
- Basic API key is not a full authentication system (basic API key не является полноценной системой авторизации)
- Concurrent manual and background checks may update the same target state; this is mitigated by repository-level transaction logic (manual checks и background checks могут обновлять одно состояние target; это снижается через transaction logic в repository layer)

---

## 25. Future Improvements (Планы улучшений)

- Replace `BaseHTTPRequestHandler` with FastAPI (заменить `BaseHTTPRequestHandler` на FastAPI)
- Replace single background worker with scheduler + worker pool (заменить один background worker на scheduler + worker pool)
- Add email queue worker (добавить отдельный email queue worker)
- Add full authentication system (добавить полноценную авторизацию)
- Add role-based access control (добавить role-based access control)
- Add web dashboard (добавить веб-панель)
- Add security headers check module (добавить модуль проверки security headers)
- Add Docker healthchecks (добавить Docker healthchecks)
- Add GitHub Actions CI pipeline (добавить GitHub Actions CI pipeline)
- Add Prometheus/Grafana integration (добавить интеграцию Prometheus/Grafana)
