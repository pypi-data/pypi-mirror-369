"""

绘制亚历山大.艾尔德交易系统图形
参见：《走进我的交易室》（2007年 地震出版社） Alexander Elder
"""
from __future__ import annotations
import hikyuu.cpp.core310
from hikyuu.cpp.core310 import Indicator
from hikyuu.cpp.core310 import Query
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import CVAL
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import EMA
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import MACD
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import PRICELIST
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import SAFTYLOSS
from hikyuu.cpp.core310.pybind11_detail_function_record_v1_system_libcpp_abi1 import VIGOR
from hikyuu.draw.drawplot import adjust_axes_show
from hikyuu.draw.drawplot import ax_draw_macd2
from hikyuu.draw.drawplot import ax_set_locator_formatter
from hikyuu.draw.drawplot import create_figure
from hikyuu.draw.drawplot import show_gcf
from matplotlib.pyplot import plot
from numpy import mean
__all__ = ['CLOSE', 'CVAL', 'EMA', 'Indicator', 'MACD', 'PRICELIST', 'Query', 'SAFTYLOSS', 'VIGOR', 'adjust_axes_show', 'ax_draw_macd2', 'ax_set_locator_formatter', 'constant', 'create_figure', 'draw', 'mean', 'plot', 'show_gcf']
def _draw_ema_pipe(axes, kdata, ema, n = 22, w = 0.1):
    ...
def _find_ema_coefficient(closes, emas, number = 66, percent = 0.95):
    """
    计算EMA通道系数。
        在《走进我的交易室》中，艾尔德介绍的价格通道为：
            通道上轨 ＝ EMA ＋ EMA＊通道系数
            通道下轨 ＝ EMA － EMA＊通道系数
        其中一条绘制得恰到好处的通道应能将绝大多数价格包含在内，一般调节通道系数使其能够包含95％的价格
        参数：closes：收盘价序列
              emas：收盘价对应的EMA序列
              number: 以最近多少天的数据来计算，即取最后N天的数据作为计算标准
              percent：通道包含多少的价格，如0.95表示通道将包含95%的价格
        
    """
def draw(stock, query = ..., ma_n = 22, ma_w = 'auto', vigor_n = 13):
    """
    绘制亚历山大.艾尔德交易系统图形
    """
CLOSE: hikyuu.cpp.core310.Indicator  # value = Indicator{...
constant: hikyuu.cpp.core310.Constant  # value = <hikyuu.cpp.core310.Constant object>
