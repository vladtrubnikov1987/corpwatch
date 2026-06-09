# [[CorpWatch]] Roadmap 
## Enterprise Monitoring and Alerting Platform  
### Дорожная карта проекта 
---

## Project Goal (Цель проекта)

**CorpWatch** is a enterprise monitoring and alerting platform.(это платформа мониторинга и оповещений для предприятий.)

The system monitors websites, APIs, and internal services, stores health check results in a database, sends email alerts, writes logs, and runs inside Docker containers.

(Система отслеживает сайты, API и внутренние сервисы, сохраняет результаты проверок в базу данных, отправляет email-уведомления, ведёт логи и запускается в Docker-контейнерах.)

---

## 1. Project Scope (Границы проекта)

### In Scope (Входит в проект)

- Python HTTP API (HTTP API на Python)
- REST-like endpoints (REST-подобные эндпоинты)
- MariaDB database (база данных MariaDB)
- Monitoring targets management (управление целями мониторинга)
- Manual health checks (ручные проверки доступности)
- Scheduled background checks (автоматические фоновые проверки)
- Alerts (оповещения о проблемах)
- SMTP notifications (email-уведомления через SMTP)
- Application logging (логирование приложения)
- Dockerfile (файл сборки Docker-образа)
- Docker Compose deployment (развёртывание через Docker Compose)
- PowerShell automation scripts (PowerShell-скрипты автоматизации)
- GitHub repository (репозиторий на GitHub)
- Technical report (технический отчёт)
- Live demonstration (живая демонстрация)

### Out of Scope (Не входит в проект)

- Full user authentication (полноценная авторизация пользователей)
- Complex frontend dashboard (сложная веб-панель)
- Real production SMTP account (реальный production SMTP-аккаунт)
- Kubernetes deployment (развёртывание в Kubernetes)
- Real vulnerability exploitation (реальная эксплуатация уязвимостей)
- Advanced CI/CD pipeline (сложный CI/CD pipeline)

---

## 2. Functional Requirements (Функциональные требования)

- **FR-1:** Add monitoring target (добавить цель мониторинга)
- **FR-2:** View all monitoring targets (просмотреть все цели мониторинга)
- **FR-3:** View one monitoring target by ID (просмотреть одну цель по ID)
- **FR-4:** Update monitoring target settings (обновить настройки цели)
- **FR-5:** Disable or delete monitoring target (отключить или удалить цель)
- **FR-6:** Run manual health check (запустить ручную проверку)
- **FR-7:** Run scheduled background checks (запускать проверки в фоне)
- **FR-8:** Store check results in database (сохранять результаты проверок в БД)
- **FR-9:** Detect failures and downtime (обнаруживать сбои и недоступность)
- **FR-10:** Create alerts (создавать оповещения)
- **FR-11:** Send SMTP email notifications (отправлять email-уведомления через SMTP)
- **FR-12:** Store notification history (сохранять историю уведомлений)
- **FR-13:** Provide monitoring summary report (предоставлять сводный отчёт)

---

## 3. Non-Functional Requirements (Нефункциональные требования)

- **NFR-1:** The system must run through Docker Compose (система должна запускаться через Docker Compose)
- **NFR-2:** Database data must persist after container restart (данные БД должны сохраняться после перезапуска контейнеров)
- **NFR-3:** The backend must return JSON responses (backend должен возвращать JSON-ответы)
- **NFR-4:** The application must handle errors without crashing (приложение должно обрабатывать ошибки без падения)
- **NFR-5:** Logs must include INFO, WARNING, and ERROR levels (логи должны включать уровни INFO, WARNING и ERROR)
- **NFR-6:** Deployment must be reproducible using scripts (развёртывание должно повторяться через скрипты)
- **NFR-7:** The project must be stored in GitHub (проект должен храниться в GitHub)

---

## 4. Technology Stack (Технологический стек)

- Python (язык программирования)
- `http.server` / `BaseHTTPRequestHandler` (HTTP-сервер на Python)
- `requests` (библиотека для HTTP-запросов)
- `smtplib` (библиотека для SMTP-отправки email)
- `logging` (стандартное логирование Python)
- `threading` (параллельное выполнение через потоки)
- MariaDB (реляционная база данных)
- Docker (контейнеризация)
- Docker Compose (управление несколькими контейнерами)
- MailHog (тестовый SMTP-сервис)
- phpMyAdmin (веб-интерфейс для MariaDB)
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
└── README.md                 # Project documentation (документация проекта)
```

---

## 6. Database Design (Проектирование базы данных)

### Tables (Таблицы)

1. `users` — system users (пользователи системы)
2. `monitoring_targets` — services to monitor (сервисы для мониторинга)
3. `check_results` — health check history (история проверок)
4. `alerts` — failure alerts (оповещения о сбоях)
5. `notifications` — email notification history (история email-уведомлений)

### Relationships (Связи)

```text
users 1 → many monitoring_targets

monitoring_targets 1 → many check_results

monitoring_targets 1 → many alerts

alerts 1 → many notifications
```

### Main Target Fields (Основные поля цели мониторинга)

- `id`
- `user_id`
- `name`
- `url`
- `expected_status`
- `timeout_seconds`
- `max_response_time_ms`
- `check_interval_seconds`
- `is_active`
- `created_at`
- `updated_at`

---

## 7. Docker Infrastructure (Docker-инфраструктура)

### Services (Сервисы)

- `app` — Python backend service (Python backend-сервис)
- `db` — MariaDB database service (сервис базы данных MariaDB)
- `phpmyadmin` — database web UI (веб-интерфейс для БД)
- `mailhog` — test SMTP service (тестовый SMTP-сервис)

### Required Files (Обязательные файлы)

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### Docker Goals (Цели Docker-этапа)

- Build Python application image (собрать Docker-образ Python-приложения)
- Start all services with one command (запустить все сервисы одной командой)
- Connect containers by service names (соединять контейнеры по именам сервисов)
- Store MariaDB data in Docker volume (хранить данные MariaDB в Docker volume)
- Expose backend API port (открыть порт backend API)

---

## 8. Backend Skeleton (Каркас backend-приложения)

### Main Components (Основные компоненты)

- `main.py` — starts the HTTP server and background worker (запускает HTTP-сервер и фоновый поток)
- `config/settings.py` — application settings (настройки приложения)
- `utils/logger.py` — logging configuration (настройка логирования)
- `repositories/database.py` — database connection manager (менеджер подключения к БД)

### Goal (Цель)

The application starts, connects to MariaDB, writes logs, and returns a health response.

Приложение запускается, подключается к MariaDB, пишет логи и возвращает ответ проверки здоровья.

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

### Health Checks API (API проверок доступности)

```text
POST /api/targets/{id}/check
GET  /api/targets/{id}/checks
GET  /api/checks
```

### Alerts API (API оповещений)

```text
GET /api/alerts
GET /api/alerts/{id}
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

## 10. Monitoring Service (Сервис мониторинга)

### Responsibilities (Ответственности)

- Load active monitoring targets from database (загружать активные цели из БД)
- Send HTTP request using `requests` (отправлять HTTP-запрос через `requests`)
- Measure response time (измерять время ответа)
- Compare actual status with expected status (сравнивать фактический и ожидаемый статус)
- Detect timeout or connection error (обнаруживать timeout или ошибку подключения)
- Save result to `check_results` (сохранять результат в `check_results`)

### Result Types (Типы результата)

- `SUCCESS` — target is healthy (цель работает нормально)
- `SLOW_RESPONSE` — target is too slow (цель отвечает слишком медленно)
- `WRONG_STATUS` — unexpected status code (неожиданный статус-код)
- `TIMEOUT` — request timeout (истекло время ожидания)
- `CONNECTION_ERROR` — connection failed (ошибка подключения)

---

## 11. Alert Service (Сервис оповещений)

### Responsibilities (Ответственности)

- Analyze failed check results (анализировать неудачные проверки)
- Create alert records (создавать записи об оповещениях)
- Assign severity level (назначать уровень серьёзности)
- Pass alert to notification service (передавать alert в сервис уведомлений)

### Severity Levels (Уровни серьёзности)

- `LOW` — slow response (медленный ответ)
- `MEDIUM` — wrong status code (неверный статус-код)
- `HIGH` — timeout (превышение времени ожидания)
- `CRITICAL` — connection error or repeated failure (ошибка подключения или повторный сбой)

---

## 12. Notification Service (Сервис уведомлений)

### Responsibilities (Ответственности)

- Send email through SMTP (отправлять email через SMTP)
- Use MailHog for demonstration (использовать MailHog для демонстрации)
- Store notification status in database (сохранять статус уведомления в БД)
- Log successful and failed email sending (логировать успешную и неудачную отправку)

### Email Types (Типы email)

- Failure alert (оповещение о сбое)
- Slow response warning (предупреждение о медленном ответе)
- Monitoring report (отчёт мониторинга)

---

## 13. Background Worker (Фоновый поток)

### Technology (Технология)

- `threading`

### Responsibilities (Ответственности)

The background worker runs in a separate thread.

Фоновый обработчик работает в отдельном потоке.

It periodically:

Он периодически:

- loads active targets (загружает активные цели)
- checks each target (проверяет каждую цель)
- stores check results (сохраняет результаты)
- creates alerts if needed (создаёт оповещения при необходимости)
- sends email notifications (отправляет email-уведомления)

---

## 14. Reporting (Отчётность)

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
- Active alerts (активные оповещения)
- Last check time (время последней проверки)

---

## 15. Logging Strategy (Стратегия логирования)

### Log Levels (Уровни логирования)

- `INFO` — normal system operations (обычные операции системы)
- `WARNING` — slow response or suspicious state (медленный ответ или подозрительное состояние)
- `ERROR` — failure, exception, unavailable service (сбой, исключение, недоступный сервис)

### Logged Events (Логируемые события)

- Application started (приложение запущено)
- Database connected (подключение к БД выполнено)
- Monitoring target created (цель мониторинга создана)
- Health check completed (проверка выполнена)
- Alert created (alert создан)
- Email sent (email отправлен)
- Email sending failed (отправка email не удалась)
- Database error (ошибка БД)
- HTTP request error (ошибка HTTP-запроса)

---

## 16. Error Handling Strategy (Стратегия обработки ошибок)

The system must handle:

Система должна обрабатывать:

- Invalid JSON body (невалидное JSON-тело запроса)
- Missing required fields (отсутствующие обязательные поля)
- Target not found (цель не найдена)
- Database connection error (ошибка подключения к БД)
- Request timeout (timeout HTTP-запроса)
- Connection error (ошибка подключения)
- SMTP sending error (ошибка отправки SMTP)
- Unknown internal error (неизвестная внутренняя ошибка)

---

## 17. PowerShell Automation Scripts (PowerShell-скрипты автоматизации)

### Required Scripts (Обязательные скрипты)

```text
build.ps1      # Build Docker images (собрать Docker-образы)
start.ps1      # Start the system (запустить систему)
stop.ps1       # Stop the system (остановить систему)
redeploy.ps1   # Rebuild and restart the system (пересобрать и перезапустить систему)
```

### Optional Scripts (Дополнительные скрипты)

```text
logs.ps1        # View logs (посмотреть логи)
status.ps1      # Show containers status (показать статус контейнеров)
reset-db.ps1    # Reset database volume (сбросить volume базы данных)
healthcheck.ps1 # Check API health (проверить здоровье API)
```

---

## 18. GitHub Implementation (Реализация проекта на GitHub)

### Repository Setup (Настройка репозитория)

- Create GitHub repository `corpwatch` (создать репозиторий `corpwatch`)
- Add `.gitignore` (добавить `.gitignore`)
- Add `README.md` (добавить `README.md`)
- Add `.env.example` but do not commit real `.env` (добавить `.env.example`, но не добавлять настоящий `.env`)
- Add project roadmap file (добавить файл дорожной карты проекта)
- Add initial project structure (добавить начальную структуру проекта)

### Branching Strategy (Стратегия веток)

Recommended simple strategy:

Рекомендуемая простая стратегия:

```text
main        # stable version (стабильная версия)
dev         # development version (версия для разработки)
feature/*   # feature branches (ветки для отдельных функций)
```

### Suggested Feature Branches (Рекомендуемые feature-ветки)

```text
feature/project-structure
feature/database-schema
feature/docker-compose
feature/backend-skeleton
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

Use clear English commit messages.

Использовать понятные сообщения коммитов на английском.

Examples:

Примеры:

```text
init: create project structure
db: add initial MariaDB schema
docker: add docker compose configuration
api: add health endpoint
api: add monitoring targets CRUD
service: add manual health check logic
service: add alert creation logic
smtp: add MailHog notification service
worker: add background monitoring thread
docs: update README with deployment steps
```

### GitHub README Sections (Разделы README на GitHub)

- Project overview (обзор проекта)
- Features (функции)
- Architecture (архитектура)
- Technology stack (технологический стек)
- Project structure (структура проекта)
- Database schema (схема базы данных)
- API endpoints (API-эндпоинты)
- Docker deployment (развёртывание через Docker)
- PowerShell scripts (PowerShell-скрипты)
- Testing (тестирование)
- Demo scenario (сценарий демонстрации)

---

## 19. Testing (Тестирование)

### Test Types (Типы тестов)

- Unit tests (модульные тесты)
- Integration tests (интеграционные тесты)
- Manual API tests (ручные API-тесты)
- Docker deployment tests (тесты Docker-развёртывания)

### Testing Evidence (Доказательства тестирования)

- API request screenshots (скриншоты API-запросов)
- phpMyAdmin screenshots (скриншоты phpMyAdmin)
- MailHog email screenshots (скриншоты email в MailHog)
- Docker containers status screenshot (скриншот статуса контейнеров)
- Application logs screenshot (скриншот логов приложения)
- Test command output (вывод команды тестирования)

---

## 20. Demo Scenario (Сценарий демонстрации)

### Live Demo Steps (Шаги живой демонстрации)

1. Run `start.ps1` (запустить `start.ps1`)
2. Show running containers (показать запущенные контейнеры)
3. Open `GET /api/health` (открыть `GET /api/health`)
4. Add working monitoring target (добавить рабочую цель мониторинга)
5. Add broken monitoring target (добавить нерабочую цель мониторинга)
6. Run manual health check (запустить ручную проверку)
7. Show check history (показать историю проверок)
8. Show alert records (показать записи alerts)
9. Show email in MailHog (показать email в MailHog)
10. Show database tables in phpMyAdmin (показать таблицы в phpMyAdmin)
11. Show application logs (показать логи приложения)
12. Show summary report (показать сводный отчёт)
13. Run `stop.ps1` (запустить `stop.ps1`)

---

## 21. Documentation (Документация)

### Technical Report Sections (Разделы технического отчёта)

1. Cover Page (титульная страница)
2. Project Overview (обзор проекта)
3. Functional Requirements (функциональные требования)
4. System Architecture (архитектура системы)
5. Database Design (проектирование базы данных)
6. OOP Design (ООП-дизайн)
7. Concurrency Design (проектирование параллелизма)
8. Logging Strategy (стратегия логирования)
9. SMTP Integration (SMTP-интеграция)
10. External API Integration (интеграция внешних API)
11. Docker Architecture (Docker-архитектура)
12. GitHub Workflow (рабочий процесс в GitHub)
13. Testing Strategy (стратегия тестирования)
14. Challenges and Solutions (проблемы и решения)
15. Future Improvements (планы улучшений)
16. Conclusion (заключение)

---

## 22. Presentation Plan (План презентации)

### Presentation Structure (Структура презентации)

1. Problem Introduction (описание проблемы)
2. System Overview (обзор системы)
3. Technology Stack (технологический стек)
4. System Architecture (архитектура системы)
5. Database Design (проектирование базы данных)
6. Backend Functionality (функциональность backend)
7. Concurrency Demonstration (демонстрация параллелизма)
8. SMTP Alert Demonstration (демонстрация SMTP-уведомления)
9. Docker Deployment (Docker-развёртывание)
10. PowerShell Automation (PowerShell-автоматизация)
11. GitHub Repository Overview (обзор GitHub-репозитория)
12. Live Demo (живая демонстрация)
13. Lessons Learned (извлечённые уроки)

---

## 23. Development Order (Порядок разработки)

### Phase 1 — Planning (Планирование)

- Define project scope (определить границы проекта)
- Define functional requirements (определить функциональные требования)
- Define non-functional requirements (определить нефункциональные требования)
- Prepare GitHub repository (подготовить GitHub-репозиторий)

### Phase 2 — Design (Проектирование)

- Design project structure (спроектировать структуру проекта)
- Design database schema (спроектировать схему БД)
- Design API endpoints (спроектировать API-эндпоинты)
- Design service classes (спроектировать сервисные классы)

### Phase 3 — Infrastructure (Инфраструктура)

- Create Dockerfile (создать Dockerfile)
- Create docker-compose.yml (создать docker-compose.yml)
- Add MariaDB service (добавить сервис MariaDB)
- Add phpMyAdmin service (добавить сервис phpMyAdmin)
- Add MailHog service (добавить сервис MailHog)

### Phase 4 — Backend Core (Ядро backend)

- Create backend skeleton (создать каркас backend)
- Add database connection (добавить подключение к БД)
- Add logging configuration (добавить настройку логирования)
- Add health endpoint (добавить health-эндпоинт)

### Phase 5 — Monitoring Features (Функции мониторинга)

- Add monitoring targets CRUD (добавить CRUD для целей мониторинга)
- Add manual health checks (добавить ручные проверки)
- Add check history (добавить историю проверок)
- Add summary report (добавить сводный отчёт)

### Phase 6 — Alerts and Notifications (Оповещения и уведомления)

- Add alert creation logic (добавить логику создания alerts)
- Add severity classification (добавить классификацию серьёзности)
- Add SMTP notification service (добавить SMTP-сервис уведомлений)
- Store notification history (сохранять историю уведомлений)

### Phase 7 — Background Processing (Фоновая обработка)

- Add background worker (добавить фоновый поток)
- Run scheduled checks (запускать проверки по расписанию)
- Log background operations (логировать фоновые операции)

### Phase 8 — Automation (Автоматизация)

- Add PowerShell scripts (добавить PowerShell-скрипты)
- Test scripted deployment (проверить развёртывание через скрипты)
- Update README instructions (обновить инструкции в README)

### Phase 9 — Testing and Demo (Тестирование и демонстрация)

- Write unit tests (написать модульные тесты)
- Run integration tests (запустить интеграционные тесты)
- Prepare manual test checklist (подготовить список ручных проверок)
- Prepare demo screenshots (подготовить скриншоты для демонстрации)

### Phase 10 — Final Documentation (Финальная документация)

- Write technical report (написать технический отчёт)
- Prepare presentation (подготовить презентацию)
- Final GitHub cleanup (финально привести GitHub-репозиторий в порядок)
- Tag final version `v1.0` (поставить тег финальной версии `v1.0`)

---

## 24. Definition of Done (Критерии готовности)

The project is ready when:

Проект готов, когда:

- The system starts with `docker compose up` (система запускается через `docker compose up`)
- `start.ps1` starts all services (скрипт `start.ps1` запускает все сервисы)
- Backend API is available (backend API доступен)
- MariaDB stores application data (MariaDB хранит данные приложения)
- Monitoring targets CRUD works (CRUD целей мониторинга работает)
- Manual health checks work (ручные проверки работают)
- Background checks work (фоновые проверки работают)
- Alerts are created on failures (alerts создаются при сбоях)
- SMTP notifications appear in MailHog (SMTP-уведомления появляются в MailHog)
- Logs contain INFO, WARNING, ERROR events (логи содержат события INFO, WARNING, ERROR)
- Summary report endpoint works (эндпоинт сводного отчёта работает)
- GitHub repository is clean and documented (GitHub-репозиторий чистый и документированный)
- README explains how to run the project (README объясняет, как запустить проект)
- Technical report is completed (технический отчёт готов)
- Live demo scenario is tested (сценарий живой демонстрации проверен)

---

## 25. Future Improvements (Планы улучшений)

- Add web dashboard (добавить веб-панель)
- Add user authentication (добавить авторизацию пользователей)
- Add role-based access control (добавить ролевой доступ)
- Add security headers check module (добавить модуль проверки security headers)
- Add daily email reports (добавить ежедневные email-отчёты)
- Add Docker healthchecks (добавить Docker healthchecks)
- Add GitHub Actions CI pipeline (добавить GitHub Actions CI pipeline)
- Add Prometheus/Grafana integration (добавить интеграцию Prometheus/Grafana)
