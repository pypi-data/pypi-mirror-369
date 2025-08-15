from __future__ import annotations
from hikyuu.cpp.core310 import ConditionBase
from hikyuu.cpp.core310 import EnvironmentBase
from hikyuu.cpp.core310 import Indicator
from hikyuu.cpp.core310 import KData
from hikyuu.cpp.core310 import Portfolio
from hikyuu.cpp.core310 import SignalBase
from hikyuu.cpp.core310 import System
from hikyuu.cpp.core310 import TradeManager
from hikyuu.draw.drawplot.bokeh_draw import ax_draw_macd as bk_ax_draw_macd
from hikyuu.draw.drawplot.bokeh_draw import ax_draw_macd2 as bk_ax_draw_macd2
from hikyuu.draw.drawplot.bokeh_draw import create_figure as bk_create_figure
from hikyuu.draw.drawplot.bokeh_draw import gca as bk_gca
from hikyuu.draw.drawplot.bokeh_draw import gcf as bk_gcf
from hikyuu.draw.drawplot.bokeh_draw import ibar as bk_ibar
from hikyuu.draw.drawplot.bokeh_draw import iplot as bk_iplot
from hikyuu.draw.drawplot.bokeh_draw import kplot as bk_kplot
from hikyuu.draw.drawplot.bokeh_draw import sgplot as bk_sgplot
from hikyuu.draw.drawplot.bokeh_draw import show_gcf as bk_show_gcf
from hikyuu.draw.drawplot.bokeh_draw import use_bokeh_in_notebook
from hikyuu.draw.drawplot.echarts_draw import ibar as ec_ibar
from hikyuu.draw.drawplot.echarts_draw import iplot as ec_iplot
from hikyuu.draw.drawplot.echarts_draw import kplot as ec_kplot
from hikyuu.draw.drawplot.echarts_draw import sys_performance as ec_sys_performance
from hikyuu.draw.drawplot.echarts_draw import sysplot as ec_sysplot
from hikyuu.draw.drawplot.matplotlib_draw import DRAWBAND
from hikyuu.draw.drawplot.matplotlib_draw import DRAWICON
from hikyuu.draw.drawplot.matplotlib_draw import DRAWIMG
from hikyuu.draw.drawplot.matplotlib_draw import DRAWIMG as DRAWBMP
from hikyuu.draw.drawplot.matplotlib_draw import DRAWLINE
from hikyuu.draw.drawplot.matplotlib_draw import DRAWNUMBER
from hikyuu.draw.drawplot.matplotlib_draw import DRAWNUMBER_FIX
from hikyuu.draw.drawplot.matplotlib_draw import DRAWRECTREL
from hikyuu.draw.drawplot.matplotlib_draw import DRAWSL
from hikyuu.draw.drawplot.matplotlib_draw import DRAWTEXT
from hikyuu.draw.drawplot.matplotlib_draw import DRAWTEXT_FIX
from hikyuu.draw.drawplot.matplotlib_draw import PLOYLINE
from hikyuu.draw.drawplot.matplotlib_draw import RGB
from hikyuu.draw.drawplot.matplotlib_draw import SHOWICONS
from hikyuu.draw.drawplot.matplotlib_draw import STICKLINE
from hikyuu.draw.drawplot.matplotlib_draw import adjust_axes_show as mpl_adjust_axes_show
from hikyuu.draw.drawplot.matplotlib_draw import ax_draw_macd as mpl_ax_draw_macd
from hikyuu.draw.drawplot.matplotlib_draw import ax_draw_macd2 as mpl_ax_draw_macd2
from hikyuu.draw.drawplot.matplotlib_draw import ax_set_locator_formatter as mpl_ax_set_locator_formatter
from hikyuu.draw.drawplot.matplotlib_draw import cnplot as mpl_cnplot
from hikyuu.draw.drawplot.matplotlib_draw import create_figure as mpl_create_figure
from hikyuu.draw.drawplot.matplotlib_draw import evplot as mpl_evplot
from hikyuu.draw.drawplot.matplotlib_draw import ibar as mpl_ibar
from hikyuu.draw.drawplot.matplotlib_draw import iheatmap as mpl_iheatmap
from hikyuu.draw.drawplot.matplotlib_draw import iplot as mpl_iplot
from hikyuu.draw.drawplot.matplotlib_draw import kplot as mpl_kplot
from hikyuu.draw.drawplot.matplotlib_draw import mkplot as mpl_mkplot
from hikyuu.draw.drawplot.matplotlib_draw import set_mpl_params
from hikyuu.draw.drawplot.matplotlib_draw import sgplot as mpl_sgplot
from hikyuu.draw.drawplot.matplotlib_draw import sys_heatmap as mpl_sys_heatmap
from hikyuu.draw.drawplot.matplotlib_draw import sys_performance as mpl_sys_performance
from hikyuu.draw.drawplot.matplotlib_draw import sysplot as mpl_sysplot
from hikyuu.draw.drawplot.matplotlib_draw import tm_heatmap as mpl_tm_heatmap
from hikyuu.draw.drawplot.matplotlib_draw import tm_performance as mpl_tm_performance
import matplotlib as matplotlib
from matplotlib.pyplot import gca as mpl_gca
from matplotlib.pyplot import gcf as mpl_gcf
from . import bokeh_draw
from . import common
from . import echarts_draw
from . import matplotlib_draw
__all__: list = ['use_draw_engine', 'get_current_draw_engine', 'create_figure', 'gcf', 'show_gcf', 'gca', 'ax_draw_macd', 'ax_draw_macd2', 'use_bokeh_in_notebook', 'use_draw_with_echarts', 'DRAWNULL', 'STICKLINE', 'DRAWBAND', 'RGB', 'PLOYLINE', 'DRAWLINE', 'DRAWTEXT', 'DRAWNUMBER', 'DRAWTEXT_FIX', 'DRAWNUMBER_FIX', 'DRAWSL', 'DRAWIMG', 'DRAWICON', 'DRAWBMP', 'SHOWICONS', 'DRAWRECTREL']
def adjust_axes_show(axeslist):
    """
    用于调整上下紧密相连的坐标轴显示时，其上一坐标轴最小值刻度和下一坐标轴最大值刻度
        显示重叠的问题。
    
        :param axeslist: 上下相连的坐标轴列表 (ax1,ax2,...)
        
    """
def ax_draw_macd(axes, kdata, n1 = 12, n2 = 26, n3 = 9):
    """
    绘制MACD
    
        :param axes: 指定的坐标轴
        :param KData kdata: KData
        :param int n1: 指标 MACD 的参数1
        :param int n2: 指标 MACD 的参数2
        :param int n3: 指标 MACD 的参数3
        
    """
def ax_draw_macd2(axes, ref, kdata, n1 = 12, n2 = 26, n3 = 9):
    """
    绘制MACD。
        当BAR值变化与参考序列ref变化不一致时，显示为灰色，
        当BAR和参考序列ref同时上涨，显示红色
        当BAR和参考序列ref同时下跌，显示绿色
    
        :param axes: 指定的坐标轴
        :param ref: 参考序列，EMA
        :param KData kdata: KData
        :param int n1: 指标 MACD 的参数1
        :param int n2: 指标 MACD 的参数2
        :param int n3: 指标 MACD 的参数3
        
    """
def ax_set_locator_formatter(axes, dates, typ):
    """
     设置指定坐标轴的日期显示，根据指定的K线类型优化X轴坐标显示
    
        :param axes: 指定的坐标轴
        :param dates: Datetime构成可迭代序列
        :param Query.KType typ: K线类型
        
    """
def create_figure(n = 1, figsize = None):
    """
    生成含有指定坐标轴数量的窗口，最大只支持4个坐标轴。
    
        :param int n: 坐标轴数量
        :param figsize: (宽, 高)
        :return: (ax1, ax2, ...) 根据指定的坐标轴数量而定，超出[1,4]个坐标轴时，返回None
        
    """
def gca():
    ...
def gcf():
    ...
def get_current_draw_engine():
    ...
def set_current_draw_engine(engine):
    ...
def show_gcf():
    ...
def use_draw_engine(engine = 'matplotlib'):
    ...
def use_draw_with_bokeh():
    ...
def use_draw_with_echarts():
    ...
def use_draw_with_matplotlib():
    ...
DRAWNULL: float  # value = nan
g_draw_engine: str = 'matplotlib'
