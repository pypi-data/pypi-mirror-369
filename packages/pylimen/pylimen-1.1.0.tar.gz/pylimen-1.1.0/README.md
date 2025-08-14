# Limen

Limen is an access control system that provides fine-grained security and encapsulation for Python classes. It implements true C++ semantics including public, protected, and private access levels, friend relationships, and inheritance-based access control with automatic detection of access levels based on method naming conventions.

*Limen (Latin: "threshold") - The boundary between spaces, representing the controlled passage between public and private domains.*

### Key Features

- **C++ Style Access Control**: Complete implementation of `@private`, `@protected`, `@public` decorators
- **Implicit Access Control**: Automatic access level detection based on naming conventions (_, __, normal names)
- **Name Mangling Bypass Prevention**: Blocks circumvention of access control via `_ClassName__method` patterns
- **Friend Relationships**: Support for `@friend` classes, methods, functions, and staticmethods/classmethods
- **Advanced Inheritance**: True C++ style inheritance with public, protected, and private inheritance patterns
- **Dual-Layer Security**: Access modifiers on friend methods for fine-grained permission control
- **Descriptor Support**: Full compatibility with `@staticmethod`, `@classmethod`, `@property` decorators
- **Multiple Inheritance**: Support for complex inheritance hierarchies with proper access control
- **Runtime Management**: Dynamic enable/disable enforcement, metrics, and debugging capabilities
- **Enhanced Error Handling**: Contextual exception types with detailed error messages, code suggestions, and intelligent formatting
- **Zero Dependencies**: Pure Python implementation with no external requirements

<details>
<summary><strong>Installation</strong></summary>

## Installation

### From PyPI (Recommended)
```bash
pip install pylimen
```

### From Source
```bash
git clone https://github.com/Ma1achy/Limen.git
cd Limen
pip install -e .
```

</details>

<details>
<summary><strong>Access Control & Inheritance</strong></summary>

## Access Control & Inheritance

Limen provides comprehensive access control through explicit decorators and C++ style inheritance semantics with public, protected, and private inheritance types.

### Basic Access Control Decorators

#### @private - Same Class Only

Private methods are only accessible within the same class where they're defined.

```python
from limen import private, protected, public, friend

class Base:
    @private
    def _private_method(self):
        return "private"
    
    @public
    def public_method(self):
        # Works - same class access
        return self._private_method()

obj = Base()
obj.public_method()  # Works - public access
# obj._private_method()  # PermissionDeniedError - private access
```

#### @protected - Inheritance Hierarchy

Protected methods are accessible within the same class and its subclasses.

```python
class Base:
    @protected
    def _protected_method(self):
        return "protected"

class Derived(Base):
    def foo(self):
        # Works - derived class can access protected members
        return self._protected_method()

obj = Derived()
obj.foo()  # Works - calls protected method internally
# obj._protected_method()  # PermissionDeniedError - external access blocked
```

#### @public - Universal Access

Public methods are accessible from anywhere (default Python behavior, useful for explicit documentation).

```python
class Base:
    @public
    def get_data(self):
        return "data"
    
    @public
    def check_status(self):
        return "ok"

obj = Base()
obj.get_data()      # Works from anywhere
obj.check_status()  # Works from anywhere
```

### C++ Style Inheritance Control

Apply inheritance decorators to modify access levels of inherited members according to C++ semantics.

#### Public Inheritance (Default)

Standard Python inheritance behavior where access levels are preserved:

```python
class Base:
    def public_method(self):              # Implicit @public
        return "public"
    
    def _protected_method(self):          # Implicit @protected
        return "protected"
    
    def __private_method(self):           # Implicit @private
        return "private"

class Derived(Base):
    def test_access(self):
        # Can access public and protected members from base
        public_data = self.public_method()       # Inherited as public
        protected_data = self._protected_method() # Inherited as protected
        
        # Cannot access private members from base
        # private_data = self.__private_method()  # PermissionDeniedError
        
        return f"{public_data}, {protected_data}"

obj = Derived()
result = obj.test_access()          # Works internally
external_public = obj.public_method()  # Works externally - public access
# external_protected = obj._protected_method()  # PermissionDeniedError - protected
```

#### Protected Inheritance

Protected inheritance converts public members to protected, following C++ semantics:

```python
class Base:
    def public_method(self):             # Implicit @public
        return "public"
    
    def _protected_method(self):         # Implicit @protected
        return "protected"
    
    @private
    def _private_method(self):           # Explicit @private
        return "private"

@protected(Base)  # Protected inheritance - applies implicit control to Base
class Derived(Base):
    def operation(self):
        # Can access all inherited members internally
        public_data = self.public_method()       # Now protected due to inheritance
        protected_data = self._protected_method() # Remains protected
        # Cannot access private members
        # secret = self._private_method()        # PermissionDeniedError
        return f"{public_data}, {protected_data}"

obj = Derived()
result = obj.operation()       # Works internally

# External access - all methods are now protected due to inheritance
# obj.public_method()          # PermissionDeniedError - public became protected
# obj._protected_method()      # PermissionDeniedError - protected remains protected
```

#### Private Inheritance

Private inheritance makes all inherited members private to the derived class:

```python
class Base:
    def public_method(self):             # Implicit @public
        return "public"
    
    def _protected_method(self):         # Implicit @protected
        return "protected"

@private(Base)  # Private inheritance
class Derived(Base):
    def operation(self):
        # Can access inherited members internally
        public_data = self.public_method()    # Now private due to inheritance
        protected_data = self._protected_method() # Now private due to inheritance
        return f"{public_data}, {protected_data}"
    
    def public_interface(self):
        # Expose functionality through controlled interface
        return self.operation()

obj = Derived()
result = obj.public_interface()       # Works - controlled access

# External access blocked - all inherited methods are now private
# obj.public_method()                 # PermissionDeniedError - public became private
# obj._protected_method()             # PermissionDeniedError - protected became private
```

#### Inheritance Summary

| Inheritance Type | Public Members | Protected Members | Private Members |
|------------------|----------------|-------------------|-----------------|
| **Public** (default) | Remain public | Remain protected | Remain private (inaccessible) |
| **Protected** `@protected(Base)` | Become protected | Remain protected | Remain private (inaccessible) |
| **Private** `@private(Base)` | Become private | Become private | Remain private (inaccessible) |

### Multiple Inheritance with Access Control

Apply inheritance decorators to multiple base classes for complex access patterns:

```python
class BaseA:
    def method_a(self):                 # Implicit @public
        return "a"
    
    def _helper_a(self):                # Implicit @protected
        return "helper a"

class BaseB:
    def method_b(self):                 # Implicit @public
        return "b"
    
    def _helper_b(self):                # Implicit @protected
        return "helper b"

# Multiple inheritance with different access patterns
@protected(BaseA)                      # Only BaseA gets protected inheritance
@private(BaseB)                        # Only BaseB gets private inheritance
class Derived(BaseA, BaseB):
    def operation(self):
        # BaseA methods - protected due to inheritance
        a_method = self.method_a()       # Now protected
        a_helper = self._helper_a()      # Still protected
        
        # BaseB methods - private due to inheritance
        b_method = self.method_b()       # Now private
        b_helper = self._helper_b()      # Now private
        
        return f"{a_method}, {a_helper}, {b_method}, {b_helper}"
    
    def public_interface(self):
        return self.operation()

obj = Derived()
result = obj.public_interface()       # Works - controlled access

# External access follows inheritance rules
# obj.method_a()                      # PermissionDeniedError - protected inheritance
# obj.method_b()                      # PermissionDeniedError - private inheritance
```

### Friend Relationships with Inheritance

Friend relationships are preserved across inheritance patterns:

```python
class Target:
    def _protected_method(self):        # Implicit @protected
        return "protected"

@friend(Target)
class Helper:
    def access_target(self, target):
        # Friend can access protected members
        return target._protected_method()

# Protected inheritance preserves friend relationships
@protected(Target)
class Derived(Target):
    def internal_operation(self):
        return self._protected_method()     # Works internally

helper = Helper()
derived_obj = Derived()

# Friend access works even with inheritance
result = helper.access_target(derived_obj)  # Works - friend relationship preserved

# Regular external access blocked
# derived_obj._protected_method()           # PermissionDeniedError - protected access
```

\n</details><details>\n<summary><strong>Implicit Access Control</strong></summary>## Implicit Access Control

Limen provides automatic access level detection based on Python naming conventions. When inheritance decorators are applied, methods are automatically wrapped with appropriate access control based on their names.

### Naming Convention Rules

- **Normal names** (e.g., `method_name`) → `@public`
- **Single underscore prefix** (e.g., `_method_name`) → `@protected`
- **Double underscore prefix** (e.g., `__method_name`) → `@private`

### Automatic Application with Inheritance Decorators

When you use inheritance decorators like `@protected(BaseClass)`, implicit access control is automatically applied to both the base class and derived class:

```python
class Base:
    def public_method(self):               # Automatically treated as @public
        return "public"
    
    def _protected_method(self):           # Automatically treated as @protected
        return "protected"
    
    def __private_method(self):            # Automatically treated as @private
        return "private"
    
    @public                                # Explicit decorator overrides implicit
    def _explicitly_public(self):
        return "explicit public"

# Inheritance decorator applies implicit access control to Base
@protected(Base)
class Derived(Base):
    def test_access(self):
        # Can access all inherited methods internally
        public_data = self.public_method()       # Inherited public method
        protected_data = self._protected_method() # Inherited protected method
        explicit_data = self._explicitly_public() # Explicit override
        return f"{public_data}, {protected_data}, {explicit_data}"

obj = Derived()

# Internal access works
result = obj.test_access()  # Works - internal access

# External access controlled by inheritance rules
# Protected inheritance converts public methods to protected
obj.public_method()         # PermissionDeniedError - public became protected
obj._protected_method()     # PermissionDeniedError - protected method
obj._explicitly_public()   # PermissionDeniedError - explicit public became protected
```

### Manual Application

You can also manually apply implicit access control without inheritance:

```python
from limen.utils.implicit import apply_implicit_access_control

class Base:
    def public_method(self):
        return "public"
    
    def _protected_method(self):
        return "protected"
    
    def __private_method(self):
        return "private"

# Manually apply implicit access control
apply_implicit_access_control(Base)

obj = Base()
obj.public_method()      # Works - public access
# obj._protected_method()  # PermissionDeniedError - protected access
# obj.__private_method()   # PermissionDeniedError - private access (name mangled)
```

### Explicit Override of Implicit Rules

Explicit decorators always take precedence over implicit naming conventions:

```python
class Base:
    @private                               # Explicit private
    def normal_name_but_private(self):     # Normal name, but explicitly private
        return "private despite normal name"
    
    @public                                # Explicit public
    def _underscore_but_public(self):      # Underscore name, but explicitly public
        return "public despite underscore"

@protected(Base)  # Apply implicit control
class Derived(Base):
    pass

obj = Derived()

# Explicit decorators override naming conventions
# obj.normal_name_but_private()    # PermissionDeniedError - explicitly private
obj._underscore_but_public()       # PermissionDeniedError - but protected inheritance affects it
```

\n</details><details>\n<summary><strong>Friend Relationships</strong></summary>## Friend Relationships

Friend classes and functions can access private and protected members of target classes, providing controlled access across class boundaries.

### Friend Classes

Friend classes can access private and protected members of the target class.

```python
class Target:
    @private
    def _private_method(self):
        return "private"
    
    @protected
    def _protected_method(self):
        return "protected"

@friend(Target)
class FriendA:
    def access_target(self, target):
        # Friend can access private methods
        private_data = target._private_method()
        protected_data = target._protected_method()
        return f"{private_data}, {protected_data}"

@friend(Target)
class FriendB:
    def inspect_target(self, target):
        # Multiple classes can be friends
        return target._protected_method()

# Usage
target = Target()
friend_a = FriendA()
friend_b = FriendB()

friend_a.access_target(target)   # Friend access works
friend_b.inspect_target(target)  # Multiple friends work

# Regular class cannot access private members
class Regular:
    def try_access(self, target):
        # PermissionDeniedError - not a friend
        return target._protected_method()
```

### Friend Functions

Friend functions are standalone functions that can access private and protected members.

```python
class Target:
    @private
    def _private_method(self):
        return "private"
    
    @protected
    def _protected_method(self):
        return "protected"

@friend(Target)
def friend_function_a(target):
    """Friend function for processing"""
    private_data = target._private_method()
    return f"Processed: {private_data}"

@friend(Target)
def friend_function_b(target):
    """Friend function for analysis"""
    protected_data = target._protected_method()
    return f"Analyzed: {protected_data}"

def regular_function(target):
    """Regular function - no friend access"""
    # PermissionDeniedError - cannot access private methods
    return target._private_method()

# Usage
target = Target()

friend_function_a(target)   # Friend function works
friend_function_b(target)   # Another friend function works
# regular_function(target)  # PermissionDeniedError
```

### Friend Descriptors

Friend relationships work with all Python descriptor types: staticmethod, classmethod, and property.

```python
class Target:
    def __init__(self, value):
        self._value = value
    
    @private
    def _private_method(self):
        return "private"
    
    @private
    @property
    def private_property(self):
        return self._value

class Helper:
    # Friend staticmethod
    @friend(Target)
    @staticmethod
    def static_helper(target):
        return target._private_method()
    
    # Friend classmethod
    @friend(Target)
    @classmethod
    def class_helper(cls, target):
        return target._private_method()
    
    # Friend instance method accessing property
    @friend(Target)
    def access_property(self, target):
        return target.private_property

target = Target("secret")
result1 = Helper.static_helper(target)    # Works
result2 = Helper.class_helper(target)     # Works
helper = Helper()
result3 = helper.access_property(target)  # Works
```

\n</details><details>\n<summary><strong>Dual-Layer Security: Access Modifiers on Friend Methods</strong></summary>## Dual-Layer Security: Access Modifiers on Friend Methods

**Advanced Feature**: Apply access modifiers to friend methods themselves for fine-grained control.

```python
class Target:
    @private
    def _private_method(self):
        return "private"

class Helper:
    # Public friend method - anyone can call it
    @public
    @friend(Target)
    def public_access(self, target):
        return target._private_method()
    
    # Protected friend method - only inheritance can use it
    @protected
    @friend(Target)
    def protected_access(self, target):
        return target._private_method()
    
    # Private friend method - only internal use
    @private
    @friend(Target)
    def private_access(self, target):
        return target._private_method()
    
    def internal_operation(self, target):
        # Can use private friend method internally
        return self.private_access(target)

class DerivedHelper(Helper):
    def inherited_operation(self, target):
        # Can use protected friend method via inheritance
        return self.protected_access(target)

# Usage
target = Target()
helper = Helper()
derived = DerivedHelper()

# Public friend method works for everyone
helper.public_access(target)

# Protected friend method works via inheritance
derived.inherited_operation(target)

# Private friend method works via internal access
helper.internal_operation(target)

# Direct access to protected/private friend methods blocked
# helper.protected_access(target)  # PermissionDeniedError
# helper.private_access(target)    # PermissionDeniedError
```

### Staticmethod and Classmethod with Access Modifiers

```python
class Target:
    @private
    def _private_method(self):
        return "private"

class Helper:
    # Protected friend staticmethod
    @protected
    @friend(Target)
    @staticmethod
    def protected_static_helper(target):
        return target._private_method()
    
    # Private friend classmethod
    @private
    @friend(Target)
    @classmethod
    def private_class_helper(cls, target):
        return target._private_method()
    
    @classmethod
    def internal_class_operation(cls, target):
        # Can use private classmethod internally
        return cls.private_class_helper(target)

class DerivedHelper(Helper):
    @classmethod
    def use_protected_static(cls, target):
        # Can use protected staticmethod via inheritance
        return cls.protected_static_helper(target)

target = Target()
helper = Helper()
derived = DerivedHelper()

# Protected staticmethod works via inheritance
derived.use_protected_static(target)

# Private classmethod works via internal access
helper.internal_class_operation(target)

# Direct access blocked
# Helper.protected_static_helper(target)  # PermissionDeniedError
# Helper.private_class_helper(target)     # PermissionDeniedError
```

\n</details><details>\n<summary><strong>Security Features</strong></summary>## Security Features

### Name Mangling Bypass Prevention

**Critical Security Feature**: Limen prevents bypassing access control through Python's name mangling mechanism using multiple protection layers.

Python automatically converts private methods like `__private_method` to `_ClassName__private_method`. Without protection, external code could bypass access control by directly accessing the mangled name:

#### Protection for Implicit Private Methods

```python
class SecureClass:
    def __private_method(self):
        return "secret data"
    
    def public_access(self):
        return self.__private_method()  # Legitimate internal access

# Apply implicit access control (detects __ methods as private)
from limen.utils.implicit import apply_implicit_access_control
apply_implicit_access_control(SecureClass)

obj = SecureClass()

# Internal access works
result = obj.public_access()  # "secret data"

# Direct access blocked (AttributeError)
# obj.__private_method()  # AttributeError: no attribute '__private_method'

# Name mangling bypass blocked (PermissionDeniedError)  
# obj._SecureClass__private_method()  # PermissionDeniedError: Access denied to private method
```

#### Protection for Explicit @private Decorators

Explicit `@private` decorators also prevent name mangling bypasses through descriptor-level access control:

```python
from limen import private

class SecureClass:
    @private
    def __private_method(self):
        return "secret data"
    
    @private  
    def regular_private(self):
        return "also secret"
    
    def public_access(self):
        return f"{self.__private_method()}, {self.regular_private()}"

obj = SecureClass()

# Internal access works
result = obj.public_access()  # "secret data, also secret"

# Direct access blocked (PermissionDeniedError)
# obj.regular_private()  # PermissionDeniedError: Access denied to private method

# Name mangling bypass blocked (PermissionDeniedError) 
# obj._SecureClass__private_method()  # PermissionDeniedError: Access denied to private method

# Manual mangling attempts fail (AttributeError)
# obj._SecureClass__regular_private()  # AttributeError: no such attribute
```

**How It Works:**
- **Explicit decorators**: Descriptor-level access control validates every method call regardless of access path
- **Implicit detection**: Custom `__getattribute__` protection intercepts mangled name access for `__` methods  
- **Dual protection**: Methods can be protected by both mechanisms simultaneously
- **Friend preservation**: Authorized friends can still access via any legitimate method

**Friend Access Still Works:**
```python
class DataStore:
    def __private_data(self):
        return "sensitive"
    
    @private
    def __explicit_private(self):
        return "explicit sensitive"

@friend(DataStore)
class AuthorizedProcessor:
    def process(self, store):
        # Friend can access via mangled name when authorized (both types)
        implicit = store._DataStore__private_data()
        explicit = store._DataStore__explicit_private()
        return f"{implicit}, {explicit}"

apply_implicit_access_control(DataStore)

store = DataStore()
processor = AuthorizedProcessor()
result = processor.process(store)  # Works - friend access allowed

# Unauthorized access still blocked for both
class UnauthorizedClass:
    def hack(self, store):
        return store._DataStore__private_data()  # PermissionDeniedError

unauthorized = UnauthorizedClass()
# unauthorized.hack(store)  # PermissionDeniedError: Access denied
```

This security feature ensures that Limen's access control cannot be circumvented through Python's name mangling, providing true encapsulation and security for your private methods.

\n</details><details>\n<summary><strong>Property Access Control</strong></summary>## Property Access Control

Control getter and setter access independently with sophisticated property decorators.

### Basic Property Control

```python
class Base:
    def __init__(self, name, value):
        self._name = name
        self._value = value
    
    @protected
    @property
    def value(self):
        """Protected getter - accessible in inheritance"""
        return self._value
    
    @value.setter
    @private
    def value(self, new_value):
        """Private setter - only same class"""
        if new_value > 0:
            self._value = new_value
    
    def update_value(self, amount):
        # Private setter works within same class
        self.value = self._value + amount
    
    @public
    @property
    def name(self):
        """Public getter"""
        return self._name

class Derived(Base):
    def check_value(self):
        # Can read value (protected getter)
        return f"Value: {self.value}"
    
    def try_modify_value(self, new_value):
        # Cannot use private setter
        # self.value = new_value  # PermissionDeniedError
        pass

obj1 = Base("item1", 100)
obj2 = Derived("item2", 200)

# Public property access
print(obj1.name)

# Protected property access via inheritance
print(obj2.check_value())

# Internal value modification
obj1.update_value(50)

# External access to protected property
# print(obj1.value)  # PermissionDeniedError
```

### Friend Access to Properties

```python
class Target:
    def __init__(self, value):
        self._value = value
    
    @private
    @property
    def private_property(self):
        return self._value

@friend(Target)
class Friend:
    def access_property(self, target):
        # Friend can access private property
        value = target.private_property
        return f"Accessed: {value}"

target = Target("secret")
friend = Friend()
result = friend.access_property(target)  # Works
```

\n</details><details>\n<summary><strong>System Management</strong></summary>## System Management

### Runtime Control

```python
from limen import (
    enable_enforcement, 
    disable_enforcement, 
    is_enforcement_enabled,
    get_access_control_system
)

class Base:
    @private
    def _private_method(self):
        return "private"

obj = Base()

# Normal enforcement
try:
    obj._private_method()  # PermissionDeniedError
except PermissionDeniedError:
    print("Access blocked")

# Disable enforcement (useful for testing)
disable_enforcement()
result = obj._private_method()  # Now works
print(f"Access allowed: {result}")

# Re-enable enforcement
enable_enforcement()
# obj.secret_method()  # PermissionDeniedError again

# Check enforcement status
print(f"Enforcement enabled: {is_enforcement_enabled()}")
```

### System Metrics and Debugging

```python
from limen.system import get_access_control_system

# Get system instance for advanced operations
access_control = get_access_control_system()

# Check enforcement status
print(f"Enforcement enabled: {access_control.enforcement_enabled}")

# Get friendship relationships count
friendship_manager = access_control._friendship_manager
print(f"Total friend relationships: {friendship_manager.get_friends_count()}")
print(f"Classes with friends: {friendship_manager.get_relationships_count()}")

# Reset system state (useful for testing)
from limen import reset_system
reset_system()
```

\n</details><details>\n<summary><strong>Error Handling</strong></summary>## Error Handling

Limen provides comprehensive, contextual exception types with enhanced error messages that include actual code suggestions and detailed explanations.

### Exception Types

```python
from limen.exceptions import (
    LimenError,                  # Base exception for all Limen errors
    PermissionDeniedError,       # Access denied to private/protected members
    DecoratorConflictError,      # Conflicting access level decorators
    DecoratorUsageError,         # Incorrect decorator usage
)
```

#### LimenError
Base exception class for all Limen access control errors. All other Limen exceptions inherit from this.

#### PermissionDeniedError
Raised when attempting to access private or protected members from unauthorized contexts.

```python
class SecureClass:
    @private
    def secret_method(self):
        return "secret"

try:
    obj = SecureClass()
    obj.secret_method()  # Unauthorized access
except PermissionDeniedError as e:
    print(f"Access denied: {e}")
    # Output: Access denied to private method secret_method
```

#### DecoratorConflictError
Raised when conflicting access level decorators are applied to the same method. Provides enhanced error messages with actual code suggestions and function body extraction.

```python
# This will raise an error during class creation
try:
    class ConflictClass:
        @private
        @protected  # Conflicting access levels
        def conflicted_method(self, data: str) -> str:
            return f"processing {data}"
except DecoratorConflictError as e:
    print(f"Decorator conflict: {e}")
    # Enhanced output shows:
    # Conflicting access level decorators on conflicted_method(): 
    # already has @private, cannot apply @protected.
    # Did you mean:
    # @protected
    # def conflicted_method(self, data: str) -> str:
    #     return f"processing {data}"
    # ?
```

#### DecoratorUsageError  
Raised when decorators are used incorrectly (wrong context, invalid syntax, etc.). Provides contextual suggestions based on the specific misuse.

```python
# Invalid decorator usage examples:

# 1. Module-level function (not allowed)
try:
    @private  # Cannot use on module-level function
    def module_function():
        pass
except DecoratorUsageError as e:
    print(f"Invalid usage: {e}")
    # Output: @private cannot be applied to module-level functions. 
    # Access control decorators can only be used on class methods.
    # Did you mean to put this function inside a class?

# 2. Bare class decoration (missing inheritance target)
try:
    @private  # Missing class argument
    class MyClass:
        pass
except DecoratorUsageError as e:
    print(f"Invalid usage: {e}")
    # Output: @private cannot be applied to a class without specifying a class to inherit from.
    # Did you mean: @private(BaseClass) ?

# 3. Duplicate decorator application
try:
    class DuplicateClass:
        @private
        @private  # Applied twice
        def duplicate_method(self):
            return "data"
except DecoratorConflictError as e:
    print(f"Duplicate decorator: {e}")
    # Output: @private was applied to duplicate_method() more than once!
    # Did you mean:
    # @private
    # def duplicate_method(self):
    #     return "data"
    # ?
```

### Enhanced Error Messages

Limen's error system provides contextual, helpful error messages that include:

- **Actual function signatures** with type annotations
- **Real function body content** (not just "pass")
- **Specific suggestions** for fixing the error
- **Contextual help** based on the type of mistake

```python
# Example with complex method signature
class ExampleClass:
    @property
    @private
    @protected  # Conflict error
    def complex_property(self) -> Dict[str, int]:
        return {"count": 42, "status": 1}

# Error message will show:
# Conflicting access level decorators on complex_property: 
# already has @private, cannot apply @protected.
# Did you mean:
# @property
# @protected  
# def complex_property(self) -> Dict[str, int]:
#     return {"count": 42, "status": 1}
# ?
```

### Property vs Method Formatting

Error messages intelligently format target names based on the member type:
- **Methods**: Show with parentheses `method_name()`
- **Properties**: Show without parentheses `property_name`

```python
# Property error (no parentheses)
class MyClass:
    @property
    @private
    @private  # Duplicate
    def my_prop(self):
        return "value"
# Error: @private was applied to my_prop more than once!

# Method error (with parentheses)  
class MyClass:
    @private
    @private  # Duplicate
    def my_method(self):
        return "value"
# Error: @private was applied to my_method() more than once!
```

### Error System Architecture

Limen's error system is built with a modular, maintainable architecture:

- **`method_utils.py`**: Method introspection utilities
  - `MethodInspector`: Extracts method types, arguments, and decorators with type hints
  - `FunctionBodyExtractor`: Extracts actual function implementation code  
  - `TargetFormatter`: Formats method names appropriately (with/without parentheses)

- **`message_generators.py`**: Contextual message generation
  - `MessageGenerator`: Creates detailed, helpful error messages with code suggestions
  - Handles different error scenarios with specific, actionable advice

- **`limen_errors.py`**: Clean, focused exception classes
  - Each exception focuses on its core responsibility
  - Uses composition for shared functionality
  - Easy to extend and maintain

This modular design ensures that error messages are consistent, helpful, and maintainable as the system grows.

\n</details><details>\n<summary><strong>Testing and Development</strong></summary>## Testing and Development

### Testing with Enforcement Control

```python
import unittest
from limen import disable_enforcement, enable_enforcement

class TestSecureClass(unittest.TestCase):
    def setUp(self):
        # Disable enforcement for easier testing
        disable_enforcement()
    
    def tearDown(self):
        # Re-enable enforcement
        enable_enforcement()
    
    def test_private_method_access(self):
        class TestClass:
            @private
            def _secret(self):
                return "secret"
        
        obj = TestClass()
        # This works because enforcement is disabled
        result = obj._secret()
        self.assertEqual(result, "secret")

# Or use context manager approach
from limen.system import get_access_control_system

def test_with_disabled_enforcement():
    access_control = get_access_control_system()
    original_state = access_control.enforcement_enabled
    
    try:
        access_control.enforcement_enabled = False
        # Test code here with enforcement disabled
        pass
    finally:
        access_control.enforcement_enabled = original_state
```

### Debugging Friend Relationships

```python
from limen.system import get_access_control_system

class TargetClass:
    @private
    def secret(self):
        return "secret"

@friend(TargetClass)
class FriendClass:
    pass

# Debug friendship relationships
access_control = get_access_control_system()
friendship_manager = access_control._friendship_manager

print(f"Total friends: {friendship_manager.get_friends_count()}")
print(f"Classes with friends: {friendship_manager.get_relationships_count()}")

# Check if specific friendship exists
is_friend = friendship_manager.is_friend(TargetClass, FriendClass)
print(f"FriendClass is friend of TargetClass: {is_friend}")
```

\n</details><details>\n<summary><strong>Requirements</strong></summary>## Requirements

- **Python 3.12+**
- **No external dependencies** for core functionality
- **Optional development dependencies** for testing and development

\n</details><details>\n<summary><strong>Development Setup</strong></summary>## Development Setup

### Clone and Setup

```bash
git clone https://github.com/Ma1achy/Limen.git
cd Limen
pip install -e .[dev]
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=limen

# Run specific test categories
pytest -m access_control      # Access control tests
pytest -m friend_methods      # Friend relationship tests
pytest -m inheritance         # Inheritance tests
pytest -m edge_cases          # Edge cases and boundary tests
```

### Development Commands

```bash
# Format code
black limen/ tests/

# Type checking
mypy limen/

# Lint code
flake8 limen/ tests/
```

\n</details><details>\n<summary><strong>Contributing</strong></summary>## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

### Development Guidelines

1. **Add tests** for new features
2. **Update documentation** for API changes
3. **Follow code style** (Black formatting, type hints)
4. **Ensure compatibility** with Python 3.8+

\n</details><details>\n<summary><strong>License</strong></summary>## LicenseMIT License - see [LICENSE](LICENSE) file for details.</details>