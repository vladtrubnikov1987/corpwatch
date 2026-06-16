from typing import Optional

from repositories.database import database_manager


class AlertRepository:
    def create_alert(self, data: dict) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO alerts (
                        target_id,
                        check_result_id,
                        severity,
                        message,
                        is_resolved
                    )
                    VALUES (%s, %s, %s, %s, FALSE);
                    """,
                    (
                        data["target_id"],
                        data["check_result_id"],
                        data["severity"],
                        data["message"],
                    ),
                )

                connection.commit()
                return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_open_alert_by_target_id(self, target_id: int) -> Optional[dict]:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM alerts
                    WHERE target_id = %s
                      AND is_resolved = FALSE
                    ORDER BY id DESC
                    LIMIT 1;
                    """,
                    (target_id,),
                )

                return cursor.fetchone()

        finally:
            connection.close()

    def resolve_open_alerts_by_target_id(self, target_id: int) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE alerts
                    SET
                        is_resolved = TRUE,
                        resolved_at = CURRENT_TIMESTAMP
                    WHERE target_id = %s
                      AND is_resolved = FALSE;
                    """,
                    (target_id,),
                )

                connection.commit()
                return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_all_alerts(self) -> list[dict]:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM alerts
                    ORDER BY id DESC;
                    """
                )

                return cursor.fetchall()

        finally:
            connection.close()


alert_repository = AlertRepository()