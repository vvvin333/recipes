import json
import logging
import sys

from constants import LOGS_SEPARATOR


def get_logger(name, formatter, log_filename="logfile.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(formatter, log_filename))
    logger.addHandler(get_stream_handler(formatter))
    return logger


def get_file_handler(formatter, log_filename):
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    return file_handler


def get_stream_handler(formatter):
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_app_log(record):
    json_obj = {
        'recipes': {
            'log': {
                'level': record.levelname,
                'type': 'app',
                # datetime without ms
                'timestamp': record.asctime.split(",")[0],
                'msg_template': record.msg,
                'message': record.message
            }
        }
    }

    return json_obj


class CustomFormatter(logging.Formatter):
    def __init__(self, formatter):
        logging.Formatter.__init__(self, formatter)

    def format(self, record):
        logging.Formatter.format(self, record)
        return (
                json.dumps(get_app_log(record), indent=2, ensure_ascii=False,)
                + LOGS_SEPARATOR
        )
