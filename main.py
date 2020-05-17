from fish import Fish, TemplateLoder
from fish.response import Html,TemplateResponse

app = Fish()
app.static_dir = "static"
app.static_url = "/static"

tmp = TemplateLoder(template_dir_name="template")


@app.get("/")
def index(req):
    return TemplateResponse(tmp("index.html"))


if __name__ == '__main__':
    app.run(port=80)