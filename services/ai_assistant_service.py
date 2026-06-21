import json
import os
import re
from typing import Any

import requests


# Deterministic diagnosis by result_type.
# This is CorpWatch domain logic written in code — NOT LLM reasoning.
DIAGNOSIS_BY_RESULT_TYPE = {
    "SUCCESS": "цель сейчас работает нормально",
    "SLOW_RESPONSE": "цель отвечает, но медленнее заданного порога",
    "WRONG_STATUS": "цель ответила, но неожиданным HTTP-кодом",
    "TIMEOUT": "цель не ответила за отведённый таймаут",
    "CONNECTION_ERROR": (
        "не удалось подключиться к цели: возможны проблемы с DNS, "
        "сетью или сам сервис недоступен"
    ),
}


# Few-shot prompt. The single example teaches the small model the tone,
# length and structure far better than a long list of rules.
PROMPT_TEMPLATE = """Ты — ассистент CorpWatch. Объясняешь данные мониторинга простым \
разговорным русским, как коллега рядом, а не как официальный отчёт.

Правила:
- 2–4 коротких фразы. Без заголовков и нумерованных разделов.
- Не повторяй один и тот же факт разными словами.
- Причину сбоя бери ТОЛЬКО из поля deterministic_diagnosis. Ничего не придумывай.
- Если цель активна, но проверки падают — так и скажи: цель активна, но не отвечает.
- Если данных мало — скажи, что стоит проверить дальше.

Пример хорошего ответа:
"Цель 6 (spectrdiagnostic.com) не отвечает уже 62 проверки подряд — это около \
10 минут. Сам CorpWatch работает нормально, проблема на стороне сервиса: не \
отвечает шлюз за прокси или туннелем. Стоит проверить, поднят ли demo-контейнер \
nginx и жив ли Cloudflare-туннель."

Факты CorpWatch:
{facts_json}

Вопрос пользователя:
{user_question}

Ответь коротко и живым русским языком."""


class AIAssistantService:
    """
    CorpWatch AI Assistant.

    Architecture:
    - Does NOT connect to MariaDB directly.
    - Reads facts only through CorpWatch API.
    - Does NOT let the LLM make monitoring decisions.
    - The LLM only rephrases verified facts in simple human language.
    """

    def __init__(self) -> None:
        self.corpwatch_api_url = os.getenv("CORPWATCH_API_URL", "http://app:8000").rstrip("/")
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://ollama:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.api_key = os.getenv("API_KEY", "change_me")

    # ---------- CorpWatch API access ----------

    def _get_json(self, path: str) -> dict[str, Any]:
        response = requests.get(f"{self.corpwatch_api_url}{path}", timeout=10)
        response.raise_for_status()
        return response.json()

    def _post_json(self, path: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.corpwatch_api_url}{path}",
            headers={"X-API-Key": self.api_key},
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
        patterns = [
            r"target\s+(\d+)",
            r"\bid\b\s*=?\s*(\d+)",   # \b avoids matching "covid 19", "android 7"
            r"таргет\s+(\d+)",
            r"цель\s+(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def estimate_downtime(
        self,
        consecutive_failures: Any,
        interval_seconds: Any,
    ) -> str | None:
        """
        Translate a raw failure count into something meaningful.

        The LLM cannot compute this — it does not know the check interval.
        So we do it in code and hand it over as a ready fact.
        """

        try:
            failures = int(consecutive_failures)
            interval = int(interval_seconds)
        except (TypeError, ValueError):
            return None

        if failures <= 0 or interval <= 0:
            return None

        minutes = round(failures * interval / 60)
        return (
            f"{failures} проверок подряд с ошибкой при интервале {interval}с — "
            f"цель недоступна примерно {minutes} мин"
        )

    def classify_result(
        self,
        result_type: str | None,
        status_code: int | None,
    ) -> str:
        """Deterministic classification. CorpWatch domain logic, not LLM guessing."""

        # Specific status codes must be checked BEFORE the generic WRONG_STATUS,
        # otherwise these branches become unreachable.
        if result_type == "WRONG_STATUS" and status_code == 530:
            return (
                "похоже на проблему Cloudflare-туннеля или origin: "
                "demo-сервис может быть недоступен за Cloudflare"
            )

        if result_type == "WRONG_STATUS" and status_code in (502, 503, 504):
            return (
                "похоже на проблему шлюза/upstream: "
                "сервис может быть недоступен за прокси или туннелем"
            )

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
        """Build compact, operationally relevant facts for the LLM."""

        compact_facts: dict[str, Any] = {
            "summary": summary_report.get("data", summary_report),
            "active_targets": [],
            "manual_check": None,
            "downtime_estimate": None,
            "deterministic_diagnosis": "ручная проверка не запрашивалась",
        }

        targets_data = targets.get("data", targets)
        targets_by_id: dict[Any, dict[str, Any]] = {}

        if isinstance(targets_data, list):
            for target in targets_data:
                targets_by_id[target.get("id")] = target
                compact_facts["active_targets"].append(
                    {
                        "id": target.get("id"),
                        "name": target.get("name"),
                        "url": target.get("url"),
                        "is_active": target.get("is_active"),
                        "expected_status": target.get("expected_status"),
                        "consecutive_failures": target.get("consecutive_failures"),
                    }
                )

        if manual_check:
            result_type = manual_check.get("result_type")
            status_code = manual_check.get("status_code")
            target_id = manual_check.get("target_id")

            compact_facts["manual_check"] = {
                "target_id": target_id,
                "target_name": manual_check.get("target_name"),
                "target_url": manual_check.get("target_url"),
                "expected_status": manual_check.get("expected_status"),
                "actual_status": status_code,
                "result_type": result_type,
                "response_time_ms": manual_check.get("response_time_ms"),
                "alert_status": manual_check.get("alert_status"),
                "alert_severity": manual_check.get("alert_severity"),
                "notification_status": manual_check.get("notification_status"),
                "error_message": manual_check.get("error_message"),
            }

            compact_facts["deterministic_diagnosis"] = self.classify_result(
                result_type=result_type,
                status_code=status_code,
            )

            # Compute downtime in code, using the target's own interval.
            focused = targets_by_id.get(target_id, {})
            compact_facts["downtime_estimate"] = self.estimate_downtime(
                focused.get("consecutive_failures"),
                focused.get("check_interval_seconds"),
            )

        return compact_facts

    def build_prompt(self, user_question: str, facts: dict[str, Any]) -> str:
        # JSON (not a raw Python dict repr) — the model parses it more reliably,
        # and ensure_ascii=False keeps Russian readable.
        facts_json = json.dumps(facts, ensure_ascii=False, indent=2, default=str)
        return PROMPT_TEMPLATE.format(facts_json=facts_json, user_question=user_question)

    # ---------- LLM ----------

    def ask_ollama(self, prompt: str) -> str:
        response = requests.post(
            f"{self.ollama_api_url}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                # Low temperature -> focused, less rambling.
                # num_predict caps length so the model can't pad.
                "options": {"temperature": 0.3, "num_predict": 250},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    # ---------- Main entry point ----------

    def explain(self, user_question: str, run_check: bool = False) -> dict[str, Any]:
        target_id = self.extract_target_id(user_question)

        # 1. Read facts from CorpWatch API.
        try:
            summary_report = self.get_summary_report()
            targets = self.get_targets()
        except requests.RequestException:
            return {
                "success": False,
                "error": "corpwatch_api_unavailable",
                "message": "Не удалось получить данные из CorpWatch API. "
                           "Проверь, что сервис app доступен.",
            }

        # 2. Optionally run a manual check.
        manual_check = None
        if run_check:
            if target_id is None:
                return {
                    "success": False,
                    "error": "target_id_required",
                    "message": "Напиши target id. Например: проверь target 6",
                }
            try:
                manual_check = self.run_manual_check(target_id)
            except requests.RequestException:
                return {
                    "success": False,
                    "error": "manual_check_failed",
                    "message": f"Не удалось запустить ручную проверку target {target_id}.",
                }

        # 3. Build deterministic facts.
        facts = self.build_facts(
            summary_report=summary_report,
            targets=targets,
            manual_check=manual_check,
        )

        # 4. LLM only rephrases. If it is down, monitoring still works.
        prompt = self.build_prompt(user_question=user_question, facts=facts)
        try:
            answer = self.ask_ollama(prompt)
        except requests.RequestException:
            return {
                "success": False,
                "error": "ollama_unavailable",
                "message": "AI-ассистент временно недоступен (Ollama не отвечает). "
                           "Мониторинг при этом работает — проверь alerts напрямую.",
                "facts": facts,
            }

        return {
            "success": True,
            "question": user_question,
            "target_id": target_id,
            "manual_check_was_run": manual_check is not None,
            "facts": facts,
            "answer": answer,
        }


ai_assistant_service = AIAssistantService()