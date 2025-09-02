import logging
import os

# custom logger
logger = logging.getLogger("KJ-LOGGER")
logger.setLevel(logging.DEBUG)

# Creating a logs directory
os.makedirs("logs", exist_ok=True)

# Console Handler (Docker logs)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# File Handler
file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.DEBUG)


# Common Formatter
formatter = logging.Formatter(
    "%(levelname)s:     [%(asctime)s]  [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add Handlers
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.propagate = False
