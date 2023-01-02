from fastapi import Depends
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse

statusrouter = APIRouter(tags=['status'])
templates = Jinja2Templates(directory='./status/templates')

@statusrouter.route('/', methods=['GET', 'POST'])
def show(page):
    try:
        return render_template(f'pages/{page}.html')
    except TemplateNotFound:
        abort(404)