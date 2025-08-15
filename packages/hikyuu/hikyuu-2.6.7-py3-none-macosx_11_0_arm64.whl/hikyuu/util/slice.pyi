from __future__ import annotations
__all__ = ['list_getitem']
def list_getitem(data, i):
    """
    对C++引出的vector，实现python的切片，
           将引入的vector类的__getitem__函数覆盖即可。
        
    """
