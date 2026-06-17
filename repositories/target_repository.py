from repositories.database import database_manager


class TargetRepository:
    def create_target(self, target_data: dict) -> int:
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
                        failure_threshold,
                        consecutive_failures,
                        is_active
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        target_data["user_id"],
                        target_data["name"],
                        target_data["url"],
                        target_data.get("expected_status", 200),
                        target_data.get("timeout_seconds", 5),
                        target_data.get("max_response_time_ms", 1000),
                        target_data.get("check_interval_seconds", 60),
                        target_data.get("failure_threshold", 3),
                        target_data.get("consecutive_failures", 0),
                        target_data.get("is_active", True),
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
                    SELECT
                        id,
                        user_id,
                        name,
                        url,
                        expected_status,
                        timeout_seconds,
                        max_response_time_ms,
                        check_interval_seconds,
                        failure_threshold,
                        consecutive_failures,
                        is_active,
                        created_at,
                        updated_at
                    FROM monitoring_targets
                    ORDER BY id;
                    """
                )

                return cursor.fetchall()

        finally:
            connection.close()

    def get_active_targets(self) -> list[dict]:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        name,
                        url,
                        expected_status,
                        timeout_seconds,
                        max_response_time_ms,
                        check_interval_seconds,
                        failure_threshold,
                        consecutive_failures,
                        is_active,
                        created_at,
                        updated_at
                    FROM monitoring_targets
                    WHERE is_active = TRUE
                    ORDER BY id;
                    """
                )

                return cursor.fetchall()

        finally:
            connection.close()

    def get_target_by_id(self, target_id: int) -> dict | None:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        name,
                        url,
                        expected_status,
                        timeout_seconds,
                        max_response_time_ms,
                        check_interval_seconds,
                        failure_threshold,
                        consecutive_failures,
                        is_active,
                        created_at,
                        updated_at
                    FROM monitoring_targets
                    WHERE id = %s;
                    """,
                    (target_id,),
                )

                return cursor.fetchone()

        finally:
            connection.close()

    def update_target(self, target_id: int, target_data: dict) -> bool:
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
                        failure_threshold = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        target_data["name"],
                        target_data["url"],
                        target_data.get("expected_status", 200),
                        target_data.get("timeout_seconds", 5),
                        target_data.get("max_response_time_ms", 1000),
                        target_data.get("check_interval_seconds", 60),
                        target_data.get("failure_threshold", 3),
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
                    SET
                        is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP
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

    def update_consecutive_failures(self, target_id: int, value: int) -> bool:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE monitoring_targets
                    SET
                        consecutive_failures = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (value, target_id),
                )

                connection.commit()
                return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def increment_consecutive_failures(self, target_id: int) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE monitoring_targets
                    SET
                        consecutive_failures = consecutive_failures + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (target_id,),
                )

                cursor.execute(
                    """
                    SELECT consecutive_failures
                    FROM monitoring_targets
                    WHERE id = %s;
                    """,
                    (target_id,),
                )

                row = cursor.fetchone()

                connection.commit()

                return row["consecutive_failures"]

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def reset_consecutive_failures(self, target_id: int) -> bool:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE monitoring_targets
                    SET
                        consecutive_failures = 0,
                        updated_at = CURRENT_TIMESTAMP
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