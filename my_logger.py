import logging


_COLOR_CODES = {
    "reset": "\u001B[0m",  # reset
    "blue": "\u001B[34m"  # blue
}


def setup():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")


def info_log(id: str = "INFO", msg: str = "") -> None:
    logging.info(f"{_COLOR_CODES['blue']}{id}{_COLOR_CODES['reset']}    : {msg}")
