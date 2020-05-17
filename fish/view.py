from .parser import BaseParser, UrlParser
from .response import ResponseBase, Json, MethodNotAllowResponse
from typing import Tuple


class BaseView:
    PARSER_CLASSES: Tuple[BaseParser] = (UrlParser,)
    SHOW_DOCUMENT: bool = False

    def __init__(self, request):
        request.parsing(self.PARSER_CLASSES)
        self.request = request

    def __call__(self):
        response_view = getattr(self, self.request.method.lower(), None)
        if response_view is None:
            resp = MethodNotAllowResponse()
            return resp()

        # 如果访问文档
        if self.SHOW_DOCUMENT and "doc" in self.request.data:
            resp = Json({"help": response_view.__doc__})
            return resp()

        resp = response_view(self.request)
        # 如果已经返回了response对象，则直接返回对象
        if resp is None:
            raise AttributeError("need some value !")

        if isinstance(resp, ResponseBase):
            return resp()

        return Json(resp)()


class View(BaseView):
    pass
