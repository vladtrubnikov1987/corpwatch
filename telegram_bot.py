import os
import re
import time
from typing import Any

import requests

from utils.logger import logger


class CorpWatchTelegramBot:
    def __init__(self) -> None:
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not self.telegram_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}"

        self.ai_assistant_url = os.getenv(
            "AI_ASSISTANT_URL",
            "http://ai_assistant:8010",
        ).rstrip("/")

        self.corpwatch_api_url = os.getenv(
            "CORPWATCH_API_URL",
            "http://app:8000",
        ).rstrip("/")

        self.api_key = os.getenv("API_KEY", "change_me")

        self.poll_interval_seconds = int(
            os.getenv("TELEGRAM_POLL_INTERVAL_SECONDS", "2")
        )

        allowed_chat_ids_raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")

        self.allowed_chat_ids = {
            int(chat_id.strip())
            for chat_id in allowed_chat_ids_raw.split(",")
            if chat_id.strip()
        }

        self.offset = 0

    def is_chat_allowed(self, chat_id: int) -> bool:
        if not self.allowed_chat_ids:
            return True

        return chat_id in self.allowed_chat_ids

    def send_message(self, chat_id: int, text: str) -> None:
        response = requests.post(
            f"{self.telegram_api_url}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )

        response.raise_for_status()

    def send_typing_action(self, chat_id: int) -> None:
        try:
            requests.post(
                f"{self.telegram_api_url}/sendChatAction",
                json={
                    "chat_id": chat_id,
                    "action": "typing",
                },
                timeout=10,
            )
        except requests.RequestException as error:
            logger.warning("Failed to send Telegram typing action: %s", error)

    def get_updates(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.telegram_api_url}/getUpdates",
            params={
                "offset": self.offset,
                "timeout": 30,
            },
            timeout=40,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            logger.warning("Telegram getUpdates returned not ok: %s", data)
            return []

        return data.get("result", [])

    # ---------- CorpWatch API ----------

    def get_targets(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.corpwatch_api_url}/api/targets",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        return data.get("targets", data.get("data", []))

    def get_targets_text(self) -> str:
        targets = self.get_targets()

        if not targets:
            return "В CorpWatch пока нет targets."

        active_targets = []
        inactive_targets = []

        for target in targets:
            line = (
                f"{target.get('id')} — "
                f"{target.get('name')} — "
                f"{target.get('url')} — "
                f"expected {target.get('expected_status')}"
            )

            if int(target.get("is_active", 0)) == 1:
                active_targets.append(line)
            else:
                inactive_targets.append(line)

        parts = []

        if active_targets:
            parts.append("Active targets:")
            parts.extend(active_targets)

        if inactive_targets:
            parts.append("")
            parts.append("Inactive targets:")
            parts.extend(inactive_targets)

        return "\n".join(parts)

    def get_target_text(self, target_id: int) -> str:
        targets = self.get_targets()

        for target in targets:
            if int(target.get("id")) == target_id:
                status = "active" if int(target.get("is_active", 0)) == 1 else "inactive"

                return (
                    f"Target {target.get('id')} — {target.get('name')}\n\n"
                    f"URL: {target.get('url')}\n"
                    f"Expected status: {target.get('expected_status')}\n"
                    f"Timeout: {target.get('timeout_seconds')} sec\n"
                    f"Max response time: {target.get('max_response_time_ms')} ms\n"
                    f"Check interval: {target.get('check_interval_seconds')} sec\n"
                    f"Failure threshold: {target.get('failure_threshold')}\n"
                    f"Status: {status}\n\n"
                    f"Чтобы запустить проверку, напиши:\n"
                    f"проверь target {target_id}"
                )

        return (
            f"Target {target_id} не найден.\n"
            f"Напиши /targets, чтобы увидеть список targets."
        )

    # ---------- Intent helpers ----------

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

    def has_check_intent(self, text: str) -> bool:
        lowered = text.lower()

        check_words = [
            "проверь",
            "проверить",
            "проверяй",
            "запусти проверку",
            "сделай проверку",
            "manual check",
            "check",
        ]

        return any(word in lowered for word in check_words)

    def is_system_status_question(self, text: str) -> bool:
        lowered = text.lower()

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

        return any(phrase in lowered for phrase in system_phrases)

    def detect_mode(self, text: str) -> str:
        target_id = self.extract_target_id(text)
        check_intent = self.has_check_intent(text)
        system_status_question = self.is_system_status_question(text)

        if check_intent and target_id is not None:
            return "manual_check"

        if system_status_question:
            return "system_summary"

        return "free_chat"

    # ---------- AI Assistant ----------

    def ask_ai_assistant(
        self,
        question: str,
        run_check: bool,
        mode: str,
    ) -> str:
        response = requests.post(
            f"{self.ai_assistant_url}/ai/explain",
            headers={
                "X-API-Key": self.api_key,
            },
            json={
                "question": question,
                "run_check": run_check,
                "mode": mode,
            },
            timeout=150,
        )

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return "AI assistant вернул невалидный ответ."

        if not response.ok:
            return data.get(
                "message",
                f"AI assistant вернул ошибку HTTP {response.status_code}.",
            )

        if not data.get("success"):
            return data.get("message", "AI assistant вернул ошибку.")

        return data.get("answer", "AI assistant не вернул answer.")

    # ---------- Message handling ----------

    def handle_message(self, message: dict[str, Any]) -> None:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return

        text = text.strip()

        logger.info("Telegram message received from chat_id=%s: %s", chat_id, text)

        if not self.is_chat_allowed(chat_id):
            logger.warning("Ignored message from unauthorized chat_id=%s", chat_id)
            return

        if text.startswith("/start"):
            self.send_message(
                chat_id,
                (
                    "Привет. Я CorpWatch AI Assistant.\n\n"
                    "Можешь написать:\n"
                    "/targets\n"
                    "4\n"
                    "target 4\n"
                    "проверь target 4\n"
                    "что сейчас с системой?\n"
                    "что такое API?"
                ),
            )
            return

        if text.startswith("/help"):
            self.send_message(
                chat_id,
                (
                    "Команды:\n"
                    "/start — начать\n"
                    "/help — помощь\n"
                    "/targets — показать targets\n\n"
                    "Примеры:\n"
                    "4 — показать информацию о target 4\n"
                    "target 4 — показать информацию о target 4\n"
                    "проверь target 4 — запустить manual check\n"
                    "проверь — попросит указать target id\n"
                    "что сейчас с системой? — summary CorpWatch\n"
                    "что такое API? — свободный вопрос к Ollama"
                ),
            )
            return

        if text.startswith("/targets"):
            try:
                self.send_typing_action(chat_id)
                targets_text = self.get_targets_text()
                self.send_message(chat_id, targets_text)
            except requests.RequestException as error:
                logger.error("Telegram bot failed to get targets: %s", error)
                self.send_message(
                    chat_id,
                    "Не смог получить targets из CorpWatch API. Проверь контейнер app.",
                )

            return

        target_id = self.extract_target_id(text)
        check_intent = self.has_check_intent(text)

        if check_intent and target_id is None:
            self.send_message(
                chat_id,
                "Напиши target id. Например: проверь target 4",
            )
            return

        if target_id is not None and not check_intent:
            try:
                self.send_typing_action(chat_id)
                target_text = self.get_target_text(target_id)
                self.send_message(chat_id, target_text)
            except requests.RequestException as error:
                logger.error("Telegram bot failed to get target info: %s", error)
                self.send_message(
                    chat_id,
                    "Не смог получить target из CorpWatch API. Проверь контейнер app.",
                )

            return

        mode = self.detect_mode(text)
        run_check = mode == "manual_check"

        try:
            self.send_typing_action(chat_id)

            answer = self.ask_ai_assistant(
                question=text,
                run_check=run_check,
                mode=mode,
            )

            self.send_message(chat_id, answer)

        except requests.RequestException as error:
            logger.error("Telegram bot failed to call AI assistant: %s", error)

            self.send_message(
                chat_id,
                (
                    "Не смог получить ответ от CorpWatch AI Assistant. "
                    "Проверь контейнеры ai_assistant и ollama."
                ),
            )

    def run(self) -> None:
        logger.info("CorpWatch Telegram bot started")
        logger.info("AI assistant URL: %s", self.ai_assistant_url)
        logger.info("CorpWatch API URL: %s", self.corpwatch_api_url)

        if self.allowed_chat_ids:
            logger.info("Telegram whitelist enabled: %s", self.allowed_chat_ids)
        else:
            logger.warning("Telegram whitelist is empty. Bot accepts any chat.")

        while True:
            try:
                updates = self.get_updates()

                for update in updates:
                    self.offset = update["update_id"] + 1

                    message = update.get("message")

                    if message:
                        self.handle_message(message)

            except Exception as error:
                logger.error("Telegram bot loop error: %s", error)
                time.sleep(self.poll_interval_seconds)


if __name__ == "__main__":
    bot = CorpWatchTelegramBot()
    bot.run()