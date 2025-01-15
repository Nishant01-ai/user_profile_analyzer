from fastapi.applications import FastAPI

from . import cba_router


def register_routers(app: FastAPI) -> FastAPI:

    prefix_summary = "/cba/ml"
    app.include_router(cba_router.router, prefix= prefix_summary)

    return app
