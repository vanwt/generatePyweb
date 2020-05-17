"""
wsgi -> application -> router -> request -> view
处理 environ 中的参数
data,method...
"""


#
# class lazyproperty:
#     def __init__(self, func):
#         self.func = func
#
#     def __get__(self, instance, cls):
#         print('ins', instance)
#         value = self.func(instance)
#         print('fun_name', self.func.__name__, self.func)
#         setattr(instance, self.func.__name__, value)
#         print('val', value)
#         return value


def lazyproperty(func):
    name = "__" + func.__name__

    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value

    return lazy


class Request(object):
    def __init__(self, environ):
        self.environ = environ
        self.path = environ["PATH_INFO"]
        self.method = environ['REQUEST_METHOD'].upper()
        self.data = {}
        self._cookie = environ.get("HTTP_COOKIE", None)
        #
        # for k, v in environ.items():
        #     print(k, v)

    def parsing(self, parsers):
        """ 根据解析器解析数据 """
        for parser in parsers:

            p = parser(self.environ)
            if p.is_par():
                self.data.update(p.parser())

    # @lazyproperty
    @property
    def cookie(self):
        if self._cookie is None:
            return {}
        # 对cookie格式化
        return parser_cookie(self._cookie)


def parser_cookie(cookie):
    data = {}
    for c in cookie.split(";"):
        key, *value = c.strip().split("=")
        if '[' in value and ']' in value or "{" in value and "}" in value:
            value = eval(value.replace("null", "None").replace("undefined", "None"))
            data.update(value)
        else:
            data.update({key: value})

    return data
