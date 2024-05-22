import logging
from colorist import Color, BrightColor


class MyLoggerFormatter(logging.Formatter):

    format = "(%(asctime)s) %(message)s"

    FORMATS = {
        logging.DEBUG: Color.DEFAULT + format + Color.OFF,
        logging.INFO: Color.DEFAULT + format + Color.OFF,
        logging.WARNING: Color.YELLOW + format + Color.OFF,
        logging.ERROR: Color.RED + format + Color.OFF,
        logging.CRITICAL: BrightColor.RED + format + Color.OFF,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
