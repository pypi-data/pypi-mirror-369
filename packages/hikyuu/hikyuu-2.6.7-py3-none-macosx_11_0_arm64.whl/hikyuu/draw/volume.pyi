"""

绘制普通K线图 + 成交量（成交金额）
"""
from __future__ import annotations
import hikyuu.cpp.core310
from hikyuu.cpp.core310 import Indicator
from hikyuu.cpp.core310 import Query
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import CVAL
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import IF
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import MA
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import PRICELIST
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import SG_Cross
from hikyuu.draw.drawplot import adjust_axes_show
from hikyuu.draw.drawplot import ax_draw_macd
from hikyuu.draw.drawplot import ax_set_locator_formatter
from hikyuu.draw.drawplot import create_figure
from hikyuu.draw.drawplot import get_current_draw_engine
from hikyuu.draw.drawplot import show_gcf
from hikyuu.util.mylog import spend_time
__all__ = ['CLOSE', 'CVAL', 'IF', 'Indicator', 'MA', 'PRICELIST', 'Query', 'SG_Cross', 'VOL', 'adjust_axes_show', 'ax_draw_macd', 'ax_set_locator_formatter', 'create_figure', 'draw', 'draw2', 'get_current_draw_engine', 'show_gcf', 'spend_time']
def draw(stock, query = ..., ma1_n = 5, ma2_n = 10, ma3_n = 20, ma4_n = 60, ma5_n = 100, vma1_n = 5, vma2_n = 10):
    """
    绘制普通K线图 + 成交量（成交金额）
    """
def draw2(stock, query = ..., ma1_n = 7, ma2_n = 20, ma3_n = 30, ma4_n = 42, ma5_n = 100, vma1_n = 5, vma2_n = 10):
    """
    绘制普通K线图 + 成交量（成交金额）+ MACD
    """
CLOSE: hikyuu.cpp.core310.Indicator  # value = Indicator{...
VOL: hikyuu.cpp.core310.Indicator  # value = Indicator{...
