import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from services.ai_assistant_service import ai_assistant_service
from utils.logger import logger


def parse_bool(value) -> bool:
    if value is True:
        return True

    if value is False or value is None:
        return False

    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "y", "да")

    return False


class AIAssistantHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        logger.info("AI Assistant HTTP request: " + format, *args)

    def _send_json_response(self, status_code: int, data: dict) -> None:
        response_body = json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))

        if content_length == 0:
            return {}

        body = self.rfile.read(content_length)

        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON body")

    def _is_authorized(self) -> bool:
        expected_api_key = os.getenv("API_KEY", "change_me")
        provided_api_key = self.headers.get("X-API-Key")

        return provided_api_key == expected_api_key

    def do_GET(self) -> None:
        if self.path == "/ai/health":
            self._send_json_response(
                200,
                {
                    "success": True,
                    "service": "corpwatch_ai_assistant",
                    "status": "healthy",
                    "type": "liveness",
                },
            )
            return

        self._send_json_response(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def do_POST(self) -> None:
        if self.path != "/ai/explain":
            self._send_json_response(
                404,
                {
                    "success": False,
                    "error": "Endpoint not found",
                },
            )
            return

        if not self._is_authorized():
            logger.warning("Unauthorized request to /ai/explain")

            self._send_json_response(
                401,
                {
                    "success": False,
                    "error": "Unauthorized",
                },
            )
            return

        try:
            data = self._read_json_body()

            question = data.get("question", "Что сейчас сломалось?")
            run_check = parse_bool(data.get("run_check", False))
            mode = data.get("mode")
            conversation_context = data.get("conversation_context", "")

            logger.info(
                "AI explain request received. mode=%s run_check=%s question=%s context_len=%s",
                mode,
                run_check,
                question,
                len(conversation_context),
            )

            result = ai_assistant_service.explain(
                user_question=question,
                run_check=run_check,
                mode=mode,
                conversation_context=conversation_context,
            )

            status_code = 200 if result.get("success") else 400
            self._send_json_response(status_code, result)

        except ValueError as error:
            logger.warning("AI assistant received invalid request: %s", error)

            self._send_json_response(
                400,
                {
                    "success": False,
                    "error": "Invalid request",
                    "message": "Request body must be valid JSON",
                },
            )

        except Exception as error:
            logger.error("AI assistant failed to process request: %s", error)

            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                    "message": "AI assistant failed to process request. Check container logs.",
                },
            )


def run_ai_assistant_server() -> None:
    host = os.getenv("AI_ASSISTANT_HOST", "0.0.0.0")
    port = int(os.getenv("AI_ASSISTANT_PORT", "8010"))

    server_address = (host, port)
    http_server = ThreadingHTTPServer(server_address, AIAssistantHandler)

    logger.info("CorpWatch AI Assistant started on %s:%s", host, port)

    http_server.serve_forever()


if __name__ == "__main__":
    run_ai_assistant_server()