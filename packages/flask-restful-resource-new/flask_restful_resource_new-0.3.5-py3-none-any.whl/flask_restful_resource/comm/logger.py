#!usr/bin/env python
# coding=utf-8
"""
@author: holens
@time: 2018/09/02
@desc: 线程安全的logger
"""
import logging
import logging.handlers

logger_dict = {}

CONSOLE_FORMAT = "%(asctime)s | %(levelname)s | %(lineno)s | %(funcName)s | %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name, level=logging.INFO, fmt=CONSOLE_FORMAT, datefmt=DATEFMT):
    """
    返回一个logger对象
    :param name:
    :return:logger对象
    """
    # 判断logger对象是否存在
    if name in logger_dict:
        return logger_dict[name]

    logger = logging.getLogger(name)

    logger.setLevel(level)
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    logger.addHandler(console_handler)

    # 字典保存logger对象
    logger_dict[name] = logger

    logging.basicConfig(level=level, handlers=[console_handler])
    logger.propagate = False
    return logger
