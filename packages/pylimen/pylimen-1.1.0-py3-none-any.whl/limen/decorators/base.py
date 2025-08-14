"""
Base class for access control decorators using Template Method pattern
"""
import inspect
from ..core import AccessLevel, InheritanceType
from ..descriptors import DescriptorFactory
from ..exceptions import DecoratorConflictError, DecoratorUsageError


class AccessControlDecorator:
    """Base class for access control decorators using Template Method pattern"""
    
    def __init__(self, access_level: AccessLevel):
        self._access_level = access_level
    
    def __call__(self, *args):
        """Template method for decorator application"""
        if len(args) == 0:
            return self._create_parameterized_decorator()
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, type):
                # This is a class - we need to check if it's bare decoration or inheritance
                if self._is_bare_class_decoration():
                    # This is bare decoration like @private \n class Foo:
                    # Apply implicit access control based on naming conventions
                    return self._handle_implicit_class_decoration(arg)
                else:
                    # This is valid - @private(BaseClass) called, now applying to derived class
                    return self._handle_class_decoration(arg)
            else:
                return self._apply_to_function(arg)
        else:
            return self._handle_multiple_arguments(args)
    
    def _create_parameterized_decorator(self):
        """Create decorator when called with parentheses"""
        def decorator(func):
            return self._apply_to_function(func)
        return decorator
    
    def _handle_multiple_arguments(self, args):
        """Handle multiple arguments (inheritance from multiple bases)"""
        if all(isinstance(arg, type) for arg in args):
            return self._create_inheritance_decorator(args)
        else:
            scope_context = self._get_scope_context()
            raise DecoratorUsageError(
                self._access_level.value, 
                "invalid inheritance arguments",
                scope_context
            )
    
    def _apply_to_function(self, func):
        """Apply access control to a function"""
        self._validate_function_usage(func)
        self._check_access_level_conflict(func)
        
        # Check if this is already a descriptor created by the limen system
        from ..descriptors.base import AccessControlledDescriptor
        if isinstance(func, AccessControlledDescriptor):
            # Update the access level of the existing descriptor
            func._access_level = self._access_level
            return func
        
        return DescriptorFactory.create_method_descriptor(func, self._access_level)
    
    def _find_available_classes(self):
        """Find available classes in the current scope for suggestions"""
        import inspect
        
        try:
            # Get the frame where the decorator was applied
            frame = inspect.currentframe()
            # Go up through the frames to find the module/class definition context
            available_classes = []
            
            # Check multiple frame levels to find class definitions
            current_frame = frame.f_back
            for _ in range(5):  # Check up to 5 frames up
                if current_frame:
                    # Check both globals and locals
                    for namespace in [current_frame.f_globals, current_frame.f_locals]:
                        for name, obj in namespace.items():
                            if (isinstance(obj, type) and 
                                not name.startswith('_') and 
                                name not in ['Exception', 'BaseException'] and
                                'limen' not in str(obj.__module__ or '') and
                                name not in ['AccessLevel', 'InheritanceType', 'AccessControlDecorator']):
                                available_classes.append(name)
                    current_frame = current_frame.f_back
                else:
                    break
            
            # Remove duplicates and sort
            return sorted(list(set(available_classes)))[:3]  # Limit to 3 suggestions
            
        except Exception:
            return ["BaseClass"]  # Fallback suggestion

    def _handle_implicit_class_decoration(self, cls):
        """Handle bare class decoration (should raise error for now)"""
        # For now, we don't support bare class decoration like @private \n class Foo:
        # This would be for implicit access control on the class itself
        # But the user's requirements show this should be an error case
        
        # Try to find available classes in the same scope for suggestions
        available_classes = self._find_available_classes()
        scope_context = self._get_scope_context()
        
        # Add the actual class name being decorated
        scope_context['class_name'] = cls.__name__
        
        raise DecoratorUsageError(
            self._access_level.value,
            "bare class",
            {"available_classes": available_classes, **scope_context}
        )
    
    def _handle_class_decoration(self, cls):
        """Handle class decoration (inheritance)"""
        # If we get here, it's valid inheritance decoration
        return self._create_inheritance_decorator([cls])
    
    def _create_inheritance_decorator(self, base_classes):
        """Create inheritance decorator"""
        inheritance_type = InheritanceType(self._access_level.value)
        
        def decorator(derived_class):
            # Validate that this is actually being applied to a class
            if not isinstance(derived_class, type):
                if callable(derived_class):
                    if hasattr(derived_class, '__qualname__') and '.' in derived_class.__qualname__:
                        target_type = "method"
                    else:
                        target_type = "function"
                    scope_context = self._get_scope_context()
                    raise DecoratorUsageError(
                        self._access_level.value, 
                        target_type,
                        scope_context
                    )
                else:
                    scope_context = self._get_scope_context()
                    raise DecoratorUsageError(
                        self._access_level.value,
                        "non-class target",
                        scope_context
                    )
            
            # Apply implicit access control to base classes first
            for base_class in base_classes:
                self._apply_implicit_access_control(base_class)
            
            # Then apply to derived class
            self._apply_implicit_access_control(derived_class)
            
            if not hasattr(derived_class, '_inheritance_info'):
                derived_class._inheritance_info = {}
            
            for base_class in base_classes:
                derived_class._inheritance_info[base_class.__name__] = inheritance_type.value
                # Additional inheritance logic would go here
            
            return derived_class
        
        return decorator
    
    def _validate_function_usage(self, func):
        """Validate decorator is used on class methods"""
        from ..utils.validation import validate_method_usage
        validate_method_usage(func, self._access_level.value)

    def _get_method_name(self, func):
        """Get the method name, handling different decorator types"""
        if hasattr(func, '__name__'):
            return func.__name__
        elif isinstance(func, property):
            return getattr(func.fget, '__name__', 'property_method')
        elif isinstance(func, staticmethod):
            return getattr(func.__func__, '__name__', 'static_method')
        elif isinstance(func, classmethod):
            return getattr(func.__func__, '__name__', 'class_method')
        else:
            return 'unknown_method'

    def _detect_wrapper_decorators(self, func):
        """Detect common wrapper decorators like @property, @staticmethod, @classmethod"""
        wrapper_decorators = []
        
        if isinstance(func, property):
            wrapper_decorators.append("property")
        elif isinstance(func, staticmethod):
            wrapper_decorators.append("staticmethod")
        elif isinstance(func, classmethod):
            wrapper_decorators.append("classmethod")
        
        return wrapper_decorators

    def _get_scope_context(self) -> dict:
        """Get scope context information from the call stack"""
        import inspect
        import re
        
        context = {}
        
        try:
            stack = inspect.stack()
            
            # Look through the stack to find relevant context
            for i, frame_info in enumerate(stack[1:], 1):
                frame = frame_info.frame
                
                # For class decoration, look for the special __build_class__ frame
                if frame_info.function == '__build_class__':
                    # This is the frame where a class is being built
                    if 'name' in frame.f_locals:
                        context['class_name'] = frame.f_locals['name']
                        break
                
                # Look for class definition pattern in code context
                if hasattr(frame_info, 'code_context') and frame_info.code_context:
                    for line in frame_info.code_context:
                        line = line.strip()
                        # Match class definition patterns
                        class_match = re.match(r'class\s+(\w+)', line)
                        if class_match:
                            context['class_name'] = class_match.group(1)
                            break
                    
                    if 'class_name' in context:
                        break
                
                # Check if we're in a class namespace being built
                if '__name__' in frame.f_locals and frame.f_locals.get('__name__'):
                    # This might be a class namespace
                    class_name = frame.f_locals.get('__qualname__')
                    if class_name and '.' not in class_name:  # Avoid nested classes for now
                        context['class_name'] = class_name
                        break
                
                # Try to get module name
                if '__name__' in frame.f_globals:
                    module_name = frame.f_globals['__name__']
                    if module_name != '__main__':
                        context.setdefault('module_name', module_name)
                        
        except Exception:
            # If anything goes wrong with stack inspection, just return empty context
            pass
            
        return context

    def _get_class_context_from_stack(self):
        """Extract class name from the call stack during decorator application"""
        import inspect
        import re
        
        try:
            # Get the call stack
            stack = inspect.stack()
            
            # Look through the stack frames to find class definition context
            for frame_info in stack[1:15]:  # Check more frames
                frame = frame_info.frame
                
                # Method 1: Look for __build_class__ frame
                if frame_info.function == '__build_class__':
                    if 'name' in frame.f_locals:
                        return frame.f_locals['name']
                
                # Method 2: Look for class definition in code context
                if hasattr(frame_info, 'code_context') and frame_info.code_context:
                    for line in frame_info.code_context:
                        line = line.strip()
                        class_match = re.match(r'class\s+(\w+)', line)
                        if class_match:
                            return class_match.group(1)
                
                # Method 3: Look for class definition context via __qualname__
                local_vars = frame.f_locals
                if '__qualname__' in local_vars:
                    qualname = local_vars['__qualname__']
                    if isinstance(qualname, str) and '.' not in qualname and qualname.isidentifier():
                        # This looks like a class being defined
                        return qualname
                
                # Method 4: Look for class name being assigned
                if '__name__' in local_vars and '__module__' in local_vars:
                    class_name = local_vars.get('__name__')
                    if (class_name and isinstance(class_name, str) and 
                        class_name.isidentifier() and not class_name.startswith('_')):
                        return class_name
                        
            return None
        except Exception:
            # If stack inspection fails, just return None
            return None

    def _check_access_level_conflict(self, func):
        """Check for conflicting access level decorators"""
        from ..utils.descriptors import (
            get_access_level_from_descriptor, 
            get_friend_flag_from_descriptor
        )
        
        existing_level = get_access_level_from_descriptor(func)
        has_friend_flag = get_friend_flag_from_descriptor(func)

        if existing_level is not None:
            # Special case: Allow overriding or confirming access level if it was set by friend decorator
            if has_friend_flag and existing_level == AccessLevel.PUBLIC:
                # Allow explicit access level to override or confirm the friend decorator's default
                return
            
            # Try to detect wrapper decorators for better suggestions
            wrapper_decorators = self._detect_wrapper_decorators(func)
            
            # Get a better method name
            method_name = self._get_method_name(func)
            
            # Try to get class context for better error messages
            class_context = self._get_class_context_from_stack()
            
            raise DecoratorConflictError(
                existing_level.value, 
                self._access_level.value, 
                method_name,
                {
                    "wrapper_decorators": wrapper_decorators, 
                    "func_obj": func,
                    "class_name": class_context
                }
            )

    def _is_bare_class_decoration(self):
        """Check if this is bare class decoration (invalid)"""
        try:
            # Use inspect.stack() to get reliable frame information
            stack = inspect.stack()
            
            # Look for the decorator application in the stack
            # We skip the first few frames which are internal to our decorator
            for frame_info in stack[3:8]:  # Check a reasonable range of frames
                if frame_info.code_context:
                    line = frame_info.code_context[0].strip()
                    # Look for patterns like "@private" without parentheses
                    decorator_name = f"@{self._access_level.value}"
                    if line.startswith(decorator_name) and "(" not in line:
                        return True  # Bare decoration detected
                    elif f"@{self._access_level.value}(" in line:
                        return False  # Inheritance decoration detected
            
            # If we can't determine from the stack, assume it's valid (safer)
            return False
        except Exception:
            # If anything goes wrong with stack inspection, assume valid
            return False
    
    def _apply_implicit_access_control(self, cls):
        """Apply implicit access control based on naming conventions and inheritance"""
        from ..utils import apply_implicit_access_control
        from ..descriptors import DescriptorFactory
        
        # First apply standard implicit access control
        apply_implicit_access_control(cls)
        
        # For inheritance decoration, also ensure all inherited methods have descriptors
        # so they can participate in inheritance-based access control
        for name in dir(cls):
            # Skip special methods and private attributes
            if name.startswith('__') and name.endswith('__'):
                continue
            if name.startswith('_' + cls.__name__ + '__'):  # Name-mangled private
                continue
                
            attr = getattr(cls, name)
            
            # Only process callable methods that aren't already our descriptors
            if (callable(attr) and 
                not hasattr(attr, '_access_level') and 
                not hasattr(attr, '_owner')):
                
                # Check if this method is inherited (not defined in this class)
                if name not in cls.__dict__:
                    # This is an inherited method - wrap it with a descriptor
                    # so it can participate in inheritance-based access control
                    
                    # Determine the original access level
                    if name.startswith('_'):
                        access_level = AccessLevel.PROTECTED
                    else:
                        access_level = AccessLevel.PUBLIC
                    
                    # Create a descriptor for the inherited method
                    descriptor = DescriptorFactory.create_method_descriptor(attr, access_level)
                    setattr(cls, name, descriptor)
                    if hasattr(descriptor, '__set_name__'):
                        descriptor.__set_name__(cls, name)
