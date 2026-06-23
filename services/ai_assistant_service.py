import os
import re
from datetime import datetime
from typing import Any

import requests

from utils.logger import logger


FREE_CHAT_PROMPT_TEMPLATE = """Ты — локальный AI assistant проекта CorpWatch по имени Jarvis.

Ты работаешь в Telegram как обычный полезный AI assistant, но также понимаешь контекст проекта CorpWatch.

Твои возможности:
- отвечать на обычные вопросы;
- объяснять Python, Docker, API, backend, databases, monitoring, Telegram bot, Ollama;
- анализировать архитектуру проекта;
- помогать с README, ROADMAP, Demo.md, Markdown и кодом;
- отвечать подробно, если пользователь просит "полностью", "подробно", "разбери всё", "проанализируй полностью";
- продолжать предыдущую мысль, если пользователь пишет короткий follow-up: "да", "полностью", "продолжай", "сделай", "ок".

Главные правила:
- Если пользователь пишет по-русски — отвечай ТОЛЬКО по-русски.
- Не используй китайский язык.
- Не смешивай языки без необходимости.
- Не притягивай CorpWatch к ответу, если вопрос явно не про CorpWatch.
- Если вопрос про CorpWatch, Docker, мониторинг, target, alert, backend, Telegram bot или AI layer — отвечай в контексте проекта CorpWatch.
- Если пользователь просит анализ файла, но содержимое файла не передано в сообщении или контексте, честно скажи, что тебе нужно содержимое файла или команда/механизм доступа к файлу.
- Не проси уточнение, если смысл можно восстановить из CONTEXT.
- Если запрос широкий, дай структурированный ответ: архитектура, сильные стороны, слабые места, улучшения, вывод.
- Для monitoring-статусов не выдумывай факты: status, result_type, alert, notification должны приходить из CorpWatch API.
- В free_chat можно отвечать свободно и развёрнуто.

CONTEXT:
Current datetime: {current_datetime}

Conversation context:
{conversation_context}

USER QUESTION:
{user_question}

Ответь естественно, полезно и по делу.
"""


HUMAN_EXPLANATION_PROMPT_TEMPLATE = """Ты — локальный AI assistant проекта CorpWatch.

Тебе переданы проверенные факты мониторинга от Python backend.
Ты НЕ принимаешь monitoring decisions.
Ты только объясняешь пользователю уже готовые факты простым языком.

Правила:
- Отвечай по-русски.
- Не меняй technical facts.
- Не выдумывай HTTP status, result_type, alert_status, notification_status.
- Не говори, что сайт работает, если result_type не SUCCESS.
- Не говори, что есть проблема, если result_type SUCCESS и alert_status NO_ALERT.
- Ответ должен быть понятным человеку.

FACTS:
{facts}

Сделай короткое человеческое объяснение результата.
"""


SUMMARY_REWRITE_PROMPT_TEMPLATE = """Ты — локальный AI assistant проекта CorpWatch.

Тебе передан черновик summary, созданный Python backend на основе verified facts.
Ты НЕ принимаешь monitoring decisions.
Ты только переписываешь черновик более понятным языком.

Правила:
- Отвечай по-русски.
- Не меняй смысл.
- Не выдумывай новые targets, alerts или ошибки.
- Если в черновике сказано, что есть open alerts, не называй систему полностью стабильной.
- Если open alerts = 0, можно сказать, что критичных открытых проблем сейчас нет.

SUMMARY DRAFT:
{summary_draft}

Перепиши summary естественным языком.
"""


class AIAssistantService:
    """
    CorpWatch AI Assistant.

    Modes:
    - manual_check: run check and explain target result.
    - system_summary: explain CorpWatch monitoring summary.
    - free_chat: normal LLM answer without forced monitoring context.
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

    def detect_mode(
        self,
        user_question: str,
        run_check: bool = False,
        mode: str | None = None,
    ) -> str:
        if mode in ("manual_check", "system_summary", "free_chat"):
            return mode

        text = user_question.strip().lower()

        if run_check:
            return "manual_check"

        summary_words = [
            "что сейчас с системой",
            "что с системой",
            "статус системы",
            "summary",
            "system summary",
            "сводка",
            "общий статус",
        ]

        if any(word in text for word in summary_words):
            return "system_summary"

        check_words = [
            "проверь",
            "проверить",
            "check target",
            "run check",
            "manual check",
        ]

        if any(word in text for word in check_words) and self.extract_target_id(text):
            return "manual_check"

        return "free_chat"

    def normalize_api_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: self.normalize_api_data(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self.normalize_api_data(item) for item in data]

        return data

    def pick_first_existing(self, data: dict[str, Any], keys: list[str], default=None):
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return default

    # ---------- Ollama ----------

    def ask_ollama(
        self,
        prompt: str,
        temperature: float = 0.2,
        num_predict: int = 400,
    ) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
        }

        response = requests.post(
            f"{self.ollama_api_url}/api/generate",
            json=payload,
            timeout=180,
        )

        response.raise_for_status()
        data = response.json()

        answer = data.get("response", "")

        if not answer:
            raise requests.RequestException("Ollama returned empty response")

        return answer.strip()

    # ---------- Prompt builders ----------

    def build_free_chat_prompt(
        self,
        user_question: str,
        conversation_context: str = "",
    ) -> str:
        return FREE_CHAT_PROMPT_TEMPLATE.format(
            current_datetime=datetime.now().isoformat(timespec="seconds"),
            conversation_context=conversation_context or "No previous context.",
            user_question=user_question,
        )

    def build_human_explanation_prompt(self, facts: dict[str, Any]) -> str:
        return HUMAN_EXPLANATION_PROMPT_TEMPLATE.format(
            facts=facts,
        )

    def build_summary_rewrite_prompt(self, summary_draft: str) -> str:
        return SUMMARY_REWRITE_PROMPT_TEMPLATE.format(
            summary_draft=summary_draft,
        )

    # ---------- Fact builders ----------

    def build_facts(
        self,
        summary_report: dict[str, Any],
        targets: dict[str, Any],
        manual_check: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "summary_report": self.normalize_api_data(summary_report),
            "targets": self.normalize_api_data(targets),
            "manual_check": self.normalize_api_data(manual_check),
        }

    def build_manual_check_answer(
        self,
        facts: dict[str, Any],
        human_explanation: str | None = None,
    ) -> str:
        manual_check = facts.get("manual_check") or {}

        target = manual_check.get("target") or {}
        check_result = manual_check.get("check_result") or manual_check.get("result") or {}

        target_name = (
            target.get("name")
            or manual_check.get("target_name")
            or manual_check.get("name")
            or "Unknown target"
        )

        target_url = (
            target.get("url")
            or manual_check.get("target_url")
            or manual_check.get("url")
            or "Unknown URL"
        )

        expected_status = (
            target.get("expected_status")
            or manual_check.get("expected_status")
            or check_result.get("expected_status")
        )

        actual_status = (
            check_result.get("status_code")
            or manual_check.get("status_code")
            or manual_check.get("actual_status")
        )

        response_time_ms = (
            check_result.get("response_time_ms")
            or manual_check.get("response_time_ms")
        )

        result_type = (
            check_result.get("result_type")
            or manual_check.get("result_type")
            or "UNKNOWN"
        )

        alert_status = manual_check.get("alert_status", "UNKNOWN")
        notification_status = manual_check.get("notification_status", "UNKNOWN")
        severity = manual_check.get("severity")

        is_ok = result_type == "SUCCESS" and alert_status in (
            "NO_ALERT",
            "RESOLVED",
            "UNKNOWN",
        )

        status_line = "Статус: OK" if is_ok else "Статус: ПРОБЛЕМА"

        parts = [status_line]

        if human_explanation:
            parts.append("")
            parts.append(human_explanation)

        parts.append("")
        parts.append("Технические детали:")
        parts.append(f"Target: {target_name}")
        parts.append(f"URL: {target_url}")

        if expected_status is not None:
            parts.append(f"Expected HTTP: {expected_status}")

        if actual_status is not None:
            parts.append(f"Actual HTTP: {actual_status}")

        if response_time_ms is not None:
            parts.append(f"Response time: {response_time_ms} ms")

        parts.append(f"Result: {result_type}")
        parts.append(f"Alert: {alert_status}")

        if severity is not None:
            parts.append(f"Severity: {severity}")

        parts.append(f"Notification: {notification_status}")

        return "\n".join(parts)

    def build_summary_draft(self, facts: dict[str, Any]) -> str:
        summary = facts.get("summary_report") or {}
        targets_data = facts.get("targets") or {}

        total_targets = self.pick_first_existing(
            summary,
            ["total_targets", "targets_total"],
            "unknown",
        )

        active_targets = self.pick_first_existing(
            summary,
            ["active_targets", "targets_active"],
            "unknown",
        )

        open_alerts = self.pick_first_existing(
            summary,
            ["open_alerts", "alerts_open"],
            0,
        )

        total_checks = self.pick_first_existing(
            summary,
            ["total_checks", "checks_total"],
            "unknown",
        )

        failed_checks = self.pick_first_existing(
            summary,
            ["failed_checks", "checks_failed"],
            "unknown",
        )

        system_status = "OK" if open_alerts == 0 else "ПРОБЛЕМА"

        return (
            f"System status: {system_status}\n"
            f"Total targets: {total_targets}\n"
            f"Active targets: {active_targets}\n"
            f"Open alerts: {open_alerts}\n"
            f"Total checks: {total_checks}\n"
            f"Failed checks: {failed_checks}\n"
            f"Targets data: {targets_data}\n"
            "\n"
            "Explain this monitoring summary to the user in Russian. "
            "Do not invent facts. If open_alerts is greater than 0, do not say the system is fully stable."
        )

    # ---------- Main entry point ----------

    def explain(
        self,
        user_question: str,
        run_check: bool = False,
        mode: str | None = None,
        conversation_context: str = "",
    ) -> dict[str, Any]:
        selected_mode = self.detect_mode(
            user_question=user_question,
            run_check=run_check,
            mode=mode,
        )

        target_id = self.extract_target_id(user_question)

        logger.info(
            "AI assistant selected mode=%s target_id=%s",
            selected_mode,
            target_id,
        )

        # Free chat does not need CorpWatch API.
        if selected_mode == "free_chat":
            prompt = self.build_free_chat_prompt(
                user_question=user_question,
                conversation_context=conversation_context,
            )

            try:
                answer = self.ask_ollama(
                    prompt=prompt,
                    temperature=0.5,
                    num_predict=1000,
                )
            except requests.RequestException as error:
                logger.error("Ollama free_chat failed: %s", error)

                return {
                    "success": False,
                    "error": "ollama_unavailable",
                    "message": "AI-ассистент временно недоступен: Ollama не отвечает.",
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
        except requests.RequestException as error:
            logger.error("CorpWatch API unavailable: %s", error)

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
            except requests.RequestException as error:
                logger.error("Manual check failed for target_id=%s: %s", target_id, error)

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
                    num_predict=350,
                )
            except requests.RequestException as error:
                logger.warning("Ollama manual_check explanation failed: %s", error)
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
                temperature=0.2,
                num_predict=500,
            )
        except requests.RequestException as error:
            logger.warning("Ollama summary rewrite failed: %s", error)
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