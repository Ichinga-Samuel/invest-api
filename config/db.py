from .env import env

TORTOISE_ORM = {
    "connections": {
        "staging": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": env.DB_HOST,
                "user": env.DB_USER,
                "port": env.DB_PORT,
                "password": env.DB_PASSWORD,
                "database": env.DB_NAME,
                "ssl": False
            }
        },
    },
    "apps": {
        "models": {
            "models": ["models.user", "models.account", "models.admin", "aerich.models"],
            "default_connection": "staging"
        }
    },
    "use_tz": False,
    "timezone": env.DB_TIMEZONE
}
