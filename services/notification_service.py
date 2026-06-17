import smtplib
from email.message import EmailMessage

from config.settings import settings
from repositories.notification_repository import notification_repository
from utils.logger import logger


class NotificationService:
    def send_email(
        self,
        alert_id: int | None,
        notification_type: str,
        subject: str,
        body: str,
    ) -> dict:
        try:
            message = EmailMessage()
            message["From"] = settings.SMTP_FROM
            message["To"] = settings.SMTP_TO
            message["Subject"] = subject
            message.set_content(body)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()

                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(
                        settings.SMTP_USERNAME,
                        settings.SMTP_PASSWORD,
                    )

                smtp.send_message(message)

            notification_id = notification_repository.create_notification(
                {
                    "alert_id": alert_id,
                    "notification_type": notification_type,
                    "recipient_email": settings.SMTP_TO,
                    "subject": subject,
                    "body": body,
                    "status": "SENT",
                    "error_message": None,
                }
            )

            logger.info(
                "Email notification sent successfully. notification_id=%s",
                notification_id,
            )

            return {
                "success": True,
                "notification_id": notification_id,
                "status": "SENT",
            }

        except Exception as error:
            logger.error("Email notification failed: %s", error)

            notification_id = notification_repository.create_notification(
                {
                    "alert_id": alert_id,
                    "notification_type": notification_type,
                    "recipient_email": settings.SMTP_TO,
                    "subject": subject,
                    "body": body,
                    "status": "FAILED",
                    "error_message": str(error),
                }
            )

            return {
                "success": False,
                "notification_id": notification_id,
                "status": "FAILED",
                "error": str(error),
            }

    def send_alert_opened_email(self, alert: dict, target: dict, check_data: dict) -> dict:
        subject = f"CorpWatch Alert OPENED: {target['name']}"

        body = (
            "CorpWatch detected a monitoring problem.\n\n"
            f"Alert ID: {alert['alert_id']}\n"
            f"Target: {target['name']}\n"
            f"URL: {target['url']}\n"
            f"Severity: {alert['alert_severity']}\n"
            f"Result type: {check_data['result_type']}\n"
            f"Expected status: {target['expected_status']}\n"
            f"Actual status: {check_data['status_code']}\n"
            f"Response time: {check_data['response_time_ms']} ms\n"
            f"Consecutive failures: {alert['consecutive_failures']}\n"
        )

        notification_type = (
            "SLOW_RESPONSE"
            if check_data["result_type"] == "SLOW_RESPONSE"
            else "FAILURE"
        )

        return self.send_email(
            alert_id=alert["alert_id"],
            notification_type=notification_type,
            subject=subject,
            body=body,
        )

    def send_alert_resolved_email(self, target: dict) -> dict:
        subject = f"CorpWatch Alert RESOLVED: {target['name']}"

        body = (
            "CorpWatch detected that the target has recovered.\n\n"
            f"Target: {target['name']}\n"
            f"URL: {target['url']}\n"
            "Current result: SUCCESS\n"
            "Open alerts for this target were resolved.\n"
        )

        return self.send_email(
            alert_id=None,
            notification_type="RECOVERY",
            subject=subject,
            body=body,
        )


notification_service = NotificationService()