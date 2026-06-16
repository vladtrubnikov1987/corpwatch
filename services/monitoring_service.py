import time

import requests

from repositories.check_result_repository import check_result_repository
from repositories.target_repository import target_repository


class MonitoringService:
    def check_target_now(self, target_id: int) -> dict:
        target = target_repository.get_target_by_id(target_id)

        if target is None:
            return {
                "success": False,
                "error": "Monitoring target not found",
            }

        if not target["is_active"]:
            return {
                "success": False,
                "error": "Monitoring target is inactive",
            }

        check_data = {
            "target_id": target_id,
            "status_code": None,
            "response_time_ms": None,
            "result_type": None,
            "error_message": None,
        }

        try:
            start_time = time.perf_counter()

            response = requests.get(
                target["url"],
                timeout=target["timeout_seconds"],
            )

            end_time = time.perf_counter()

            response_time_ms = int((end_time - start_time) * 1000)

            check_data["status_code"] = response.status_code
            check_data["response_time_ms"] = response_time_ms

            if response.status_code != target["expected_status"]:
                check_data["result_type"] = "WRONG_STATUS"

            elif response_time_ms > target["max_response_time_ms"]:
                check_data["result_type"] = "SLOW_RESPONSE"

            else:
                check_data["result_type"] = "SUCCESS"

        except requests.Timeout:
            check_data["result_type"] = "TIMEOUT"
            check_data["error_message"] = (
                f"Request timed out after {target['timeout_seconds']} seconds"
            )

        except requests.RequestException as error:
            check_data["result_type"] = "CONNECTION_ERROR"
            check_data["error_message"] = str(error)

        check_result_id = check_result_repository.create_check_result(check_data)

        return {
            "success": True,
            "message": "Manual check completed",
            "check_result_id": check_result_id,
            "target_id": target_id,
            "target_name": target["name"],
            "url": target["url"],
            "expected_status": target["expected_status"],
            "status_code": check_data["status_code"],
            "response_time_ms": check_data["response_time_ms"],
            "result_type": check_data["result_type"],
            "error_message": check_data["error_message"],
        }


monitoring_service = MonitoringService()