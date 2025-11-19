"""
Streamlit Utilities for Agentic PM
Fixes ScriptRunContext warnings and provides enterprise-ready Streamlit helpers
"""

import streamlit as st
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def safe_streamlit_call(func: Callable) -> Callable:
    """
    Decorator to safely call Streamlit functions, handling ScriptRunContext warnings
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Check if we're in a Streamlit context
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            
            if ctx is None:
                # Not in Streamlit context - log and return None
                logger.warning(f"Streamlit context not available for {func.__name__}")
                return None
            
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Streamlit call {func.__name__}: {e}")
            return None
    
    return wrapper


def safe_session_state(key: str, default: Any = None) -> Any:
    """Safely get or set session state"""
    try:
        if key not in st.session_state:
            st.session_state[key] = default
        return st.session_state[key]
    except Exception as e:
        logger.warning(f"Error accessing session state for {key}: {e}")
        return default


def safe_rerun():
    """Safely rerun Streamlit app"""
    try:
        st.rerun()
    except Exception as e:
        logger.warning(f"Error rerunning app: {e}")
        # Fallback: try to use experimental_rerun if available
        try:
            st.experimental_rerun()
        except:
            pass


def safe_spinner(message: str):
    """Context manager for safe spinner usage"""
    try:
        return st.spinner(message)
    except Exception as e:
        logger.warning(f"Error creating spinner: {e}")
        # Return a no-op context manager
        from contextlib import nullcontext
        return nullcontext()

