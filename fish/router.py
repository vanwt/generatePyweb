from .errors import MethodNoteFoundError, NotFoundError
from typing import List, Callable


class PathMap():
    """
    {
        "/" : {
            "GET":view,
            "POST":view2
        }
    }
    """

    def __init__(self):
        self.path_map = {}

    def add(self, path: str, view: Callable, methods: List[str]):
        """ 不存在直接创建，已存在用update """
        if path not in self.path_map:
            self.path_map[path] = {method: view for method in methods}
        else:
            self.path_map[path].update({method: view for method in methods})

    def get(self, path: str, method: List[str]):
        """ 根据path查找 method 字典"""
        views = self.path_map.get(path, None)
        # 找不到路由
        if views is None:
            raise NotFoundError()
        # 找不到对应method方法
        func_view = views.get(method, None)
        if func_view is None:
            raise MethodNoteFoundError()
        return func_view

    def __repr__(self):
        return self.path_map


class StaticRoute():
    def __init__(self, request):
        pass

    def readFile(self, filename):
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
        return data
