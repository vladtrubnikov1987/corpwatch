from repositories.database import database_manager


class CheckResultRepository:
    def create_check_result(self, data: dict) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO check_results (
                        target_id,
                        status_code,
                        response_time_ms,
                        result_type,
                        error_message
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        data["target_id"],
                        data.get("status_code"),
                        data.get("response_time_ms"),
                        data["result_type"],
                        data.get("error_message"),
                    ),
                )

                connection.commit()
                return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()


check_result_repository = CheckResultRepository()