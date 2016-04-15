
__author__ = 'pahaz'
_default = dict(
    DEBUG=False,
    MIDDLEWARE_CLASSES=[],
    DEFAULT_CONTENT_TYPE='text/html',
    DEFAULT_CHARSET='utf-8',
    PROPAGATE_EXCEPTIONS=True,
    ROUTER={},
)


class Settings(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            try:
                return _default[item]
            except KeyError:
                raise AttributeError('Setting "{}" is not set'.format(item))


settings = Settings()
