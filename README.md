# CorpWatch — Enterprise Monitoring and Alerting Platform

## Project Overview

CorpWatch is a Python-based enterprise monitoring and alerting platform.

The system allows users to add websites and API endpoints as monitoring targets. It checks their availability using HTTP requests, stores check results in MariaDB, detects failures, creates alerts, sends SMTP email notifications, writes logs, and runs as a Docker Compose multi-container system.

## Main Features

- Python HTTP API
- REST-like endpoints
- MariaDB database
- Monitoring targets CRUD
- Manual health checks
- Background health checks using threading
- Requests-based external service checks
- SMTP email notifications
- Application logging
- Dockerfile and Docker Compose deployment
- PowerShell automation scripts
- GitHub-based project workflow

## Project Scope

### In Scope

- Add, view, update and disable monitoring targets
- Run manual health checks
- Run scheduled background checks
- Store check results in MariaDB
- Detect failed targets
- Create alerts
- Send SMTP email notifications
- Store notification history
- Provide summary report
- Run the system through Docker Compose

### Out of Scope

- Full user authentication
- Complex frontend dashboard
- Kubernetes deployment
- Celery or APScheduler
- Prometheus/Grafana integration
- Real vulnerability scanning
- Advanced CI/CD pipeline

## Security Note

The first version will include basic API key protection for unsafe API operations such as POST, PUT and DELETE.

Real secrets must not be committed to GitHub. The repository will contain only `.env.example`, while the real `.env` file will be excluded using `.gitignore`.