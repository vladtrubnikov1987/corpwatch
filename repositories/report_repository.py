from repositories.database import database_manager


class ReportRepository:
    def get_summary_report(self) -> dict:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_targets,
                        SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) AS active_targets
                    FROM monitoring_targets;
                    """
                )
                targets_summary = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_checks,
                        SUM(CASE WHEN result_type = 'SUCCESS' THEN 1 ELSE 0 END) AS success_checks,
                        SUM(CASE WHEN result_type != 'SUCCESS' THEN 1 ELSE 0 END) AS failed_checks,
                        ROUND(AVG(response_time_ms), 2) AS average_response_time_ms,
                        MAX(response_time_ms) AS worst_response_time_ms,
                        MAX(checked_at) AS last_check_time
                    FROM check_results;
                    """
                )
                checks_summary = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT
                        SUM(CASE WHEN is_resolved = FALSE THEN 1 ELSE 0 END) AS open_alerts,
                        SUM(CASE WHEN is_resolved = TRUE THEN 1 ELSE 0 END) AS resolved_alerts
                    FROM alerts;
                    """
                )
                alerts_summary = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_notifications,
                        SUM(CASE WHEN status = 'SENT' THEN 1 ELSE 0 END) AS sent_notifications,
                        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_notifications
                    FROM notifications;
                    """
                )
                notifications_summary = cursor.fetchone()

                return {
                    "total_targets": targets_summary["total_targets"] or 0,
                    "active_targets": targets_summary["active_targets"] or 0,
                    "total_checks": checks_summary["total_checks"] or 0,
                    "success_checks": checks_summary["success_checks"] or 0,
                    "failed_checks": checks_summary["failed_checks"] or 0,
                    "average_response_time_ms": checks_summary["average_response_time_ms"] or 0,
                    "worst_response_time_ms": checks_summary["worst_response_time_ms"] or 0,
                    "open_alerts": alerts_summary["open_alerts"] or 0,
                    "resolved_alerts": alerts_summary["resolved_alerts"] or 0,
                    "total_notifications": notifications_summary["total_notifications"] or 0,
                    "sent_notifications": notifications_summary["sent_notifications"] or 0,
                    "failed_notifications": notifications_summary["failed_notifications"] or 0,
                    "last_check_time": str(checks_summary["last_check_time"])
                    if checks_summary["last_check_time"]
                    else None,
                }

        finally:
            connection.close()


report_repository = ReportRepository()