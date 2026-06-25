# app/logging_config.py

import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging(app):
    """
    Sets up production logging with:
      - RotatingFileHandler  → logs/app.log      (all events)
      - RotatingFileHandler  → logs/security.log (auth events only)
      - StreamHandler        → stdout             (Docker / systemd)

    Called once inside create_app() after the app object exists.
    Does nothing in DEBUG mode — Flask's default console logging is enough.
    """
    if app.debug:
        # In development, Flask's built-in logger is sufficient.
        # Adding handlers here would double every log line.
        return

    os.makedirs('logs', exist_ok=True)

    # ── Log format ────────────────────────────────────────────────
    # Every line: timestamp | level | logger name | message
    fmt = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # ── Main file handler ─────────────────────────────────────────
    # RotatingFileHandler:
    #   maxBytes=10*1024*1024  → rotate when file hits 10 MB
    #   backupCount=10         → keep 10 old files (app.log.1 … app.log.10)
    #                            oldest is deleted when limit is reached
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8',
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)

    # ── Security file handler ─────────────────────────────────────
    # A separate log file that captures ONLY security-relevant events.
    # Auth routes write to the 'security' logger explicitly (see below).
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    security_handler.setFormatter(fmt)
    security_handler.setLevel(logging.WARNING)

    # ── Stdout handler ────────────────────────────────────────────
    # Required for Docker (logs to container stdout) and
    # systemd (journald captures stdout automatically).
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(logging.ERROR)
    # Only errors to stdout — keeps container logs clean.
    # INFO events go to file only.

    # ── Attach handlers to Flask's app logger ─────────────────────
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

    # ── Dedicated security logger ─────────────────────────────────
    # This logger is imported and used directly in auth routes.
    # It writes to security.log independently of app.logger.
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.WARNING)
    security_logger.addHandler(security_handler)
    security_logger.addHandler(file_handler)
    # Also copy security events into app.log for completeness.
    security_logger.propagate = False
    # propagate=False prevents double-logging to the root logger.

    # ── Suppress noisy third-party loggers ───────────────────────
    # These libraries log at INFO constantly — too much noise.
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    app.logger.info('Logging configured — writing to logs/app.log')
