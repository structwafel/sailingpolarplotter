import os
from typing import Union

from fastapi import FastAPI

from .routers.boatplotter import boatplotter_router

print(os.environ["TESTENV"])

app = FastAPI()

app.include_router(boatplotter_router)
