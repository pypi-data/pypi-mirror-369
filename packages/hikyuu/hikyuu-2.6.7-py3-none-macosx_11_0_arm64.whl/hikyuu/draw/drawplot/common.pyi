from __future__ import annotations
from hikyuu.cpp.core310 import Query
__all__ = ['Query', 'get_draw_title']
def get_draw_title(kdata):
    """
    根据typ值，返回相应的标题，如 上证指数（日线）
        参数：kdata: KData实例
        返回：一个包含stock名称的字符串，可用作绘图时的标题
        
    """
