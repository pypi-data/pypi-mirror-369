from __future__ import annotations
import functools as functools
import logging as logging
import multiprocessing as multiprocessing
import os as os
import time as time
import traceback as traceback
__all__ = ['FORMAT', 'LoggingContext', 'add_class_logger_handler', 'capture_multiprocess_all_logger', 'class_logger', 'functools', 'g_hku_logger_lock', 'get_default_logger', 'hku_benchmark', 'hku_debug', 'hku_debug_if', 'hku_error', 'hku_error_if', 'hku_fatal', 'hku_fatal_if', 'hku_info', 'hku_info_if', 'hku_logger', 'hku_logger_name', 'hku_trace', 'hku_trace_if', 'hku_warn', 'hku_warn_if', 'logging', 'multiprocessing', 'os', 'set_my_logger_file', 'spend_time', 'time', 'traceback', 'with_trace']
class LoggingContext:
    def __enter__(self):
        ...
    def __exit__(self, et, ev, tb):
        ...
    def __init__(self, logger, level = None, handler = None, close = True):
        ...
def add_class_logger_handler(class_list, level = 20, handler = None):
    """
    为指定的类增加日志 handler，并设定级别
    
        :param class_list: 类列表
        :param level: 日志级别
        :param handler: logging handler
        
    """
def capture_multiprocess_all_logger(queue, level = None):
    """
    重设所有子进程中的 logger 输出指定的 queue，并重设level
    
        @param multiprocessing.Queue queue 指定的 mp Queue
        @param level 日志输出等级, None为保持原有等级
        
    """
def class_logger(cls, enable = False):
    ...
def get_default_logger():
    ...
def hku_benchmark(count = 10):
    ...
def hku_debug(msg, *args, **kwargs):
    ...
def hku_debug_if(exp, msg, *args, **kwargs):
    ...
def hku_error(msg, *args, **kwargs):
    ...
def hku_error_if(exp, msg, *args, **kwargs):
    ...
def hku_fatal(msg, *args, **kwargs):
    ...
def hku_fatal_if(exp, msg, *args, **kwargs):
    ...
def hku_info(msg, *args, **kwargs):
    ...
def hku_info_if(exp, msg, *args, **kwargs):
    ...
def hku_warn(msg, *args, **kwargs):
    ...
def hku_warn_if(exp, msg, *args, **kwargs):
    ...
def set_my_logger_file(file_name):
    ...
def spend_time(func):
    ...
def with_trace(level = 20):
    ...
FORMAT: str = '%(asctime)-15s [%(levelname)s] %(message)s [%(name)s::%(funcName)s]'
_logfile: logging.handlers.RotatingFileHandler  # value = <RotatingFileHandler /Users/fasiondog/.hikyuu/hikyuu_py.log (WARNING)>
_usrdir: str = '/Users/fasiondog'
g_hku_logger_lock: multiprocessing.synchronize.Lock  # value = <Lock(owner=unknown)>
hku_logger: logging.Logger  # value = <Logger hikyuu (INFO)>
hku_logger_name: str = 'hikyuu'
hku_trace = hku_debug
hku_trace_if = hku_debug_if
