"""
Validation utilities for the Limen Access Control System
"""
from typing import Callable
from ..exceptions import DecoratorUsageError


def _get_function_scope_context(func: Callable) -> dict:
    """Get scope context for a function"""
    context = {}
    
    if hasattr(func, '__module__'):
        module_name = func.__module__
        if module_name and module_name != '__main__':
            context['module_name'] = module_name
    
    if hasattr(func, '__qualname__'):
        context['function_name'] = func.__qualname__
        
    return context


def validate_method_usage(func: Callable, decorator_name: str) -> None:
    """Validate that a decorator is being used on a class method, not a module-level function"""
    if hasattr(func, '__qualname__'):
        qualname_parts = func.__qualname__.split('.')

        # Check if this looks like a class method by examining the pattern
        # Valid patterns:
        # - ClassName.method_name (normal case)
        # - outer_func.<locals>.ClassName.method_name (class inside function)
        # - OuterClass.NestedClass.method_name (nested class)
        # Invalid patterns:
        # - function_name (module-level function)
        # - outer_func.<locals>.function_name (nested function)

        if len(qualname_parts) < 2:
            # Single part = module-level function
            scope_context = _get_function_scope_context(func)
            raise DecoratorUsageError(decorator_name, "module-level function", scope_context)
        elif '<locals>' in qualname_parts:
            # If it contains <locals>, check if it ends with ClassName.method_name
            # Find the last occurrence of <locals>
            locals_index = len(qualname_parts) - 1 - qualname_parts[::-1].index('<locals>')
            remaining_parts = qualname_parts[locals_index + 1:]

            # Should have at least 2 parts after <locals>: ClassName.method_name
            # Could be more for nested classes: OuterClass.InnerClass.method_name
            if len(remaining_parts) < 2:
                # This is likely a test case defining a function inside a test
                # Use "module-level function" for consistency with existing tests
                scope_context = _get_function_scope_context(func)
                raise DecoratorUsageError(decorator_name, "module-level function", scope_context)


def validate_class_decoration(cls, decorator_name: str) -> None:
    """Validate that class decoration is being used correctly"""
    import inspect
    
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back.f_back  # Go up two frames
        if caller_frame and cls.__name__ not in caller_frame.f_locals:
            scope_context = {'class_name': cls.__name__}
            raise DecoratorUsageError(decorator_name, "bare class", scope_context)
    finally:
        del frame
