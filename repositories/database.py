import pymysql
from pymysql.cursors import DictCursor

from config.settings import settings


class DatabaseManager:
    def get_connection(self):
        return pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursorclass=DictCursor,
            autocommit=False,
        )

    def test_connection(self) -> bool:
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok;")
                result = cursor.fetchone()
                return result["ok"] == 1
        finally:
            connection.close()


database_manager = DatabaseManager()