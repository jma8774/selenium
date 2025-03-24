import logging
from datetime import datetime
import os
from colorama import init, Fore, Style

# Initialize colorama
init()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""

    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        # Add color to the level name
        level_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger():
    # Create a custom logger
    logger = logging.getLogger("log")
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"logs/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8')

    # Set level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create formatters
    console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logger initialized")
    logger.info("--------------------------------")

    return logger

log = setup_logger()
