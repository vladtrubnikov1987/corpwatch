import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config.settings import settings
from repositories.database import database_manager
from utils.logger import logger


class ApiHandler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code: int, data: dict) -> None:
        response_body = json.dumps(data, indent=4).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def do_GET(self) -> None:
        logger.info("GET request received: %s", self.path)

        if self.path == "/api/health":
            self.handle_health_check()
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