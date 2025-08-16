import logging
import sys


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[97m",  # White
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[1;31m"  # Dark Red (Bold Red)
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        return f"{color}{record.getMessage()}{self.RESET}"


def setup_logging(level: int | str | None):
    logging.basicConfig(level=level)

    if str(level).upper() != "DEBUG" and level != logging.DEBUG:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter())
        logging.getLogger().handlers = [handler]
