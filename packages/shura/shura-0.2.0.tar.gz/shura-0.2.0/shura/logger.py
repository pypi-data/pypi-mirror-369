import logging
import sys
import json
from datetime import datetime
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)


class ShuraFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        fmt = f"{color}[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s{reset}"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class JsonFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name="shura", level=logging.DEBUG, to_file=False, filename="shura.log", file_format="log"):
    """
    Create a Shura logger with optional JSON file output

    Parameters:
    -----------
    name : str
        Logger name (default: "shura")
    level : int
        Logging level (default: logging.DEBUG)
    to_file : bool
        Whether to save logs to file (default: False)
    filename : str
        Log filename (default: "shura.log")
    file_format : str
        File format: "log" or "json" (default: "log")

    Returns:
    --------
    logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console handler with colors
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(ShuraFormatter())
        logger.addHandler(stream_handler)

        # Optional file output
        if to_file:
            file_handler = logging.FileHandler(filename)

            if file_format == "json":
                # JSON format for file
                file_handler.setFormatter(JsonFormatter())
            else:
                # Regular log format for file (default)
                file_handler.setFormatter(logging.Formatter(
                    "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                ))

            logger.addHandler(file_handler)

    return logger