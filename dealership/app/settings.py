import os


class Settings:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_TIME_TO_EXPIRE = int(os.getenv("JWT_TOKEN_TIME_TO_EXPIRE"))
    JWT_REFRESH_TOKEN_TIME_TO_EXPIRE = int(
        os.getenv("JWT_REFRESH_TOKEN_TIME_TO_EXPIRE")
    )
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PWD = os.getenv("MYSQL_PWD")
    MYSQL_DEFAULT_DB = os.getenv("MYSQL_DEFAULT_DB")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    APP_HOST = os.getenv("APP_HOST")
    APP_PORT = int(os.getenv("APP_PORT"))
