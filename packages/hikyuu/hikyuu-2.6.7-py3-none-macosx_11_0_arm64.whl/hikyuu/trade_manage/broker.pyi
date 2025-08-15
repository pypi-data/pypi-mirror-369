from __future__ import annotations
import hikyuu.cpp.core310
from hikyuu.cpp.core310 import OrderBrokerBase
from hikyuu.util.mylog import hku_error
import json as json
__all__ = ['OrderBrokerBase', 'OrderBrokerWrap', 'TestOrderBroker', 'crtOB', 'hku_error', 'json']
class OrderBrokerWrap(hikyuu.cpp.core310.OrderBrokerBase):
    """
    订单代理包装类，用户可以参考自定义自己的订单代理，加入额外的处理
           包装只有买卖操作参数只有(code, price, num)的交易接口类
        
    """
    def __init__(self, broker, name):
        """
        
                订单代理包装类，用户可以参考自定义自己的订单代理，加入额外的处理
                
        """
    def _buy(self, datetime, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        """
        
                实现 OrderBrokerBase 的 _buy 接口
                :param str market: 证券市场    
                :param str code: 证券代码
                :param float price: 买入价格
                :param int num: 买入数量        
                
        """
    def _get_asset_info(self):
        ...
    def _sell(self, datetime, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        """
        实现 OrderBrokerBase 的 _sell 接口
        """
class TestOrderBroker:
    """
    用于测试的订单代理，仅在执行买入/卖出时打印信息
    """
    def __init__(self):
        ...
    def buy(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        ...
    def sell(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        ...
def crtOB(broker, name = 'NO_NAME'):
    """
    
        快速生成订单代理包装对象
    
        :param broker: 订单代理示例，必须拥有buy和sell方法，并且参数为 code, price, num
        :param float slip: 如果当前的卖一价格和指示买入的价格绝对差值不超过slip则下单，
                            否则忽略; 对卖出操作无效，立即以当前价卖出
        
    """
