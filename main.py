import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from starlette.responses import HTMLResponse, JSONResponse
from src.api import register_routers


app = FastAPI(
    title="CBA Case Study",
    description="Case Study For User Analysis-ML-GenAI",
    docs_url="/cba/api/docs",
    redoc_url="/cba/api/redoc",
    openapi_url="/cba/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

 
@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exception:
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error. Encountered : {exception}"},
        )
    
@app.get("/cba/api/docs", include_in_schema=False)
async def swagger_ui_html() -> HTMLResponse:
    """
    Returns
    -------
    HTMLResponse
        the swager ui html page

    """
    
    return get_swagger_ui_html(
        openai_url=app.openapi_url,
        tittle="API Docs",
        swagger_ui_parameters={"syntaxHighlight.theme": "nord"}
    )


register_routers(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=16,
        log_level="warning",
    )












