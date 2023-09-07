import sqltap
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f'{settings.API_V1_STR}/openapi.json',
    debug=False if settings.ENVIRONMENT == 'prod' else True,
    docs_url=None if settings.ENVIRONMENT == 'prod' else '/docs',
    redoc_url=None if settings.ENVIRONMENT == 'prod' else '/redoc',
)


app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if settings.ENVIRONMENT.lower() == "dev":
    @app.middleware('http')
    async def add_sql_tap(request: Request, call_next):
        profiler = sqltap.start()
        response = await call_next(request)
        statistics = profiler.collect()
        sqltap.report(statistics, 'report.txt', report_format='text')
        return response


@app.get('/health', tags=['health-check'])
async def health():
    return {'message': 'ok!'}

from fastapi.templating import Jinja2Templates


@app.get("/sample-shop/{shop_name}")
def get_html(* , shop_name:str , request: Request):
    templates = Jinja2Templates(directory="/app/app/templates")
    name = "Platfo bot"
    
    # name =  "Hello my dear Fatemeh \N{kissing face} , I jus want to say I love you so much ❤️ and I miss you a lot"
    return  templates.TemplateResponse("shop.html" , {"request" : request , "name" : shop_name} )

