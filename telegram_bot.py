import os
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

    def should_run_manual_check(self, text: str) -> bool:
        lowered = text.lower()

        trigger_words = [
            "проверь",
            "проверить",
            "check target",
            "manual check",
            "что с target",
            "что с целью",
        ]

        return any(word in lowered for word in trigger_words)

    def ask_ai_assistant(self, question: str, run_check: bool) -> str:
        response = requests.post(
            f"{self.ai_assistant_url}/ai/explain",
            headers={
                "X-API-Key": self.api_key,
            },
            json={
                "question": question,
                "run_check": run_check,
            },
            timeout=150,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            return data.get("message", "AI assistant вернул ошибку.")

        return data.get("answer", "AI assistant не вернул answer.")

    def handle_message(self, message: dict[str, Any]) -> None:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return

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
                    "Что сейчас с системой?\n"
                    "Проверь target 6\n"
                    "Почему пришёл alert?"
                ),
            )
            return

        if text.startswith("/help"):
            self.send_message(
                chat_id,
                (
                    "Команды:\n"
                    "/start — начать\n"
                    "/help — помощь\n\n"
                    "Примеры:\n"
                    "Что сейчас с системой?\n"
                    "Проверь target 6\n"
                    "Проверь цель 6 и объясни простым языком"
                ),
            )
            return

        run_check = self.should_run_manual_check(text)

        try:
            self.send_typing_action(chat_id)

            answer = self.ask_ai_assistant(
                question=text,
                run_check=run_check,
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