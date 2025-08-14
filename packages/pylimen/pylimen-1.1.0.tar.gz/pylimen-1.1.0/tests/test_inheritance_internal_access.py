"""
Tests for inheritance-based internal access control.

This module tests scenarios where derived classes call parent class constructors
and methods that internally access private methods. These are legitimate internal
calls that should be allowed despite access control restrictions.
"""
import pytest
from limen import protected, private
from limen.exceptions import PermissionDeniedError


class TestInheritanceInternalAccess:
    """Test inheritance scenarios with internal private method access"""

    def test_exact_case_from_a_py(self):
        """Test the exact failing case from a.py - should now work"""
        
        class Base:
            @protected
            def _method(self):
                pass

        @private(Base)
        class Derived(Base):
            def __init__(self):
                # This should work - internal call to private method from same class
                self.result = self.__another_method()

            def __another_method(self):
                return "success"

        class Wrapper(Derived):
            def __init__(self):
                # This should work - calling parent constructor that internally uses private methods
                super().__init__()
        
        # This should not raise any exceptions
        obj = Wrapper()
        assert obj.result == "success"

    def test_private_method_access_in_constructor(self):
        """Test private method access within constructor"""
        
        class Base:
            def __init__(self):
                # Internal access to private method should work
                self.data = self.__private_helper()
            
            def __private_helper(self):
                return "private_data"

        class Derived(Base):
            def __init__(self):
                super().__init__()  # Should work - calls Base.__init__ which uses private method
        
        obj = Derived()
        assert obj.data == "private_data"

    def test_private_method_chain_calls(self):
        """Test chain of private method calls within inheritance"""
        
        class Base:
            def __init__(self):
                self.result = self.__method_a()
            
            def __method_a(self):
                return self.__method_b()
            
            def __method_b(self):
                return "chain_result"

        class Derived(Base):
            def __init__(self):
                super().__init__()
        
        obj = Derived()
        assert obj.result == "chain_result"

    def test_multiple_inheritance_with_private_methods(self):
        """Test multiple inheritance with private method access"""
        
        class BaseA:
            def __init__(self):
                self.a_data = self.__private_a()
            
            def __private_a(self):
                return "a_private"

        class BaseB:
            def __init__(self):
                self.b_data = self.__private_b()
            
            def __private_b(self):
                return "b_private"

        class MultiDerived(BaseA, BaseB):
            def __init__(self):
                BaseA.__init__(self)
                BaseB.__init__(self)
        
        obj = MultiDerived()
        assert obj.a_data == "a_private"
        assert obj.b_data == "b_private"

    def test_deep_inheritance_chain(self):
        """Test deep inheritance chain with private method access"""
        
        class GrandParent:
            def __init__(self):
                self.gp_data = self.__grandparent_private()
            
            def __grandparent_private(self):
                return "grandparent"

        class Parent(GrandParent):
            def __init__(self):
                super().__init__()
                self.p_data = self.__parent_private()
            
            def __parent_private(self):
                return "parent"

        class Child(Parent):
            def __init__(self):
                super().__init__()
                self.c_data = self.__child_private()
            
            def __child_private(self):
                return "child"
        
        obj = Child()
        assert obj.gp_data == "grandparent"
        assert obj.p_data == "parent"
        assert obj.c_data == "child"

    def test_private_inheritance_with_internal_access(self):
        """Test private inheritance decorator with internal method access"""
        
        class Base:
            @protected
            def _protected_method(self):
                return "protected"
            
            def __init__(self):
                self.internal_data = self.__private_init_helper()
            
            def __private_init_helper(self):
                return "internal"

        @private(Base)
        class Derived(Base):
            def __init__(self):
                super().__init__()
                self.derived_data = self.__derived_private()
            
            def __derived_private(self):
                return "derived_internal"
        
        obj = Derived()
        assert obj.internal_data == "internal"
        assert obj.derived_data == "derived_internal"

    def test_protected_inheritance_with_internal_access(self):
        """Test protected inheritance decorator with internal method access"""
        
        class Base:
            def __init__(self):
                self.base_result = self.__base_private()
            
            def __base_private(self):
                return "base_private"

        @protected(Base)
        class Derived(Base):
            def __init__(self):
                super().__init__()
                self.derived_result = self.__derived_private()
            
            def __derived_private(self):
                return "derived_private"
        
        obj = Derived()
        assert obj.base_result == "base_private"
        assert obj.derived_result == "derived_private"

    def test_internal_access_from_public_methods(self):
        """Test private method access from public methods in inheritance"""
        
        class Base:
            def public_method(self):
                return self.__private_helper()
            
            def __private_helper(self):
                return "helper_result"

        class Derived(Base):
            def derived_public(self):
                # Calling inherited public method that uses private method
                return self.public_method()
        
        obj = Derived()
        assert obj.derived_public() == "helper_result"

    def test_external_access_still_blocked(self):
        """Ensure external access to private methods is still blocked"""
        
        class Base:
            def __init__(self):
                self.result = self.__private_method()
            
            def __private_method(self):
                return "private"

        @private(Base)  # Apply access control
        class Derived(Base):
            def __init__(self):
                super().__init__()
        
        obj = Derived()
        
        # External access should still be blocked (implicit access control raises PermissionError)
        with pytest.raises(PermissionError, match="Access denied to private method"):
            obj._Base__private_method()

    def test_direct_subclass_access_blocked(self):
        """Ensure direct access from subclass methods is still blocked"""
        
        class Base:
            def __init__(self):
                self.result = self.__private_method()
            
            def __private_method(self):
                return "private"

        @private(Base)  # Apply access control
        class Derived(Base):
            def __init__(self):
                super().__init__()
            
            def try_direct_access(self):
                # Direct access from subclass should be blocked
                return self._Base__private_method()
        
        obj = Derived()
        
        # Implicit access control raises PermissionError for name mangling bypass
        with pytest.raises(PermissionError, match="Access denied to private method"):
            obj.try_direct_access()

    def test_friend_access_preserved_in_inheritance(self):
        """Test that friend access still works with inheritance scenarios"""
        
        class Target:
            def __init__(self):
                self.data = self.private_data()
            
            @private
            def private_data(self):  # Use explicit decorator instead of name mangling
                return "secret"

        class TargetDerived(Target):
            def __init__(self):
                super().__init__()

        # Create a friend class
        from limen import friend
        
        @friend(Target)
        class FriendClass:
            def access_target(self, target):
                return target.private_data()
        
        # Test inheritance works
        derived_obj = TargetDerived()
        assert derived_obj.data == "secret"
        
        # Test friend access still works
        friend_obj = FriendClass()
        result = friend_obj.access_target(derived_obj)
        assert result == "secret"

    def test_implicit_access_control_inheritance(self):
        """Test inheritance with implicit access control applied"""
        
        from limen.utils.implicit import apply_implicit_access_control
        
        class Base:
            def __init__(self):
                self.result = self.__private_method()
            
            def __private_method(self):
                return "implicit_private"

        # Apply implicit access control
        apply_implicit_access_control(Base)

        class Derived(Base):
            def __init__(self):
                super().__init__()
        
        # Should work - internal access via inheritance
        obj = Derived()
        assert obj.result == "implicit_private"
        
        # External access should be blocked (implicit control raises PermissionError)
        with pytest.raises(PermissionError, match="Access denied to private method"):
            obj._Base__private_method()

    def test_complex_mixed_scenario(self):
        """Test complex scenario mixing explicit decorators, inheritance, and internal access"""
        
        class Base:
            def __init__(self):
                self.explicit_result = self.explicit_private()
                self.implicit_result = self.__implicit_private()
            
            @private
            def explicit_private(self):  # Remove __ to avoid mangling issues in tests
                return "explicit"
            
            def __implicit_private(self):
                return "implicit"

        @private(Base)
        class Derived(Base):
            def __init__(self):
                super().__init__()
                self.derived_result = self.__derived_method()
            
            def __derived_method(self):
                return "derived"
        
        obj = Derived()
        assert obj.explicit_result == "explicit"
        assert obj.implicit_result == "implicit"
        assert obj.derived_result == "derived"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError):
            obj.explicit_private()
        
        # Mangled name access blocked by explicit decorator (raises PermissionDeniedError)
        with pytest.raises(PermissionDeniedError, match="Access denied to @private method"):
            obj._Base__implicit_private()

    def test_property_access_in_inheritance(self):
        """Test private property access within inheritance"""
        
        class Base:
            def __init__(self, value):
                self._value = value
                # Access private property internally
                self.cached_value = self.__private_property
            
            @private
            @property
            def __private_property(self):
                return f"private_{self._value}"

        class Derived(Base):
            def __init__(self, value):
                super().__init__(value)
        
        obj = Derived("test")
        assert obj.cached_value == "private_test"
        
        # External access should be blocked
        with pytest.raises(PermissionDeniedError, match="Access denied to @private property"):
            _ = obj._Base__private_property

    def test_static_and_class_methods_inheritance(self):
        """Test static and class method access in inheritance scenarios"""
        
        class Base:
            def __init__(self):
                # Accessing static and class methods internally
                self.static_result = self.__private_static()
                self.class_result = self.__private_class()
            
            @private
            @staticmethod
            def __private_static():
                return "static_private"
            
            @private
            @classmethod
            def __private_class(cls):
                return "class_private"

        class Derived(Base):
            def __init__(self):
                super().__init__()
        
        obj = Derived()
        assert obj.static_result == "static_private"
        assert obj.class_result == "class_private"
