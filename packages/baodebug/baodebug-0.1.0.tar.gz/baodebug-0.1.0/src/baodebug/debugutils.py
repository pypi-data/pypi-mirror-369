import logging
import cv2
import os
import shutil


def SetDebugPath(debug_path):
    if os.path.exists(debug_path):
        shutil.rmtree(debug_path)
    os.makedirs(debug_path, exist_ok=False)
    os.environ['DEBUG_PATH'] = debug_path


logLevelMap = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


class ColorFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    green = "\x1b[32;20m"    
    cyan = "\x1b[36;20m"
    blue = "\x1b[34;20m"
    red = "\x1b[31;20m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - (%(filename)s:%(lineno)d): %(message)s"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: cyan + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def ConfigureRootLogger(logLevel):
    """
    configure the root logger formats and handlers.
    """
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logLevelMap[logLevel.lower()])

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logLevelMap[logLevel.lower()])
    consoleFormatter = ColorFormatter()
    consoleHandler.setFormatter(consoleFormatter)

    rootLogger.addHandler(consoleHandler)
    
    rootLogger.critical("(set up root logger..)")


def dump_image(image, path):
    cv2.imwrite(path, image)
