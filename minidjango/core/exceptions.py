"""
Global MiniDjango exception and warning classes.
"""

__author__ = 'pahaz'


class MiniDjangoRuntimeWarning(RuntimeWarning):
    pass


class ObjectDoesNotExist(Exception):
    """The requested object does not exist"""
    pass


class MultipleObjectsReturned(Exception):
    """The query returned multiple objects
    when only one was expected."""
    pass


class PermissionDenied(Exception):
    """The user did not have permission to do that"""
    pass


class ViewDoesNotExist(Exception):
    """The requested view does not exist"""
    pass


class ImproperlyConfigured(Exception):
    """MiniDjango is somehow improperly configured"""
    pass


class ValidationError(Exception):
    """An error while validating data."""
    pass
