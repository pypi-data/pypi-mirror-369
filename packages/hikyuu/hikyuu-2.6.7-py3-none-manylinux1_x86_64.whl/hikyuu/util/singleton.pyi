from __future__ import annotations
import threading as threading
import typing
__all__ = ['SingletonType', 'threading']
class SingletonType(type):
    """
    基于 metalclass 实现单例
    
        示例：
        class MyClass(metaclass=SingletonType):
            def __init__(self,name):
                self.name = name
        
    """
    _instance_lock: typing.ClassVar[_thread.lock]  # value = <unlocked _thread.lock object at 0x77b147485840>
    @classmethod
    def __call__(cls, *args, **kwargs):
        ...
