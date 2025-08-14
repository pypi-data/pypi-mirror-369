"""
Debug utilities for Limen access control system
"""
from typing import Any, Dict, Type
from ..core.config import get_config


class DebugLogger:
    """Centralized debug logging utility"""
    
    def __init__(self):
        self._config = get_config()
    
    @property
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self._config.debugging.debug_enabled
    
    def debug_access_check(self, target_class: Type, method_name: str, 
                          access_level: str, caller_info: Any, 
                          instance_class: Type = None) -> None:
        """Log access check details"""
        if not self.is_debug_enabled or not self._config.debugging.trace_access_calls:
            return
    
    def debug_stack_inspection(self, frames_info: list, caller_info: Any = None) -> None:
        """Log stack inspection details"""
        if not self.is_debug_enabled or not self._config.debugging.trace_stack_inspection:
            return
    
    def debug_strategy_decision(self, strategy_name: str, context: Any, 
                               decision: Any, reason: str = "") -> None:
        """Log strategy decision details"""
        if not self.is_debug_enabled or not self._config.debugging.trace_strategy_decisions:
            return
    
    def debug_final_decision(self, allowed: bool, reason: str = "") -> None:
        """Log final access decision"""
        if not self.is_debug_enabled:
            return
    
    def debug_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log error with context"""
        if not self.is_debug_enabled or not self._config.debugging.verbose_errors:
            return
    
    def _format_caller_info(self, caller_info: Any) -> str:
        """Format caller info for display"""
        if not caller_info:
            return "None"
        
        if hasattr(caller_info, 'caller_class') and hasattr(caller_info, 'caller_method'):
            class_name = caller_info.caller_class.__name__ if caller_info.caller_class else 'None'
            method_name = caller_info.caller_method or 'None'
            return f"{class_name}.{method_name}"
        
        return str(caller_info)
    
    def _format_context(self, context: Any) -> str:
        """Format context object for display"""
        if hasattr(context, '__dict__'):
            items = []
            for key, value in context.__dict__.items():
                if hasattr(value, '__name__'):
                    items.append(f"{key}={value.__name__}")
                else:
                    items.append(f"{key}={value}")
            return "{" + ", ".join(items) + "}"
        return str(context)
    
    def _should_skip_frame_debug(self, frame_info) -> bool:
        """Debug version of frame skipping logic"""
        # This should match the actual skipping logic in StackInspector
        filename = frame_info.filename.lower()
        function_name = frame_info.function
        
        # Skip Limen internal frames
        if any(module in filename for module in ['limen', 'descriptor', 'access', 'inspection']):
            return True
        
        # Skip test/debug frames
        if any(module in filename for module in ['pytest', 'unittest', '_pytest']):
            return True
        
        # Skip wrapper functions
        wrapper_functions = {
            'controlled_static', 'controlled_class', 'wrapper',
            'static_wrapper', 'class_wrapper', 'method_wrapper',
            'controlled_getattribute', 'controlled_setattr', 'getter',
            '_check_access', '__get__', '__set__', '__delete__',
            'can_access', 'protected_getattribute', '_check_access_classmethod'
        }
        
        if function_name in wrapper_functions:
            return True
        
        return False


# Global debug logger instance
_debug_logger = None


def get_debug_logger() -> DebugLogger:
    """Get the global debug logger instance"""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger()
    return _debug_logger


# Convenience functions
def debug_access_check(*args, **kwargs):
    """Convenience function for access check debugging"""
    get_debug_logger().debug_access_check(*args, **kwargs)


def debug_stack_inspection(*args, **kwargs):
    """Convenience function for stack inspection debugging"""
    get_debug_logger().debug_stack_inspection(*args, **kwargs)


def debug_strategy_decision(*args, **kwargs):
    """Convenience function for strategy decision debugging"""
    get_debug_logger().debug_strategy_decision(*args, **kwargs)


def debug_final_decision(*args, **kwargs):
    """Convenience function for final decision debugging"""
    get_debug_logger().debug_final_decision(*args, **kwargs)


def debug_error(*args, **kwargs):
    """Convenience function for error debugging"""
    get_debug_logger().debug_error(*args, **kwargs)


def enable_debug_mode():
    """Enable debug mode with all tracing"""
    from ..core.config import update_config
    update_config(
        **{
            "debugging.debug_enabled": True,
            "debugging.trace_access_calls": True,
            "debugging.trace_stack_inspection": True,
            "debugging.trace_strategy_decisions": True,
            "debugging.verbose_errors": True,
            "debugging.log_level": "debug"
        }
    )


def disable_debug_mode():
    """Disable debug mode"""
    from ..core.config import update_config
    update_config(
        **{
            "debugging.debug_enabled": False,
            "debugging.trace_access_calls": False,
            "debugging.trace_stack_inspection": False,
            "debugging.trace_strategy_decisions": False,
            "debugging.verbose_errors": False
        }
    )
