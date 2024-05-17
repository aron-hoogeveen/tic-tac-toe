import threading
import time
import logging
import concurrent.futures


_COLOR_CODES = {
    "reset": "\u001B[0m",  # reset
    "blue": "\u001B[34m"  # blue
}


my_var = 0
_lock = threading.Lock()


def info_log(id: str, msg: str) -> None:
    logging.info(f"{_COLOR_CODES['blue']}{id}{_COLOR_CODES['reset']}    : {msg}")


def my_thread_function(name: str):
    global my_var, _lock
    info_log(f"{name}", f"Hello, I am thread {name}.")
    with _lock:
        my_var += 1
    time.sleep(1)
    info_log(f"{name}", "Closing.")


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    
    info_log("Main", "Start of the program.")

    # info_log("Main", f"Value of my_var before threads: {my_var}.")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(my_thread_function, ["Epic Thread", "Mega Thread"])

    # info_log("Main", f"Value of my_var after threads: {my_var}.")

    info_log("Main", "End of the program.")