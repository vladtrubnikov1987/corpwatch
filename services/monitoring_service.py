import time

import requests

from repositories.alert_repository import alert_repository
from repositories.check_result_repository import check_result_repository
from repositories.target_repository import target_repository
from services.notification_service import notification_service


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

        alert_info = self.process_alert_logic(
            target=target,
            check_result_id=check_result_id,
            check_data=check_data,
        )

        notification_info = self.process_notification_logic(
            target=target,
            check_data=check_data,
            alert_info=alert_info,
        )

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
            "consecutive_failures": alert_info["consecutive_failures"],
            "alert_status": alert_info["alert_status"],
            "alert_id": alert_info["alert_id"],
            "alert_severity": alert_info["alert_severity"],
            "notification_status": notification_info["notification_status"],
            "notification_id": notification_info["notification_id"],
        }

    def process_alert_logic(
        self,
        target: dict,
        check_result_id: int,
        check_data: dict,
    ) -> dict:
        target_id = target["id"]
        result_type = check_data["result_type"]

        if result_type == "SUCCESS":
            target_repository.update_consecutive_failures(target_id, 0)

            resolved_count = alert_repository.resolve_open_alerts_by_target_id(
                target_id
            )

            return {
                "consecutive_failures": 0,
                "alert_status": "RESOLVED" if resolved_count > 0 else "NO_ALERT",
                "alert_id": None,
                "alert_severity": None,
            }

        current_failures = int(target["consecutive_failures"]) + 1

        target_repository.update_consecutive_failures(
            target_id,
            current_failures,
        )

        if current_failures < target["failure_threshold"]:
            return {
                "consecutive_failures": current_failures,
                "alert_status": "BELOW_THRESHOLD",
                "alert_id": None,
                "alert_severity": None,
            }

        open_alert = alert_repository.get_open_alert_by_target_id(target_id)

        if open_alert is not None:
            return {
                "consecutive_failures": current_failures,
                "alert_status": "ALREADY_OPEN",
                "alert_id": open_alert["id"],
                "alert_severity": open_alert["severity"],
            }

        severity = self.calculate_severity(
            result_type=result_type,
            status_code=check_data["status_code"],
            consecutive_failures=current_failures,
            failure_threshold=target["failure_threshold"],
        )

        message = self.build_alert_message(
            target=target,
            check_data=check_data,
            consecutive_failures=current_failures,
        )

        alert_id = alert_repository.create_alert(
            {
                "target_id": target_id,
                "check_result_id": check_result_id,
                "severity": severity,
                "message": message,
            }
        )

        return {
            "consecutive_failures": current_failures,
            "alert_status": "OPENED",
            "alert_id": alert_id,
            "alert_severity": severity,
        }

    def process_notification_logic(
        self,
        target: dict,
        check_data: dict,
        alert_info: dict,
    ) -> dict:
        if alert_info["alert_status"] == "OPENED":
            notification_result = notification_service.send_alert_opened_email(
                alert=alert_info,
                target=target,
                check_data=check_data,
            )

            return {
                "notification_status": notification_result["status"],
                "notification_id": notification_result["notification_id"],
            }

        if alert_info["alert_status"] == "RESOLVED":
            notification_result = notification_service.send_alert_resolved_email(
                target=target,
            )

            return {
                "notification_status": notification_result["status"],
                "notification_id": notification_result["notification_id"],
            }

        return {
            "notification_status": "NOT_REQUIRED",
            "notification_id": None,
        }

    def calculate_severity(
        self,
        result_type: str,
        status_code: int | None,
        consecutive_failures: int,
        failure_threshold: int,
    ) -> str:
        if consecutive_failures >= failure_threshold * 2:
            return "CRITICAL"

        if result_type in ("TIMEOUT", "CONNECTION_ERROR"):
            return "HIGH"

        if result_type == "WRONG_STATUS":
            if status_code is not None and status_code >= 500:
                return "HIGH"

            return "MEDIUM"

        if result_type == "SLOW_RESPONSE":
            return "LOW"

        return "LOW"

    def build_alert_message(
        self,
        target: dict,
        check_data: dict,
        consecutive_failures: int,
    ) -> str:
        return (
            f"Target '{target['name']}' failed check. "
            f"URL: {target['url']}. "
            f"Result type: {check_data['result_type']}. "
            f"Expected status: {target['expected_status']}. "
            f"Actual status: {check_data['status_code']}. "
            f"Response time: {check_data['response_time_ms']} ms. "
            f"Consecutive failures: {consecutive_failures}."
        )


monitoring_service = MonitoringService()