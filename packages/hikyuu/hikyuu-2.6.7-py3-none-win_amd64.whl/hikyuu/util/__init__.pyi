from __future__ import annotations
import asyncio as asyncio
import ctypes as ctypes
import functools as functools
from hikyuu.util.check import HKUCheckError
from hikyuu.util.check import HKUIngoreError
from hikyuu.util.check import checkif
from hikyuu.util.check import get_exception_info
from hikyuu.util.check import hku_catch
from hikyuu.util.check import hku_check
from hikyuu.util.check import hku_check_ignore
from hikyuu.util.check import hku_check_throw
from hikyuu.util.check import hku_run_ignore_exception
from hikyuu.util.check import hku_to_async
from hikyuu.util.mylog import LoggingContext
from hikyuu.util.mylog import add_class_logger_handler
from hikyuu.util.mylog import capture_multiprocess_all_logger
from hikyuu.util.mylog import class_logger
from hikyuu.util.mylog import get_default_logger
from hikyuu.util.mylog import hku_benchmark
from hikyuu.util.mylog import hku_debug as hku_trace
from hikyuu.util.mylog import hku_debug
from hikyuu.util.mylog import hku_debug_if as hku_trace_if
from hikyuu.util.mylog import hku_debug_if
from hikyuu.util.mylog import hku_error
from hikyuu.util.mylog import hku_error_if
from hikyuu.util.mylog import hku_fatal
from hikyuu.util.mylog import hku_fatal_if
from hikyuu.util.mylog import hku_info
from hikyuu.util.mylog import hku_info_if
from hikyuu.util.mylog import hku_warn
from hikyuu.util.mylog import hku_warn_if
from hikyuu.util.mylog import set_my_logger_file
from hikyuu.util.mylog import spend_time
from hikyuu.util.mylog import with_trace
from hikyuu.util.notebook import in_interactive_session
from hikyuu.util.notebook import in_ipython_frontend
from hikyuu.util.timeout import TerminableThread
from hikyuu.util.timeout import ThreadKiller
from hikyuu.util.timeout import timeout
import logging as logging
import multiprocessing as multiprocessing
import os as os
import sys as sys
import threading as threading
import time as time
import traceback as traceback
from . import check
from . import mylog
from . import notebook
from . import singleton
__all__: list = ['spend_time', 'hku_benchmark', 'timeout', 'hku_logger', 'class_logger', 'add_class_logger_handler', 'HKUCheckError', 'hku_check', 'hku_check_throw', 'hku_check_ignore', 'hku_catch', 'hku_to_async', 'hku_run_ignore_exception', 'hku_trace', 'hku_debug', 'hku_info', 'hku_warn', 'hku_error', 'hku_fatal', 'hku_trace_if', 'hku_debug_if', 'hku_info_if', 'hku_warn_if', 'hku_info_if', 'hku_warn_if', 'hku_error_if', 'hku_fatal_if', 'with_trace', 'set_my_logger_file', 'capture_multiprocess_all_logger', 'LoggingContext', 'in_interactive_session', 'in_ipython_frontend']
FORMAT: str = '%(asctime)-15s [%(levelname)s] %(message)s [%(name)s::%(funcName)s]'
g_hku_logger_lock: multiprocessing.synchronize.Lock  # value = <Lock(owner=None)>
hku_logger: logging.Logger  # value = <Logger hikyuu (INFO)>
hku_logger_name: str = 'hikyuu'
