import logging
import sys

app_formatter = logging.Formatter(
    "%(asctime)s [APP] [%(levelname)s] %(name)s - %(message)s "
)
rmq_formatter = logging.Formatter(
    "%(asctime)s [RMQ_WORKER] [%(levelname)s] %(name)s - %(message)s "
)

app_handler = logging.StreamHandler(sys.stdout)
app_handler.setFormatter(app_formatter)

rmq_handler = logging.StreamHandler(sys.stdout)
rmq_handler.setFormatter(rmq_formatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
logger.addHandler(app_handler)
logger.propagate = False

rmq_logger = logging.getLogger("rmq_logger")
rmq_logger.setLevel(logging.INFO)
rmq_logger.addHandler(rmq_handler)
logger.propagate = False
