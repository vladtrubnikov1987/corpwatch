import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    API_KEY = os.getenv("API_KEY", "change_me")

    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "corpwatch")
    DB_USER = os.getenv("DB_USER", "corpwatch_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "corpwatch_password")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")


settings = Settings()