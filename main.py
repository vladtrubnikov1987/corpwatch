import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config.settings import settings
from repositories.database import database_manager
from services.target_service import target_service
from utils.logger import logger


class ApiHandler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code: int, data: dict) -> None:
        response_body = json.dumps(data, indent=4, default=str).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
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

    def _check_api_key(self) -> bool:
        api_key = self.headers.get("X-API-Key")
        return api_key == settings.API_KEY

    def _extract_target_id(self) -> int | None:
        match = re.match(r"^/api/targets/(\d+)$", self.path)

        if match:
            return int(match.group(1))

        return None

    def do_GET(self) -> None:
        logger.info("GET request received: %s", self.path)

        if self.path == "/api/health":
            self.handle_health_check()
            return

        if self.path == "/api/targets":
            self.handle_get_all_targets()
            return

        target_id = self._extract_target_id()

        if target_id is not None:
            self.handle_get_target_by_id(target_id)
            return

        self._send_json_response(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def do_POST(self) -> None:
        logger.info("POST request received: %s", self.path)

        if not self._check_api_key():
            self._send_json_response(
                401,
                {
                    "success": False,
                    "error": "Invalid or missing API key",
                },
            )
            return

        if self.path == "/api/targets":
            self.handle_create_target()
            return

        self._send_json_response(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def do_PUT(self) -> None:
        logger.info("PUT request received: %s", self.path)

        if not self._check_api_key():
            self._send_json_response(
                401,
                {
                    "success": False,
                    "error": "Invalid or missing API key",
                },
            )
            return

        target_id = self._extract_target_id()

        if target_id is not None:
            self.handle_update_target(target_id)
            return

        self._send_json_response(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def do_DELETE(self) -> None:
        logger.info("DELETE request received: %s", self.path)

        if not self._check_api_key():
            self._send_json_response(
                401,
                {
                    "success": False,
                    "error": "Invalid or missing API key",
                },
            )
            return

        target_id = self._extract_target_id()

        if target_id is not None:
            self.handle_deactivate_target(target_id)
            return

        self._send_json_response(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def handle_health_check(self) -> None:
        try:
            database_ok = database_manager.test_connection()

            self._send_json_response(
                200,
                {
                    "success": True,
                    "service": "CorpWatch",
                    "status": "healthy",
                    "database": "connected" if database_ok else "not connected",
                },
            )

            logger.info("Health check completed successfully")

        except Exception as error:
            logger.error("Health check failed: %s", error)

            self._send_json_response(
                500,
                {
                    "success": False,
                    "service": "CorpWatch",
                    "status": "unhealthy",
                    "database": "not connected",
                    "error": str(error),
                },
            )

    def handle_create_target(self) -> None:
        try:
            data = self._read_json_body()
            result = target_service.create_target(data)

            logger.info("Monitoring target created: %s", result["target_id"])
            self._send_json_response(201, result)

        except ValueError as error:
            logger.warning("Target creation validation failed: %s", error)
            self._send_json_response(
                400,
                {
                    "success": False,
                    "error": str(error),
                },
            )

        except Exception as error:
            logger.error("Target creation failed: %s", error)
            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                },
            )

    def handle_get_all_targets(self) -> None:
        try:
            result = target_service.get_all_targets()
            self._send_json_response(200, result)

        except Exception as error:
            logger.error("Failed to get targets: %s", error)
            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                },
            )

    def handle_get_target_by_id(self, target_id: int) -> None:
        try:
            result = target_service.get_target_by_id(target_id)

            status_code = 200 if result["success"] else 404
            self._send_json_response(status_code, result)

        except Exception as error:
            logger.error("Failed to get target: %s", error)
            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                },
            )

    def handle_update_target(self, target_id: int) -> None:
        try:
            data = self._read_json_body()
            result = target_service.update_target(target_id, data)

            status_code = 200 if result["success"] else 404
            self._send_json_response(status_code, result)

        except ValueError as error:
            logger.warning("Target update validation failed: %s", error)
            self._send_json_response(
                400,
                {
                    "success": False,
                    "error": str(error),
                },
            )

        except Exception as error:
            logger.error("Target update failed: %s", error)
            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                },
            )

    def handle_deactivate_target(self, target_id: int) -> None:
        try:
            result = target_service.deactivate_target(target_id)

            status_code = 200 if result["success"] else 404
            self._send_json_response(status_code, result)

        except Exception as error:
            logger.error("Target deactivation failed: %s", error)
            self._send_json_response(
                500,
                {
                    "success": False,
                    "error": "Internal server error",
                },
            )


def run_server() -> None:
    server_address = (settings.APP_HOST, settings.APP_PORT)
    http_server = ThreadingHTTPServer(server_address, ApiHandler)

    logger.info(
        "CorpWatch API server started on %s:%s",
        settings.APP_HOST,
        settings.APP_PORT,
    )

    http_server.serve_forever()


if __name__ == "__main__":
    run_server()