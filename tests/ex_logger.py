import logging
from . import util

def _generate_log(path):
    """
    Create a logger object
    :param path: Path of the log file.
    :return: Logger object.
    """
    # Create a logger and set the level.
    logger = logging.getLogger('LogError')
    logger.setLevel(logging.ERROR)

    # Create file handler, log format and add the format to file handler
    file_handler = logging.FileHandler(str(path))

    # See https://docs.python.org/3/library/logging.html#logrecord-attributes
    # for log format attributes.
    log_format = '%(levelname)s START\n%(message)s\n%(levelname)s END'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

_log_path = util.get_project_root_dir()
_log_path = _log_path / 'tmp' / 'test.log'

test_logger = _generate_log(_log_path)


def clear_log():
    global _log_path
    with open(_log_path, 'w'):
        # do nothing
        pass

def get_logged_errors() -> list:
    global _log_path
    start = 'ERROR START\n'
    end = 'ERROR END\n'
    read_line = True
    append = False
    i = -1
    match_list = []
    with open(_log_path, "r") as file:
        for line in file:
            if line == start:
                append = True
                match_list.append([])
                i += 1
                continue
            if line == end:
                append = False
                continue
            if append == True:
                match_list[i].append(line.rstrip())
    file.close()
    return match_list
