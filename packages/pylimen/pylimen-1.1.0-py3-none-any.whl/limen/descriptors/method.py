"""
Descriptor for regular methods - PERFORMANCE OPTIMIZED
"""
from functools import wraps
from .base import AccessControlledDescriptor
from ..core import internal_call_context

# Cache access control system to avoid repeated imports
_access_control_system = None

def get_cached_access_control():
    """Get cached access control system"""
    global _access_control_system
    if _access_control_system is None:
        from ..system.access_control import get_access_control_system
        _access_control_system = get_access_control_system()
    return _access_control_system

class MethodDescriptor(AccessControlledDescriptor):
    """Descriptor for regular methods - PERFORMANCE OPTIMIZED"""
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            try:
                self._check_access(obj)
            except Exception as e:
                # Create a new exception and directly raise it with simplified traceback
                from ..exceptions import PermissionDeniedError
                if isinstance(e, PermissionDeniedError):
                    raise PermissionDeniedError(
                        e.access_level, 
                        e.member_type, 
                        e.member_name,
                        target_class=e.target_class,
                        caller_info=e.caller_info
                    ) from None
                else:
                    raise e from None
            
            # Skip event emission in production for performance
            # (This can be re-enabled via config if needed)
            
            with internal_call_context():
                return self._func_or_value(obj, *args, **kwargs)
        
        return wrapper
    
    def _get_member_type(self) -> str:
        return "method"
