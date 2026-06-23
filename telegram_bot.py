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

        # Short in-memory conversation context.
        # It resets when container restarts.
        self.chat_memory: dict[int, list[str]] = {}
        self.max_memory_messages = int(os.getenv("TELEGRAM_MEMORY_MESSAGES", "8"))

    # ---------- Telegram low-level ----------

    def is_chat_allowed(self, chat_id: int) -> bool:
        if not self.allowed_chat_ids:
            return True

        return chat_id in self.allowed_chat_ids

    def send_message(self, chat_id: int, text: str) -> None:
        # Telegram message hard limit is 4096 chars.
        chunks = self.split_message(text, max_length=3900)

        for chunk in chunks:
            response = requests.post(
                f"{self.telegram_api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )

            response.raise_for_status()

    def split_message(self, text: str, max_length: int = 3900) -> list[str]:
        if len(text) <= max_length:
            return [text]

        chunks = []
        current = ""

        for paragraph in text.split("\n"):
            if len(current) + len(paragraph) + 1 <= max_length:
                current += paragraph + "\n"
            else:
                if current.strip():
                    chunks.append(current.strip())

                current = paragraph + "\n"

        if current.strip():
            chunks.append(current.strip())

        return chunks

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

    # ---------- Memory ----------

    def get_conversation_context(self, chat_id: int) -> str:
        messages = self.chat_memory.get(chat_id, [])
        return "\n".join(messages[-self.max_memory_messages:])

    def save_to_memory(self, chat_id: int, role: str, text: str) -> None:
        if chat_id not in self.chat_memory:
            self.chat_memory[chat_id] = []

        cleaned_text = text.strip()

        if len(cleaned_text) > 1200:
            cleaned_text = cleaned_text[:1200] + "... [truncated]"

        self.chat_memory[chat_id].append(f"{role}: {cleaned_text}")

        if len(self.chat_memory[chat_id]) > self.max_memory_messages:
            self.chat_memory[chat_id] = self.chat_memory[chat_id][-self.max_memory_messages:]

    def clear_memory(self, chat_id: int) -> None:
        self.chat_memory.pop(chat_id, None)

    # ---------- CorpWatch API ----------

    def get_targets(self) -> dict[str, Any]:
        response = requests.get(
            f"{self.corpwatch_api_url}/api/targets",
            timeout=15,
        )

        response.raise_for_status()
        return response.json()

    def get_target_by_id(self, target_id: int) -> dict[str, Any]:
        response = requests.get(
            f"{self.corpwatch_api_url}/api/targets/{target_id}",
            timeout=15,
        )

        response.raise_for_status()
        return response.json()

    # ---------- Intent detection ----------

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

    def detect_intent(self, text: str) -> tuple[str, bool]:
        normalized = text.strip().lower()

        if normalized in ("/start", "start"):
            return "start", False

        if normalized in ("/help", "help", "помощь"):
            return "help", False

        if normalized in ("/memory_clear", "memory clear", "очисти память"):
            return "memory_clear", False

        if normalized in ("/targets", "targets", "цели", "таргеты"):
            return "targets", False

        system_summary_words = [
            "что сейчас с системой",
            "что с системой",
            "статус системы",
            "summary",
            "system summary",
            "сводка",
            "общий статус",
        ]

        if any(word in normalized for word in system_summary_words):
            return "system_summary", False

        check_words = [
            "проверь",
            "проверить",
            "check target",
            "run check",
            "manual check",
        ]

        if any(word in normalized for word in check_words) and self.extract_target_id(normalized):
            return "manual_check", True

        # Bare target number or "target 4" is read-only target info.
        if self.extract_target_id(normalized) is not None:
            target_info_patterns = [
                r"^\d+$",
                r"^target\s+\d+$",
                r"^id\s*=?\s*\d+$",
                r"^таргет\s+\d+$",
                r"^цель\s+\d+$",
            ]

            if any(re.match(pattern, normalized, re.IGNORECASE) for pattern in target_info_patterns):
                return "target_info", False

        return "free_chat", False

    # ---------- Formatting ----------

    def format_targets(self, data: dict[str, Any]) -> str:
        targets = data.get("targets", [])

        if not targets:
            return "Targets не найдены."

        lines = ["Monitoring targets:"]

        for target in targets:
            target_id = target.get("id")
            name = target.get("name")
            url = target.get("url")
            is_active = target.get("is_active")
            expected_status = target.get("expected_status")
            failure_threshold = target.get("failure_threshold")
            consecutive_failures = target.get("consecutive_failures")

            status = "active" if is_active else "inactive"

            lines.append(
                f"{target_id}. {name}\n"
                f"   URL: {url}\n"
                f"   Status: {status}\n"
                f"   Expected HTTP: {expected_status}\n"
                f"   Failures: {consecutive_failures}/{failure_threshold}"
            )

        return "\n\n".join(lines)

    def format_target_info(self, data: dict[str, Any]) -> str:
        target = data.get("target") or data

        if not target:
            return "Target не найден."

        target_id = target.get("id")
        name = target.get("name")
        url = target.get("url")
        expected_status = target.get("expected_status")
        timeout_seconds = target.get("timeout_seconds")
        max_response_time_ms = target.get("max_response_time_ms")
        check_interval_seconds = target.get("check_interval_seconds")
        failure_threshold = target.get("failure_threshold")
        consecutive_failures = target.get("consecutive_failures")
        is_active = target.get("is_active")

        active_text = "active" if is_active else "inactive"

        return (
            f"Target {target_id}: {name}\n\n"
            f"URL: {url}\n"
            f"Status: {active_text}\n"
            f"Expected HTTP: {expected_status}\n"
            f"Timeout: {timeout_seconds} sec\n"
            f"Max response time: {max_response_time_ms} ms\n"
            f"Check interval: {check_interval_seconds} sec\n"
            f"Failure threshold: {failure_threshold}\n"
            f"Consecutive failures: {consecutive_failures}\n\n"
            f"Это read-only запрос. Проверка не запускалась."
        )

    def help_text(self) -> str:
        return (
            "CorpWatch Telegram bot\n\n"
            "Команды:\n"
            "/targets — показать все targets\n"
            "target 4 или 4 — показать target info без проверки\n"
            "проверь target 4 — запустить manual check\n"
            "что сейчас с системой? — system summary\n"
            "/memory_clear — очистить контекст диалога\n\n"
            "Также можно задавать обычные вопросы в free_chat режиме."
        )

    # ---------- AI Assistant ----------

    def call_ai_assistant(
        self,
        text: str,
        mode: str,
        run_check: bool,
        conversation_context: str,
    ) -> dict[str, Any]:
        payload = {
            "question": text,
            "run_check": run_check,
            "mode": mode,
            "conversation_context": conversation_context,
        }

        response = requests.post(
            f"{self.ai_assistant_url}/ai/explain",
            headers={
                "X-API-Key": self.api_key,
            },
            json=payload,
            timeout=220,
        )

        response.raise_for_status()
        return response.json()

    # ---------- Update handling ----------

    def handle_message(self, message: dict[str, Any]) -> None:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return

        if not self.is_chat_allowed(chat_id):
            logger.warning("Telegram chat_id=%s is not allowed", chat_id)
            return

        text = text.strip()

        logger.info("Telegram message received. chat_id=%s text=%s", chat_id, text)

        intent, run_check = self.detect_intent(text)

        try:
            if intent == "start":
                answer = (
                    "CorpWatch bot запущен.\n\n"
                    "Напиши /targets, чтобы увидеть targets.\n"
                    "Напиши 'проверь target 4', чтобы запустить manual check.\n"
                    "Или задай обычный вопрос."
                )
                self.send_message(chat_id, answer)
                self.save_to_memory(chat_id, "assistant", answer)
                return

            if intent == "help":
                answer = self.help_text()
                self.send_message(chat_id, answer)
                self.save_to_memory(chat_id, "assistant", answer)
                return

            if intent == "memory_clear":
                self.clear_memory(chat_id)
                self.send_message(chat_id, "Контекст диалога очищен.")
                return

            if intent == "targets":
                self.send_typing_action(chat_id)
                data = self.get_targets()
                answer = self.format_targets(data)
                self.send_message(chat_id, answer)
                self.save_to_memory(chat_id, "user", text)
                self.save_to_memory(chat_id, "assistant", answer)
                return

            if intent == "target_info":
                self.send_typing_action(chat_id)
                target_id = self.extract_target_id(text)

                if target_id is None:
                    self.send_message(chat_id, "Напиши target id. Например: target 4")
                    return

                data = self.get_target_by_id(target_id)
                answer = self.format_target_info(data)
                self.send_message(chat_id, answer)
                self.save_to_memory(chat_id, "user", text)
                self.save_to_memory(chat_id, "assistant", answer)
                return

            # manual_check, system_summary, free_chat go through AI Assistant.
            self.send_typing_action(chat_id)

            conversation_context = self.get_conversation_context(chat_id)

            result = self.call_ai_assistant(
                text=text,
                mode=intent,
                run_check=run_check,
                conversation_context=conversation_context,
            )

            answer = result.get("answer") or result.get("message") or "AI Assistant вернул пустой ответ."

            self.send_message(chat_id, answer)

            self.save_to_memory(chat_id, "user", text)
            self.save_to_memory(chat_id, "assistant", answer)

        except requests.RequestException as error:
            logger.error("Telegram request handling failed: %s", error)

            self.send_message(
                chat_id,
                (
                    "Ошибка при обработке запроса. "
                    "Проверь контейнеры corpwatch_ai_assistant, corpwatch_app и corpwatch_ollama."
                ),
            )

        except Exception as error:
            logger.error("Unexpected Telegram bot error: %s", error)

            self.send_message(
                chat_id,
                "Внутренняя ошибка Telegram bot. Проверь docker logs corpwatch_telegram_bot.",
            )

    def handle_update(self, update: dict[str, Any]) -> None:
        update_id = update.get("update_id")

        if update_id is not None:
            self.offset = update_id + 1

        message = update.get("message")

        if message:
            self.handle_message(message)

    def run(self) -> None:
        logger.info("CorpWatch Telegram bot started")

        while True:
            try:
                updates = self.get_updates()

                for update in updates:
                    self.handle_update(update)

            except requests.RequestException as error:
                logger.error("Telegram polling failed: %s", error)
                time.sleep(self.poll_interval_seconds)

            except Exception as error:
                logger.error("Unexpected Telegram bot loop error: %s", error)
                time.sleep(self.poll_interval_seconds)

            time.sleep(self.poll_interval_seconds)


if __name__ == "__main__":
    bot = CorpWatchTelegramBot()
    bot.run()