"""
Custom exception classes for the Limen Access Control System
"""
from .message_generators import MessageGenerator


class LimenError(Exception):
    """Base exception for all Limen access control errors"""
    __module__ = 'limen'
    pass


class ContextualAccessControlError(LimenError):
    """Base class for access control errors with contextual message generation"""
    __module__ = 'limen'
    
    def __init__(self, context: dict = None):
        self.context = context or {}
        message = self._generate_contextual_message()
        super().__init__(message)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _generate_contextual_message")


class PermissionDeniedError(LimenError):
    """Raised when access to a method or property is denied"""
    __module__ = 'limen'
    
    def __init__(self, access_level: str, member_type: str, member_name: str, 
                 target_class: str = None, caller_info: dict = None):
        self.access_level = access_level
        self.member_type = member_type
        self.member_name = member_name
        self.target_class = target_class
        self.caller_info = caller_info or {}
        
        # Build enhanced error message with scope information
        message = self._build_error_message()
        super().__init__(message)
    
    def _build_error_message(self) -> str:
        """Build a detailed error message with scope information"""
        # Base message
        if self.target_class:
            target = f"{self.target_class}.{self.member_name}()"
        else:
            target = f"{self.member_name}()"
        
        base_msg = f"Access denied to @{self.access_level} {self.member_type} {target}"
        
        # Add caller information if available
        caller_class = self.caller_info.get('caller_class')
        caller_function = self.caller_info.get('caller_function')
        caller_module = self.caller_info.get('caller_module')
        
        if caller_class and caller_function:
            caller_scope = f"{caller_class}.{caller_function}()"
        elif caller_function:
            if caller_module and caller_module != '__main__':
                caller_scope = f"{caller_module}.{caller_function}()"
            elif caller_function == '<module>':
                caller_scope = "module-level code"
            else:
                caller_scope = f"{caller_function}()"
        elif caller_class:
            caller_scope = f"{caller_class}"
        elif caller_module:
            caller_scope = f"{caller_module}"
        else:
            caller_scope = "external code"
        
        return f"{base_msg} from {caller_scope}"


class DecoratorConflictError(ContextualAccessControlError):
    """Raised when conflicting access level decorators are applied"""
    __module__ = 'limen'
    
    def __init__(self, existing_level: str, new_level: str, method_name: str, context: dict = None):
        self.existing_level = existing_level
        self.new_level = new_level
        self.method_name = method_name
        super().__init__(context)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message with helpful suggestions"""
        return MessageGenerator.generate_conflict_message(
            self.existing_level,
            self.new_level,
            self.method_name,
            self.context
        )


class DecoratorUsageError(ContextualAccessControlError):
    """Raised when decorators are used incorrectly"""
    __module__ = 'limen'
    
    def __init__(self, decorator_name: str, usage_type: str, context: dict = None):
        self.decorator_name = decorator_name
        self.usage_type = usage_type
        super().__init__(context)
    
    def _generate_contextual_message(self) -> str:
        """Generate a contextual error message with helpful suggestions"""
        return MessageGenerator.generate_usage_error_message(
            self.decorator_name,
            self.usage_type,
            self.context
        )
