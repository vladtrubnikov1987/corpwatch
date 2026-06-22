import json
import os
import re
from datetime import datetime
from typing import Any

import requests


DIAGNOSIS_BY_RESULT_TYPE = {
    "SUCCESS": "цель сейчас работает нормально",
    "SLOW_RESPONSE": "цель отвечает, но медленнее заданного порога",
    "WRONG_STATUS": "цель ответила неожиданным HTTP-кодом",
    "TIMEOUT": "цель не ответила за отведённый таймаут",
    "CONNECTION_ERROR": (
        "не удалось подключиться к цели: возможны проблемы с DNS, "
        "сетью или сам сервис недоступен"
    ),
}


HUMAN_EXPLANATION_PROMPT_TEMPLATE = """Ты — AI Assistant проекта CorpWatch.

Твоя задача:
написать человеческое объяснение результата проверки сайта.

Правила:
- Верни 2–4 живые фразы.
- Не пиши заголовок.
- Не пиши список.
- Не пиши technical details отдельными строками.
- Не переводи и не меняй название target.
- Не меняй HTTP-коды.
- Не меняй result_type.
- Не добавляй новые причины.
- Используй только данные ниже.
- Пиши так, будто объясняешь человеку, что произошло.

Target name: {target_name}
URL: {target_url}
Result type: {result_type}
Expected HTTP: {expected_status}
Actual HTTP: {actual_status}
Diagnosis: {diagnosis}
Alert status: {alert_status}
Severity: {alert_severity}
Notification status: {notification_status}
Response time ms: {response_time_ms}

Ответь по-русски."""


SUMMARY_REWRITE_PROMPT_TEMPLATE = """Ты — AI Assistant проекта CorpWatch.

Ниже находится технически правильный summary draft.
Твоя задача — переписать его человеческим языком.

Правила:
- Не меняй смысл.
- Не говори, что система стабильна, если в draft сказано, что есть проблема.
- Не придумывай новые причины.
- Не придумывай targets, контейнеры, nginx, Cloudflare или tunnel.
- Не меняй числа.
- Не используй слова "сегодня", "вчера", "завтра", если их нет в draft.
- Дату и время последней проверки переписывай ровно как указано в draft.
- Ответ должен быть 3–5 коротких фраз.
- Пиши как помощник, который объясняет состояние мониторинга человеку.

Summary draft:
{draft}

Ответь по-русски."""


FREE_CHAT_PROMPT_TEMPLATE = """Ты — локальный AI assistant.

Пользователь может задавать обычные вопросы на русском, английском или иврите.

Правила:
- Отвечай на языке пользователя, если можешь.
- Если пользователь просит "на русском" — отвечай по-русски.
- Не притягивай CorpWatch к ответу, если вопрос явно не про CorpWatch.
- Если вопрос про CorpWatch, Docker, мониторинг, target, alert или систему — отвечай в контексте проекта CorpWatch.
- Если вопрос общий, отвечай как обычный помощник.
- Если вопрос про дату или время, используй текущую дату и время из CONTEXT.
- Если не понимаешь вопрос, попроси переформулировать.

CONTEXT:
Current datetime: {current_datetime}

USER QUESTION:
{user_question}

Ответь естественно и кратко."""


class AIAssistantService:
    """
    CorpWatch AI Assistant.

    Modes:
    - manual_check: run check and explain target result.
    - system_summary: explain CorpWatch monitoring summary.
    - free_chat: general Ollama answer without CorpWatch summary.
    """

    def __init__(self) -> None:
        self.corpwatch_api_url = os.getenv(
            "CORPWATCH_API_URL",
            "http://app:8000",
        ).rstrip("/")

        self.ollama_api_url = os.getenv(
            "OLLAMA_API_URL",
            "http://ollama:11434",
        ).rstrip("/")

        self.ollama_model = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:3b",
        )

        self.api_key = os.getenv(
            "API_KEY",
            "change_me",
        )

    # ---------- CorpWatch API access ----------

    def _get_json(self, path: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.corpwatch_api_url}{path}",
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def _post_json(self, path: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.corpwatch_api_url}{path}",
            headers={
                "X-API-Key": self.api_key,
            },
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def get_summary_report(self) -> dict[str, Any]:
        return self._get_json("/api/reports/summary")

    def get_targets(self) -> dict[str, Any]:
        return self._get_json("/api/targets")

    def run_manual_check(self, target_id: int) -> dict[str, Any]:
        return self._post_json(f"/api/targets/{target_id}/check")

    # ---------- Helpers ----------

    def extract_target_id(self, text: str) -> int | None:
        text = text.strip()

        if text.isdigit():
            return int(text)

        patterns = [
            r"\btarget\s+(\d+)\b",
            r"\bid\s*=?\s*(\d+)\b",
            r"\bтаргет\s+(\d+)\b",
            r"\bцель\s+(\d+)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                return int(match.group(1))

        return None

    def normalize_api_data(self, data: dict[str, Any]) -> Any:
        return data.get("data", data.get("targets", data))

    def to_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def to_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def detect_mode(
        self,
        user_question: str,
        run_check: bool,
        mode: str | None,
    ) -> str:
        if mode in {"manual_check", "system_summary", "free_chat"}:
            return mode

        if run_check:
            return "manual_check"

        lowered = user_question.lower()

        system_phrases = [
            "что сейчас с системой",
            "что с системой",
            "состояние системы",
            "статус системы",
            "summary",
            "system status",
            "что происходит в системе",
            "как система",
            "как дела у системы",
        ]

        if any(phrase in lowered for phrase in system_phrases):
            return "system_summary"

        return "free_chat"

    def estimate_downtime(
        self,
        consecutive_failures: Any,
        interval_seconds: Any,
    ) -> str | None:
        try:
            failures = int(consecutive_failures)
            interval = int(interval_seconds)
        except (TypeError, ValueError):
            return None

        if failures <= 0 or interval <= 0:
            return None

        total_seconds = failures * interval

        if total_seconds < 60:
            return None

        minutes = round(total_seconds / 60)

        return (
            f"{failures} проверок подряд с ошибкой при интервале {interval}с — "
            f"примерно {minutes} мин"
        )

    def classify_result(
        self,
        result_type: str | None,
        status_code: int | None,
    ) -> str:
        if result_type == "WRONG_STATUS" and status_code == 530:
            return (
                "похоже на проблему Cloudflare Tunnel или origin-сервера: "
                "demo-сайт может быть недоступен за Cloudflare"
            )

        if result_type == "WRONG_STATUS" and status_code in (502, 503, 504):
            return "сервис недоступен за прокси или туннелем"

        return DIAGNOSIS_BY_RESULT_TYPE.get(
            result_type or "",
            "недостаточно данных для точной классификации",
        )

    # ---------- Fact building ----------

    def build_facts(
        self,
        summary_report: dict[str, Any],
        targets: dict[str, Any],
        manual_check: dict[str, Any] | None,
    ) -> dict[str, Any]:
        compact_facts: dict[str, Any] = {
            "summary": summary_report.get("data", summary_report),
            "targets": [],
            "manual_check": None,
            "downtime_estimate": None,
            "deterministic_diagnosis": "ручная проверка не запрашивалась",
        }

        targets_data = self.normalize_api_data(targets)
        targets_by_id: dict[int, dict[str, Any]] = {}

        if isinstance(targets_data, list):
            for target in targets_data:
                target_id = target.get("id")

                if target_id is None:
                    continue

                target_id_int = int(target_id)
                targets_by_id[target_id_int] = target

                compact_facts["targets"].append(
                    {
                        "id": target_id_int,
                        "name": target.get("name"),
                        "url": target.get("url"),
                        "is_active": target.get("is_active"),
                        "expected_status": target.get("expected_status"),
                        "check_interval_seconds": target.get("check_interval_seconds"),
                        "consecutive_failures": target.get("consecutive_failures"),
                    }
                )

        if manual_check:
            manual_data = manual_check.get("data", manual_check)

            result_type = manual_data.get("result_type")
            status_code = manual_data.get("status_code")
            target_id = manual_data.get("target_id")

            target_id_int = int(target_id) if target_id is not None else None
            focused_target = targets_by_id.get(target_id_int, {})

            compact_facts["manual_check"] = {
                "target_id": target_id_int,
                "target_name": manual_data.get("target_name") or focused_target.get("name"),
                "target_url": manual_data.get("target_url") or focused_target.get("url"),
                "is_active": focused_target.get("is_active"),
                "expected_status": manual_data.get("expected_status")
                or focused_target.get("expected_status"),
                "actual_status": status_code,
                "result_type": result_type,
                "response_time_ms": manual_data.get("response_time_ms"),
                "alert_status": manual_data.get("alert_status"),
                "alert_severity": manual_data.get("alert_severity"),
                "notification_status": manual_data.get("notification_status"),
                "error_message": manual_data.get("error_message"),
            }

            compact_facts["deterministic_diagnosis"] = self.classify_result(
                result_type=result_type,
                status_code=status_code,
            )

            compact_facts["downtime_estimate"] = self.estimate_downtime(
                focused_target.get("consecutive_failures"),
                focused_target.get("check_interval_seconds"),
            )

        return compact_facts

    # ---------- Summary ----------

    def build_summary_draft(self, facts: dict[str, Any]) -> str:
        summary = facts.get("summary") or {}

        total_targets = self.to_int(summary.get("total_targets"))
        active_targets = self.to_int(summary.get("active_targets"))
        total_checks = self.to_int(summary.get("total_checks"))
        success_checks = self.to_int(summary.get("success_checks"))
        failed_checks = self.to_int(summary.get("failed_checks"))
        open_alerts = self.to_int(summary.get("open_alerts"))
        resolved_alerts = self.to_int(summary.get("resolved_alerts"))
        total_notifications = self.to_int(summary.get("total_notifications"))
        sent_notifications = self.to_int(summary.get("sent_notifications"))
        failed_notifications = self.to_int(summary.get("failed_notifications"))
        average_response_time_ms = self.to_float(summary.get("average_response_time_ms"))
        worst_response_time_ms = self.to_int(summary.get("worst_response_time_ms"))
        last_check_time = summary.get("last_check_time")

        if open_alerts > 0:
            system_status = "ПРОБЛЕМА"
            main_line = (
                f"CorpWatch сейчас НЕ считает систему полностью стабильной: "
                f"есть {open_alerts} открытый alert."
            )
        elif failed_checks > 0:
            system_status = "ВНИМАНИЕ"
            main_line = (
                "Сейчас открытых alert нет, но в истории мониторинга "
                f"есть {failed_checks} failed checks."
            )
        else:
            system_status = "OK"
            main_line = "CorpWatch сейчас не видит открытых проблем."

        lines = [
            f"System status: {system_status}",
            main_line,
            f"Всего targets: {total_targets}. Активных targets: {active_targets}.",
            f"Всего проверок: {total_checks}. Успешных: {success_checks}. Ошибочных: {failed_checks}.",
            f"Open alerts: {open_alerts}. Resolved alerts: {resolved_alerts}.",
            f"Average response time: {average_response_time_ms} ms.",
            f"Worst response time: {worst_response_time_ms} ms.",
            f"Notifications: всего {total_notifications}, отправлено {sent_notifications}, ошибок отправки {failed_notifications}.",
        ]

        if last_check_time:
            lines.append(f"Последняя проверка: {last_check_time}.")

        if open_alerts > 0:
            lines.append(
                "Вывод: систему нельзя называть стабильной, пока есть открытый alert."
            )

        return "\n".join(lines)

    def build_summary_rewrite_prompt(self, draft: str) -> str:
        return SUMMARY_REWRITE_PROMPT_TEMPLATE.format(draft=draft)

    # ---------- Manual check ----------

    def build_human_explanation_prompt(
        self,
        facts: dict[str, Any],
    ) -> str:
        manual_check = facts.get("manual_check") or {}

        return HUMAN_EXPLANATION_PROMPT_TEMPLATE.format(
            target_name=manual_check.get("target_name") or "Unknown target",
            target_url=manual_check.get("target_url") or "unknown URL",
            result_type=manual_check.get("result_type"),
            expected_status=manual_check.get("expected_status"),
            actual_status=manual_check.get("actual_status"),
            diagnosis=facts.get("deterministic_diagnosis"),
            alert_status=manual_check.get("alert_status"),
            alert_severity=manual_check.get("alert_severity"),
            notification_status=manual_check.get("notification_status"),
            response_time_ms=manual_check.get("response_time_ms"),
        )

    def build_default_human_explanation(self, facts: dict[str, Any]) -> str:
        manual_check = facts.get("manual_check") or {}

        target_url = manual_check.get("target_url") or "unknown URL"
        expected_status = manual_check.get("expected_status")
        actual_status = manual_check.get("actual_status")
        result_type = manual_check.get("result_type")
        diagnosis = facts.get("deterministic_diagnosis")

        if result_type == "SUCCESS":
            return (
                f"CorpWatch проверил сайт {target_url}. "
                f"Сайт отвечает корректно: ожидался HTTP {expected_status} "
                f"и был получен HTTP {actual_status}. "
                f"Проблем с доступностью сейчас не обнаружено."
            )

        return (
            f"CorpWatch проверил сайт {target_url} и обнаружил проблему. "
            f"Система ожидала HTTP {expected_status}, но получила HTTP {actual_status}. "
            f"Диагноз: {diagnosis}."
        )

    def build_manual_check_answer(
        self,
        facts: dict[str, Any],
        human_explanation: str | None = None,
    ) -> str:
        manual_check = facts.get("manual_check")

        if not manual_check:
            return "Manual check не запускался."

        target_id = manual_check.get("target_id")
        target_name = manual_check.get("target_name") or "Unknown target"
        target_url = manual_check.get("target_url") or "unknown URL"
        expected_status = manual_check.get("expected_status")
        actual_status = manual_check.get("actual_status")
        result_type = manual_check.get("result_type")
        response_time_ms = manual_check.get("response_time_ms")
        alert_status = manual_check.get("alert_status")
        alert_severity = manual_check.get("alert_severity")
        notification_status = manual_check.get("notification_status")
        error_message = manual_check.get("error_message")
        downtime_estimate = facts.get("downtime_estimate")

        status = "OK" if result_type == "SUCCESS" else "ПРОБЛЕМА"

        if not human_explanation:
            human_explanation = self.build_default_human_explanation(facts)

        lines = [
            f"Target {target_id} — {target_name}",
            "",
            f"Статус: {status}",
            "",
            human_explanation.strip(),
            "",
            "Технические детали:",
            f"URL: {target_url}",
        ]

        if expected_status is not None:
            lines.append(f"Expected HTTP: {expected_status}")

        if actual_status is not None:
            lines.append(f"Actual HTTP: {actual_status}")

        if response_time_ms is not None:
            lines.append(f"Response time: {response_time_ms} ms")

        if downtime_estimate:
            lines.append(f"Downtime estimate: {downtime_estimate}")

        if error_message:
            lines.append(f"Error: {error_message}")

        lines.append(f"Result: {result_type}")

        if alert_status:
            lines.append(f"Alert: {alert_status}")

        if alert_severity and alert_severity != "UNKNOWN":
            lines.append(f"Severity: {alert_severity}")

        if notification_status:
            lines.append(f"Notification: {notification_status}")

        return "\n".join(lines)

    # ---------- Free chat ----------

    def build_free_chat_prompt(self, user_question: str) -> str:
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return FREE_CHAT_PROMPT_TEMPLATE.format(
            current_datetime=current_datetime,
            user_question=user_question,
        )

    # ---------- LLM ----------

    def ask_ollama(
        self,
        prompt: str,
        temperature: float = 0.2,
        num_predict: int = 220,
    ) -> str:
        response = requests.post(
            f"{self.ollama_api_url}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if not answer:
            raise requests.RequestException("Ollama returned empty response")

        return answer

    # ---------- Main entry point ----------

    def explain(
        self,
        user_question: str,
        run_check: bool = False,
        mode: str | None = None,
    ) -> dict[str, Any]:
        selected_mode = self.detect_mode(
            user_question=user_question,
            run_check=run_check,
            mode=mode,
        )

        target_id = self.extract_target_id(user_question)

        # Free chat does not need CorpWatch API.
        if selected_mode == "free_chat":
            prompt = self.build_free_chat_prompt(user_question)

            try:
                answer = self.ask_ollama(
                    prompt=prompt,
                    temperature=0.3,
                    num_predict=220,
                )
            except requests.RequestException:
                return {
                    "success": False,
                    "error": "ollama_unavailable",
                    "message": (
                        "AI-ассистент временно недоступен: Ollama не отвечает."
                    ),
                }

            return {
                "success": True,
                "question": user_question,
                "mode": selected_mode,
                "answer": answer,
            }

        try:
            summary_report = self.get_summary_report()
            targets = self.get_targets()
        except requests.RequestException:
            return {
                "success": False,
                "error": "corpwatch_api_unavailable",
                "message": (
                    "Не удалось получить данные из CorpWatch API. "
                    "Проверь, что сервис app доступен."
                ),
            }

        manual_check = None

        if selected_mode == "manual_check":
            if target_id is None:
                return {
                    "success": False,
                    "error": "target_id_required",
                    "message": "Напиши target id. Например: проверь target 4",
                }

            try:
                manual_check = self.run_manual_check(target_id)
            except requests.RequestException:
                return {
                    "success": False,
                    "error": "manual_check_failed",
                    "message": f"Не удалось запустить ручную проверку target {target_id}.",
                }

        facts = self.build_facts(
            summary_report=summary_report,
            targets=targets,
            manual_check=manual_check,
        )

        if selected_mode == "manual_check":
            human_explanation = None

            try:
                prompt = self.build_human_explanation_prompt(facts)

                human_explanation = self.ask_ollama(
                    prompt=prompt,
                    temperature=0.1,
                    num_predict=180,
                )
            except requests.RequestException:
                human_explanation = None

            answer = self.build_manual_check_answer(
                facts=facts,
                human_explanation=human_explanation,
            )

            return {
                "success": True,
                "question": user_question,
                "mode": selected_mode,
                "target_id": target_id,
                "manual_check_was_run": True,
                "facts": facts,
                "human_explanation": human_explanation,
                "answer": answer,
            }

        # System summary mode.
        summary_draft = self.build_summary_draft(facts)
        prompt = self.build_summary_rewrite_prompt(summary_draft)

        try:
            answer = self.ask_ollama(
                prompt=prompt,
                temperature=0.1,
                num_predict=220,
            )
        except requests.RequestException:
            answer = summary_draft

        return {
            "success": True,
            "question": user_question,
            "mode": selected_mode,
            "target_id": target_id,
            "manual_check_was_run": False,
            "facts": facts,
            "summary_draft": summary_draft,
            "answer": answer,
        }


ai_assistant_service = AIAssistantService()