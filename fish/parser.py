import json
import cgi
from urllib.parse import parse_qs


class BaseParser:
    def parser(self):
        pass

    def is_par(self):
        pass

    @staticmethod
    def parser_data(data):
        """ 处理 {'name': [b'cmd']} 为  {'name':'cmd'} """
        if not data:
            return data

        for k, v in data.items():
            if len(v) == 1 and isinstance(v, list):
                # 如果列表中只有一个数据时
                if isinstance(v[0], bytes):
                    data[k] = v[0].decode()
                else:
                    data[k] = v[0]
            if isinstance(v, bytes):
                data[k] = v.decode()
        return data


class FormParser(BaseParser):
    content_type = ["multipart/form-data", "application/x-www-form-urlencoded"]

    def __init__(self, environ):
        self.source = environ["wsgi.input"]
        content_length = environ.get("CONTENT_LENGTH")
        self.content_length = int(content_length) if content_length.isdigit() else 0
        self.ctype, pdict = cgi.parse_header(environ['CONTENT_TYPE'])
        if "boundary" in pdict:
            self.pdict = pdict
            if isinstance(pdict["boundary"], str):
                self.pdict['boundary'] = pdict['boundary'].encode()
        else:
            self.pdict = None

    def is_par(self):
        if self.ctype in self.content_type:
            return True
        return False

    def parser(self):
        # 判断请求体的类型 是否是form-data 类型
        if self.ctype == 'multipart/form-data' and self.pdict:
            data = cgi.parse_multipart(self.source, self.pdict)
            return self.parser_data(data)
        elif self.ctype == 'application/x-www-form-urlencoded' and self.content_length:
            query = self.source.read(self.content_length).decode()
            return self.parser_data(parse_qs(query))
        else:
            return {}


class UrlParser(BaseParser):
    def __init__(self, environ):
        self.query = environ["QUERY_STRING"]

    def is_par(self):
        return True

    def parser(self):
        query = parse_qs(self.query, keep_blank_values=False, strict_parsing=False, encoding="utf-8")

        return self.parser_data(query) if query else {}


class JsonParser(BaseParser):

    def __init__(self, environ):
        self.environ = environ
        self.content_type = None
        self.content_length = str(environ.get("CONTENT_LENGTH", 0))
        if self.content_length:
            self.content_length = int(self.content_length) if self.content_length.isdigit() else 0
        ctype = environ.get('CONTENT_TYPE', None)
        if ctype:
            self.content_type, pdict = cgi.parse_header(ctype)

    def is_par(self):
        """ 如果 content_length 大于0 说明有数据存在Body中 """

        if self.content_type in ("text/plain", "text/json", "application/json") and self.content_length:
            return True
        return False

    def parser(self):
        self.body = self.environ['wsgi.input'].read(self.content_length)
        query = json.loads(self.body)
        return query


class XMLParser(BaseParser):
    def __init__(self, environ):
        self.input = environ["wsgi.input"]
        self.content_type = None
        self.content_length = str(environ.get("CONTENT_LENGTH", 0))
        if self.content_length:
            self.content_length = int(self.content_length) if self.content_length.isdigit() else 0
        ctype = environ.get('CONTENT_TYPE', None)
        if ctype:
            self.content_type, pdict = cgi.parse_header(ctype)

    def is_par(self):
        if self.content_type in ("text/xml", "application/xml"):
            return True
        return False

    def parser(self):
        query = {}
        if self.content_length:
            data = self.input.read(self.content_length)
            # 得到的字节串
            query.update({"xml": data})
        return query
