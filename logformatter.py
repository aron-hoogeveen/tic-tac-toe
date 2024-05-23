import logging
from colorist import Color, BrightColor


class MyLoggerFormatter(logging.Formatter):

    format = "(%(asctime)s) %(message)s"

    FORMATS = {
        logging.DEBUG: Color.DEFAULT + " --- DEBUG --- " + format + Color.OFF,
        logging.INFO: Color.DEFAULT + " --- INFO --- " + format + Color.OFF,
        logging.WARNING: Color.YELLOW + " --- WARNING --- " + format + Color.OFF,
        logging.ERROR: Color.RED + " --- ERROR --- " + format + Color.OFF,
        logging.CRITICAL: BrightColor.RED + " --- CRITICAL --- " + format + Color.OFF,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
