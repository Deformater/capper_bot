from decouple import config


TOKEN = config("TOKEN", cast=str)

DB_USER = config("POSTGRES_USER", cast=str)
DB_NAME = config("POSTGRES_DB", cast=str)
DB_PASS = config("POSTGRES_PASSWORD", cast=str)
DB_HOST = config("POSTGRES_SERVER", cast=str)
DB_PORT = config("POSTGRES_PORT", cast=int)

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["data.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}


DB_HOST_DEV = config("POSTGRES_SERVER_DEV", cast=str)
DB_PORT_DEV = config("POSTGRES_PORT_DEV", cast=int)

TORTOISE_ORM_DEV = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST_DEV}:{DB_PORT_DEV}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["data.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

REDIS_HOST = config("REDIS_HOST", cast=str)
REDIS_PORT = config("REDIS_PORT", cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", cast=str)

ADMIN_IDS = list(map(int, config("ADMIN_IDS", cast=str).split(',')))
GROUP_ID = config("GROUP_ID", cast=int)
GROUP_NAME = config("GROUP_NAME", cast=str)