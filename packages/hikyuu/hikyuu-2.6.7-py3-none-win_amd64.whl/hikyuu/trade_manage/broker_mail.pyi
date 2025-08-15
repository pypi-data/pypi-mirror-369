from __future__ import annotations
from email.header import Header
from email.mime.text import MIMEText
import smtplib as smtplib
__all__ = ['Header', 'MIMEText', 'MailOrderBroker', 'smtplib']
class MailOrderBroker:
    """
    
        邮件订单代理
        
    """
    def __init__(self, host, sender, pwd, receivers):
        """
        
                邮件订单代理，执行买入/卖出操作时发送 Email
        
                :param str host: smtp服务器地址
                :param int port: smtp服务器端口
                :param str sender: 发件邮箱（既用户名）
                :param str pwd: 密码
                :param list receivers: 接受者邮箱列表
                
        """
    def _sendmail(self, title, msg):
        """
        发送邮件
        
                :param str title: 邮件标题
                :param str msg: 邮件内容
                
        """
    def buy(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        """
        执行买入操作，向指定的邮箱发送邮件，格式如下::
        
                    邮件标题：【Hkyuu提醒】买入 证券代码
                    邮件内容：买入：证券代码，价格：买入的价格，数量：买入数量
        
                :param str code: 证券代码
                :param float price: 买入价格
                :param int num: 买入数量
                
        """
    def sell(self, market, code, price, num, stoploss, goal_price, part_from, remark = ''):
        """
        执行卖出操作，向指定的邮箱发送邮件，格式如下::
        
                    邮件标题：【Hkyuu提醒】卖出 证券代码
                    邮件内容：卖出：证券代码，价格：卖出的价格，数量：卖出数量
        
                :param str code: 证券代码
                :param float price: 卖出价格
                :param int num: 卖出数量
                
        """
