import json
from typing import List


class ResponseBase:
    status_code: int = 200
    content_type: str = "text/plain"
    msg: str = "OK"
    content: str = ""
    encoding = "utf-8"

    def __init__(self, content="", content_type: str = None, status: int = None, headers: List[tuple] = None,
                 encoding: str = None):
        self.headers = []
        if content:
            self.content = content
        if status is not None:
            try:
                self.status_code = int(status)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

        if not 100 <= self.status_code <= 599:
            raise ValueError('HTTP status code must be an integer from 100 to 599.')

        if content_type:
            self.content_type = content_type
        if encoding:
            self.encoding = encoding

    def response_text(self):
        """ 数据进行转码 """
        return self.content.encode(self.encoding)

    def set_cookie(self, name: str, value, second: int = None, path: str = "/"):
        """
        Set-Cookie: name=yunwei; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Path=/;
        "%a, %d %b %Y %H:%M:%S GMT"
        datetime.utcnow().strftime(f)
        """
        fmt = "{name}={value}; Path={path};".format(name=name, value=value, path=path)
        if second:
            fmt += " Expires={date}".format(date=second)

        # 加入请求头
        self.headers.append(("Set-Cookie", fmt))

    def __call__(self):
        msg = "{status} {msg}".format(status=self.status_code, msg=self.msg)
        # headers 最后生成
        self.headers.append(("Content-Type", "{ct}; charset={ed}".format(ct=self.content_type, ed=self.encoding)))

        def view(environ, start_response):
            start_response(msg, self.headers)
            yield self.response_text()

        return view


class TemplateResponse(ResponseBase):
    content_type = "text/html"

    def __init__(self, template_name: str = None, encoding: str = None):
        super(TemplateResponse, self).__init__(status=200)
        if encoding:
            self.encoding = encoding
        if template_name:
            self.file_to_response(template_name)

    def file_to_response(self, name):
        with open(name, "r", encoding="UTF-8", errors="ignore") as f:
            self.content = f.read()


class Text(ResponseBase):
    pass


class Json(ResponseBase):
    content_type = "application/json"

    def response_text(self):
        return json.dumps(self.content, ensure_ascii=False).encode("utf-8")


class Xml(ResponseBase):
    content_type = "application/xml"


class MethodNotAllowResponse(Json):
    status_code = 405
    msg = "Method Not Found"
    content = {"error": "Method Not Found"}


class NotFoundResponse(Json):
    status_code = 404
    msg = "Not Found Error"
    content = {"error": "404 Not Found !"}


class Html(ResponseBase):
    content_type = "text/html"


class CssLoader(ResponseBase):
    content_type = "text/css"
    encoding = "utf-8"


class ImageLoader(ResponseBase):
    pass
