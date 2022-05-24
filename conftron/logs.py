import logging

import structlog


def set_logging_configuration(log_level: int = logging.ERROR):
    logging.basicConfig()
    logging.getLogger().setLevel(log_level)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.threadlocal.merge_threadlocal,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str, *args, **kwargs):
    return structlog.get_logger(name, *args, **kwargs)
