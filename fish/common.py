import os
from typing import List


class TemplateLoder:
    def __init__(self, template_dir_name: str = "template"):
        self.cwd = os.getcwd()
        self._template_dir_name = template_dir_name
        self.template_path = os.path.join(self.cwd, self.template_path_name)
        self.suffix = ".html"

    def make_tmp_path(self, path):
        if "/" in path:
            path = path.split("/")
        else:
            path = [path]
        return path

    @property
    def template_path_name(self):
        return self._template_dir_name

    @template_path_name.setter
    def template_path_name(self, name):
        self._template_dir_name = name
        self.template_path = os.path.join(self.cwd, name)

    def __call__(self, html_file_name: str = None):
        if not html_file_name:
            raise AttributeError("Please fill in the Html file name!")
        if not html_file_name.endswith(self.suffix):
            html_file_name += self.suffix
        return os.path.join(self.template_path, *self.make_tmp_path(html_file_name))


class StaticLoader(object):
    suffix = ["*"]

    types = {
        "css": "text/css",
        "js": "application/javascript",
        "html": "text/html",
        "txt": "text/plan",
        "png": "image/png",
        "json": "application/json",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "jpe": "image/jpeg"
    }

    def __init__(self, directory: str, url: str, suffix: List[str] = None):
        self.cwd = os.getcwd()
        self.request = None
        self.file_path = None
        self.file_name = None
        self.is_exist = False
        self.header = []
        self.static_directory = os.path.join(self.cwd, directory)
        if not os.path.isdir(self.static_directory):
            raise FileExistsError("{dir} Not a directory !".format(dir=directory))
        self.static_url = url if url[-1] == "/" else url + "/"
        if suffix:
            self.suffix = suffix

    def __call__(self, request):
        self.init_request(request)
        msg: str = self.get_status()
        self.get_header()
        data: bytes = self.get_data() if self.is_exist else b"<h1>404 Not Found !</h1>"

        def view(environ, start_response):
            start_response(msg, self.header)
            yield data

        return view

    def init_request(self, request):
        path = request.path[len(self.static_url):]
        path = [p for p in path.split("/") if p]

        self.file_name = path[-1]
        self.file_path = os.path.join(self.static_directory, *path)

    def get_header(self):
        # 判断 path的请求类型返回对应的content-type

        if not self.is_exist or "." not in self.file_name:
            self.header = [("Content-Type", "text/html; charset=utf-8")]
        else:
            suffix = self.file_name.split(".")[-1]
            self.header = [("Content-Type", self.types.get(suffix, "text/html") + "; charset=utf-8")]

    def get_status(self):
        """
        根据判断有没有这个文件返回 404 或200 ok
        :return defalut 404  Not Found Error
        """
        if os.path.isfile(self.file_path):
            self.is_exist = True
            return "200 OK"
        return "404 Not Found Error"

    def get_data(self):
        """
        打开文件( rb encode="utf-8")，返回文件内容
        """
        f = open(self.file_path, "rb")
        data = f.read()
        f.close()
        self.header.append(("content-length", str(len(data))))
        return data


class Config:
    cwd = os.getcwd()
    template_path_name = "template"
    template_path = os.path.join(cwd, template_path_name)
    static_dir_name = "static"
    static_path = os.path.join(cwd, static_dir_name)
