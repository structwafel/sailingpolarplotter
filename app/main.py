from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers.boatplotter import boatplotter_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(boatplotter_router)


@app.get("/")
async def root():
    return FileResponse("static/boatplot.html")
