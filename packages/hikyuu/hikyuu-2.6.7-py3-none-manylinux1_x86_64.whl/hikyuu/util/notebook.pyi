from __future__ import annotations
__all__ = ['in_interactive_session', 'in_ipython_frontend']
def in_interactive_session() -> bool:
    """
    
        Check if we're running in an interactive shell.
    
        Returns
        -------
        bool
            True if running under python/ipython interactive shell.
        
    """
def in_ipython_frontend() -> bool:
    """
    
        Check if we're inside an IPython zmq frontend. 检测是否在 jupyter 环境中
    
        Returns
        -------
        bool
        
    """
