"""

绘制佩里.J.考夫曼（Perry J.Kaufman） 自适应移动平均系统(AMA)
参见：《精明交易者》（2006年 广东经济出版社） 
"""
from __future__ import annotations
import hikyuu.cpp.core310
from hikyuu.cpp.core310 import Query
from hikyuu.cpp.core310 import StockManager
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import AMA
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import CVAL
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import EMA
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import POS
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import PRICELIST
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import RESULT
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import SG_Cross
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import SG_Flex
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import SG_Single
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import STDEV
from hikyuu.draw.drawplot import adjust_axes_show
from hikyuu.draw.drawplot import ax_draw_macd
from hikyuu.draw.drawplot import ax_set_locator_formatter
from hikyuu.draw.drawplot import create_figure
from hikyuu.draw.drawplot import show_gcf
__all__ = ['AMA', 'CLOSE', 'CVAL', 'EMA', 'HIGH', 'KDATA', 'LOW', 'OPEN', 'POS', 'PRICELIST', 'Query', 'RESULT', 'SG_Cross', 'SG_Flex', 'SG_Single', 'STDEV', 'StockManager', 'adjust_axes_show', 'ax_draw_macd', 'ax_set_locator_formatter', 'create_figure', 'draw', 'draw2', 'show_gcf']
def draw(stock, query = ..., n = 10, filter_n = 20, filter_p = 0.1, sg_type = 'CROSS', show_high_low = False, arrow_style = 1):
    """
    绘制佩里.J.考夫曼（Perry J.Kaufman） 自适应移动平均系统(AMA)
    """
def draw2(block, query = ..., ama1 = None, ama2 = None, n = 10, filter_n = 20, filter_p = 0.1, sg_type = 'CROSS', show_high_low = True, arrow_style = 1):
    """
    绘制佩里.J.考夫曼（Perry J.Kaufman） 自适应移动平均系统(AMA)
    """
CLOSE: hikyuu.cpp.core310.Indicator  # value = Indicator{...
HIGH: hikyuu.cpp.core310.Indicator  # value = Indicator{...
KDATA: hikyuu.cpp.core310.Indicator  # value = Indicator{...
LOW: hikyuu.cpp.core310.Indicator  # value = Indicator{...
OPEN: hikyuu.cpp.core310.Indicator  # value = Indicator{...
