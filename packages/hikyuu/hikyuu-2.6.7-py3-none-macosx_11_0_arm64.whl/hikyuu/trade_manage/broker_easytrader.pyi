from __future__ import annotations
from hikyuu.cpp.core310 import Datetime
from hikyuu.util.mylog import hku_info
__all__ = ['Datetime', 'EasyTraderOrderBroker', 'hku_info']
class EasyTraderOrderBroker:
    """
    
        使用华泰客户端实例
        注意：buy|sell 中已屏蔽实际通过easytrade下单，防止调试误操作，请自行根据需要打开
        
    """
    def __init__(self, user):
        ...
    def buy(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        ...
    def get_asset_info(self):
        """
        以下只适用于华泰
        """
    def sell(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        ...
