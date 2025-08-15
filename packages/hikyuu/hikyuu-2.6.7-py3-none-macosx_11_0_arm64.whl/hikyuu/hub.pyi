from __future__ import annotations
import errno as errno
from functools import lru_cache
import git as git
from hikyuu.util.check import checkif
from hikyuu.util.mylog import hku_info
from hikyuu.util.singleton import SingletonType
import importlib as importlib
import inspect as inspect
import logging as logging
import os as os
import pathlib as pathlib
import shutil as shutil
import sqlalchemy as sqlalchemy
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.decl_api import Base
from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql._elements_constructors import and_
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import Sequence
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
import stat as stat
import sys as sys
import typing
__all__: list = ['add_remote_hub', 'add_local_hub', 'update_hub', 'remove_hub', 'build_hub', 'help_part', 'get_part', 'get_part_list', 'get_hub_path', 'get_part_info', 'get_part_module', 'print_part_info', 'get_hub_name_list', 'get_part_name_list', 'get_current_hub', 'search_part']
class ConfigModel(sqlalchemy.orm.decl_api.Base):
    __mapper__: typing.ClassVar[sqlalchemy.orm.mapper.Mapper]  # value = <Mapper at 0x1368ba710; ConfigModel>
    __table__: typing.ClassVar[sqlalchemy.sql.schema.Table]  # value = Table('hub_config', MetaData(), Column('id', Integer(), table=<hub_config>, primary_key=True, nullable=False, default=Sequence('config_id_seq', metadata=MetaData())), Column('key', String(), table=<hub_config>), Column('value', String(), table=<hub_config>), schema=None)
    __table_args__: typing.ClassVar[tuple]  # value = (UniqueConstraint(Column('key', String(), table=<hub_config>)))
    __tablename__: typing.ClassVar[str] = 'hub_config'
    _sa_class_manager: typing.ClassVar[sqlalchemy.orm.instrumentation.ClassManager]  # value = <ClassManager of <class 'hikyuu.hub.ConfigModel'> at 1368d4db0>
    def __init__(self, **kwargs):
        """
        A simple constructor that allows initialization from kwargs.
        
            Sets attributes on the constructed instance using the names and
            values in ``kwargs``.
        
            Only keys that are present as
            attributes of the instance's class are allowed. These could be,
            for example, any mapped columns or relationships.
            
        """
    def __repr__(self):
        ...
    def __str__(self):
        ...
class HubManager:
    """
    策略库管理
    """
    _instance: typing.ClassVar[HubManager]  # value = <hikyuu.hub.HubManager object>
    @staticmethod
    def _get_module(*args, **kwargs):
        ...
    @staticmethod
    def add_local_hub(*args, **kwargs):
        ...
    @staticmethod
    def add_remote_hub(*args, **kwargs):
        ...
    @staticmethod
    def build_hub(*args, **kwargs):
        ...
    @staticmethod
    def get_current_hub(*args, **kwargs):
        ...
    @staticmethod
    def get_hub_name_list(*args, **kwargs):
        ...
    @staticmethod
    def get_hub_path(*args, **kwargs):
        ...
    @staticmethod
    def get_part(*args, **kwargs):
        ...
    @staticmethod
    def get_part_info(*args, **kwargs):
        ...
    @staticmethod
    def get_part_module(*args, **kwargs):
        ...
    @staticmethod
    def get_part_name_list(*args, **kwargs):
        ...
    @staticmethod
    def import_part_to_db(*args, **kwargs):
        ...
    @staticmethod
    def remove_hub(*args, **kwargs):
        ...
    @staticmethod
    def search_part(*args, **kwargs):
        ...
    @staticmethod
    def setup_hub(*args, **kwargs):
        ...
    @staticmethod
    def update_hub(*args, **kwargs):
        ...
    def __init__(self):
        ...
    def download_remote_hub(self, local_dir, url, branch):
        ...
    def print_part_info(self, name):
        ...
class HubModel(sqlalchemy.orm.decl_api.Base):
    __mapper__: typing.ClassVar[sqlalchemy.orm.mapper.Mapper]  # value = <Mapper at 0x1368bba00; HubModel>
    __table__: typing.ClassVar[sqlalchemy.sql.schema.Table]  # value = Table('hub_repo', MetaData(), Column('id', Integer(), table=<hub_repo>, primary_key=True, nullable=False, default=Sequence('remote_id_seq', metadata=MetaData())), Column('name', String(), table=<hub_repo>), Column('hub_type', String(), table=<hub_repo>), Column('local_base', String(), table=<hub_repo>), Column('local', String(), table=<hub_repo>), Column('url', String(), table=<hub_repo>), Column('branch', String(), table=<hub_repo>), schema=None)
    __table_args__: typing.ClassVar[tuple]  # value = (UniqueConstraint(Column('name', String(), table=<hub_repo>)))
    __tablename__: typing.ClassVar[str] = 'hub_repo'
    _sa_class_manager: typing.ClassVar[sqlalchemy.orm.instrumentation.ClassManager]  # value = <ClassManager of <class 'hikyuu.hub.HubModel'> at 1368f9580>
    def __init__(self, **kwargs):
        """
        A simple constructor that allows initialization from kwargs.
        
            Sets attributes on the constructed instance using the names and
            values in ``kwargs``.
        
            Only keys that are present as
            attributes of the instance's class are allowed. These could be,
            for example, any mapped columns or relationships.
            
        """
    def __repr__(self):
        ...
    def __str__(self):
        ...
class HubNameRepeatError(Exception):
    def __init__(self, name):
        ...
    def __str__(self):
        ...
class HubNotFoundError(Exception):
    def __init__(self, name):
        ...
    def __str__(self):
        ...
class ModuleConflictError(Exception):
    def __init__(self, hub_name, conflict_module, hub_path):
        ...
    def __str__(self):
        ...
class PartModel(sqlalchemy.orm.decl_api.Base):
    __mapper__: typing.ClassVar[sqlalchemy.orm.mapper.Mapper]  # value = <Mapper at 0x1368bb130; PartModel>
    __table__: typing.ClassVar[sqlalchemy.sql.schema.Table]  # value = Table('hub_part', MetaData(), Column('id', Integer(), table=<hub_part>, primary_key=True, nullable=False, default=Sequence('part_id_seq', metadata=MetaData())), Column('hub_name', String(), table=<hub_part>), Column('part', String(), table=<hub_part>), Column('name', String(), table=<hub_part>), Column('author', String(), table=<hub_part>), Column('version', String(), table=<hub_part>), Column('doc', String(), table=<hub_part>), Column('module_name', String(), table=<hub_part>), Column('label', String(), table=<hub_part>), schema=None)
    __table_args__: typing.ClassVar[tuple]  # value = (UniqueConstraint(Column('name', String(), table=<hub_part>)))
    __tablename__: typing.ClassVar[str] = 'hub_part'
    _sa_class_manager: typing.ClassVar[sqlalchemy.orm.instrumentation.ClassManager]  # value = <ClassManager of <class 'hikyuu.hub.PartModel'> at 132090400>
    def __init__(self, **kwargs):
        """
        A simple constructor that allows initialization from kwargs.
        
            Sets attributes on the constructed instance using the names and
            values in ``kwargs``.
        
            Only keys that are present as
            attributes of the instance's class are allowed. These could be,
            for example, any mapped columns or relationships.
            
        """
    def __repr__(self):
        ...
    def __str__(self):
        ...
class PartNameError(Exception):
    def __init__(self, name):
        ...
    def __str__(self):
        ...
class PartNotFoundError(Exception):
    def __init__(self, name, cause):
        ...
    def __str__(self):
        ...
def add_local_hub(name, path):
    """
    增加本地数据仓库
    
        :param str name: 仓库名称
        :param str path: 本地全路径
        
    """
def add_remote_hub(name, url, branch = 'main'):
    """
    增加远程策略仓库
    
        :param str name: 本地仓库名称（自行起名）
        :param str url: git 仓库地址
        :param str branch: git 仓库分支
        
    """
def build_hub(name, cmd = 'buildall'):
    """
    构建 cpp 部分 part
    
        :param str name: 仓库名称
        :param str cmd: 同仓库下 python setup.py 后的命令参数，如: build -t ind -n cpp_example
        
    """
def dbsession(func):
    ...
def get_current_hub(*args, **kwargs):
    """
    用于在仓库part.py中获取当前所在的仓库名。
        示例： get_current_hub(__file__)
        
    """
def get_hub_name_list():
    """
    返回仓库名称列表
    """
def get_hub_path(name):
    """
    获取仓库所在的本地路径
    
        :param str name: 仓库名
        
    """
def get_part(name, *args, **kwargs):
    """
    获取指定策略部件
    
        :param str name: 策略部件名称
        :param args: 其他部件相关参数
        :param kwargs: 其他部件相关参数
        
    """
def get_part_info(name):
    """
    获取策略部件信息
    
        :param str name: 部件名称
        
    """
def get_part_list(name_list):
    """
    
        获取指定策略部件列表
    
        :param list name_list: 部件名称列表
        :return: 部件列表
        :rtype: list
        
    """
def get_part_module(part_name: str):
    """
    获取部件模块
        :param str part_name: 部件名称
        :return: 部件模块
        :rtype: module
        
    """
def get_part_name_list(hub = None, part_type = None):
    """
    获取部件名称列表
        :param str hub: 仓库名
        :param str part_type: 部件类型
        
    """
def handle_remove_read_only(func, path, exc):
    ...
def print_part_info(name):
    ...
def remove_hub(name):
    """
    删除指定的仓库
    
        :param str name: 仓库名称
        
    """
def search_part(name: str = None, hub: str = None, part_type: str = None, label: str = None):
    """
    搜索部件
    
        :param str name: 部件名称
        :param str hub: 仓库名
        :param str part_type: 部件类型
        :param str label: 标签
        :return: 部件名称列表
        :rtype: list
        
    """
def update_hub(name):
    """
    更新指定仓库
    
        :param str name: 仓库名称
        
    """
help_part = print_part_info
