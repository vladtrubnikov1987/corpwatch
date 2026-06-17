from repositories.database import database_manager


class NotificationRepository:
    def create_notification(self, data: dict) -> int:
        connection = database_manager.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO notifications (
                        alert_id,
                        notification_type,
                        recipient_email,
                        subject,
                        body,
                        status,
                        error_message
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        data.get("alert_id"),
                        data["notification_type"],
                        data["recipient_email"],
                        data["subject"],
                        data.get("body"),
                        data["status"],
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


notification_repository = NotificationRepository()