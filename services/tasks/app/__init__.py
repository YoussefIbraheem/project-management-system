import logging
from logging.config import dictConfig

from flask import Flask
from flask_jwt_extended import JWTManager

from .core.config import Settings

settings = Settings.get_instance()
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)-15s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": settings.LOGGING_LEVEL,
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "root": {"level": settings.LOGGING_LEVEL, "handlers": ["console"]},
    }
)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    # info and debug print on console and higher level logs to file

    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    JWTManager(app)

    from shared.exceptions import register_error_handlers

    register_error_handlers(app)

    from .apis.project_api import project_bp

    app.register_blueprint(project_bp)

    from .apis.board_api import board_bp

    app.register_blueprint(board_bp)

    from .apis.task_api import task_bp

    app.register_blueprint(task_bp)

    return app
