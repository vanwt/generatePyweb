from typing import List, Callable, Dict
from .router import PathMap
from .request import Request
from .response import NotFoundResponse, MethodNotAllowResponse
from .server import make_server
from .errors import MethodNoteFoundError, NotFoundError
from .parser import BaseParser
from .common import StaticLoader

METHODS = ["GET", "POST", "PUT", "DELETE"]


class Fish():
    request_class = Request
    static_url = ""
    static_dir = None

    def __init__(self):
        self.routes = PathMap()
        self.debug = True
        self.parser_map: dict = {}

    def add_routes(self, path: str, view: Callable, methods: List[str]):
        """
        添加路由
        :param path: url
        :param options:  methods 目前只有请求类型
        :return: None
        """
        # check methods
        for m in methods:
            if m not in METHODS:
                raise AttributeError("method must in {0!r}".format(METHODS))
        self.routes.add(path, view, methods)

    def route(self, path: str, parsers: List[BaseParser] = None, methods: List[str] = None):
        """
        装饰器
        @app.route("/",["GET"])
        def test(req):
            return "ok"

        @app.route("/",["POST"])
        def test2(req):
            return "ok"
        加入到路由表中

        """
        if not methods:
            raise AttributeError("If you don't fill in the methods, please use: @route.get()")

        # 解析器默认只有url解析
        parsers = parsers if parsers else ()

        # 存入解析器
        self.parser_map[path] = parsers

        def add_route(func: Callable):
            # 加入到路由表中
            self.add_routes(path, func, methods)
            return func

        return add_route

    def get(self, path: str, parsers: List[BaseParser] = None):
        """
            装饰器
            @app.get("/")
            def test(request):
                return "ok"

            @app.post("/")
            def test2(request):
                return "ok"
            加入到路由表中
        """
        # 解析器默认只有url解析
        parsers = parsers if parsers else ()

        # 存入解析器
        self.parser_map[path] = parsers

        def add_route(func):
            # 加入到路由表中
            self.add_routes(path, func, ["GET"])
            return func

        return add_route

    def post(self, path: str, parsers: List[BaseParser] = None):
        parsers = parsers if parsers else ()
        # 存入解析器
        self.parser_map[path] = parsers

        def add_route(func):
            # 加入到路由表中
            self.add_routes(path, func, ["POST"])
            return func

        return add_route

    def put(self, path: str, parsers: List[BaseParser] = None):
        parsers = parsers if parsers else ()

        # 存入解析器
        self.parser_map[path] = parsers

        def add_route(func):
            # 加入到路由表中
            self.add_routes(path, func, ["PUT"])
            return func

        return add_route

    def delete(self, path: str, parsers: List[BaseParser] = None):
        parsers = parsers if parsers else ()

        # 存入解析器
        self.parser_map[path] = parsers

        def add_route(func):
            # 加入到路由表中
            self.add_routes(path, func, ["DELETE"])
            return func

        return add_route

    def get_response(self, environ: Dict, start_response: Callable):
        request = self.request_class(environ)
        # 查找存储的解析器
        # 没有就404
        func_parser = self.parser_map.get(request.path, None)
        # 对请求进行解析
        if func_parser:
            request.parsing(func_parser)

        # 静态文件
        if self.static_dir and request.path.startswith(self.static_url):
            resp = StaticLoader(directory=self.static_dir, url=self.static_url)(request)
            return resp(environ, start_response)
        try:
            view_func = self.routes.get(request.path, request.method)
            resp = view_func(request)()
        except NotFoundError:
            resp = NotFoundResponse()()
        except MethodNoteFoundError:
            resp = MethodNotAllowResponse()()
        return resp(environ, start_response)

    def run(self, host="127.0.0.1", port=8000, debug=True):
        self.debug = debug
        make_server((host, port), self)

    def __call__(self, environ: Dict, start_response: Callable):
        # 此处要返回一个handler
        return self.get_response(environ, start_response)


__all__ = "Fish"
