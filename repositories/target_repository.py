from typing import Optional

from repositories.database import database_manager


class TargetRepository:
    def create_target(self, data: dict) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO monitoring_targets (
                        user_id,
                        name,
                        url,
                        expected_status,
                        timeout_seconds,
                        max_response_time_ms,
                        check_interval_seconds,
                        failure_threshold
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        data["user_id"],
                        data["name"],
                        data["url"],
                        data.get("expected_status", 200),
                        data.get("timeout_seconds", 5),
                        data.get("max_response_time_ms", 1000),
                        data.get("check_interval_seconds", 60),
                        data.get("failure_threshold", 3),
                    ),
                )

                connection.commit()
                return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_all_targets(self) -> list[dict]:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM monitoring_targets
                    ORDER BY id DESC;
                    """
                )
                return cursor.fetchall()

        finally:
            connection.close()

    def get_target_by_id(self, target_id: int) -> Optional[dict]:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM monitoring_targets
                    WHERE id = %s;
                    """,
                    (target_id,),
                )
                return cursor.fetchone()

        finally:
            connection.close()

    def update_target(self, target_id: int, data: dict) -> bool:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE monitoring_targets
                    SET
                        name = %s,
                        url = %s,
                        expected_status = %s,
                        timeout_seconds = %s,
                        max_response_time_ms = %s,
                        check_interval_seconds = %s,
                        failure_threshold = %s
                    WHERE id = %s;
                    """,
                    (
                        data["name"],
                        data["url"],
                        data.get("expected_status", 200),
                        data.get("timeout_seconds", 5),
                        data.get("max_response_time_ms", 1000),
                        data.get("check_interval_seconds", 60),
                        data.get("failure_threshold", 3),
                        target_id,
                    ),
                )

                connection.commit()
                return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def deactivate_target(self, target_id: int) -> bool:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE monitoring_targets
                    SET is_active = FALSE
                    WHERE id = %s;
                    """,
                    (target_id,),
                )

                connection.commit()
                return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()


target_repository = TargetRepository()