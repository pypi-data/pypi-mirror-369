from __future__ import annotations
import asyncio as asyncio
import functools as functools
import logging
import multiprocessing.synchronize
import sys as sys
import traceback as traceback
__all__ = ['HKUCheckError', 'HKUIngoreError', 'asyncio', 'checkif', 'functools', 'g_hku_logger_lock', 'get_exception_info', 'hku_catch', 'hku_check', 'hku_check_ignore', 'hku_check_throw', 'hku_logger', 'hku_run_ignore_exception', 'hku_to_async', 'sys', 'traceback']
class HKUCheckError(Exception):
    def __init__(self, expression, message):
        ...
    def __str__(self):
        ...
class HKUIngoreError(Exception):
    def __init__(self, expression, message = None):
        ...
    def __str__(self):
        ...
def checkif(expression, message, excepion = None, **kwargs):
    """
    如果 expression 为 True，则抛出异常。注意：该函数的判定和 assert 是相反的。
    
        :param boolean expression: 判断条件
        :param str message: 异常注解信息
        :param Exception exception: 指定的异常类，为None时，为默认 HKUCheckError 异常
        
    """
def get_exception_info():
    ...
def hku_catch(ret = None, trace = False, callback = None, retry = 1, with_msg = False, re_raise = False):
    """
    捕获发生的异常, 包装方式: @hku_catch()
        :param ret: 异常发生时返回值, with_msg为True时, 返回为 (ret, errmsg)
        :param boolean trace: 打印异常堆栈信息
        :param func callback: 发生异常后的回调函数, 入参同func
        :param int retry: 尝试执行的次数
        :param boolean with_msg: 是否返回异常错误信息, 为True时, 函数返回为 (ret, errmsg)
        :param boolean re_raise: 是否将错误信息以异常的方式重新抛出
        
    """
def hku_check(exp, msg, *args, **kwargs):
    ...
def hku_check_ignore(exp, *args, **kwargs):
    """
    可忽略的检查
    """
def hku_check_throw(expression, message, excepion = None, **kwargs):
    """
    如果 expression 为 False，则抛出异常。
    
        :param boolean expression: 判断条件
        :param str message: 异常注解信息
        :param Exception exception: 指定的异常类，为None时，为默认 HKUCheckError 异常
        
    """
def hku_run_ignore_exception(func, *args, **kwargs):
    """
    运行函数并忽略异常
    """
def hku_to_async(func):
    ...
g_hku_logger_lock: multiprocessing.synchronize.Lock  # value = <Lock(owner=None)>
hku_logger: logging.Logger  # value = <Logger hikyuu (INFO)>
