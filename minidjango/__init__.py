
VERSION = (0, 0, 1)
__author__ = 'pahaz'
__version__ = '.'.join(map(str, VERSION))


def setup():
    """
    Configure the settings (this happens as a side effect of accessing the
    first setting), configure logging and populate the app registry.
    """
    from minidjango.conf import settings
