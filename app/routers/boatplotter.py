import json
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from app.internal.boatplotting import create_polar_diagram, plot_tws_group_fits_polar

boatplotter_router = APIRouter()
from app.models import InputData, JsonInputData


@boatplotter_router.post("/api")
async def plotapi(body: InputData):
    config = body.config
    fig = create_polar_diagram(body.data, config)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@boatplotter_router.post("/jsonapi")
async def jsonapi(body: JsonInputData):
    config = body.config
    raw_data = json.loads(body.data)
    data = []
    for entry in raw_data:
        try:
            data.append(
                {
                    "tws": int(np.round(float(entry.get("tws")))),
                    "twa": float(entry.get("twa")),
                    "stw": float(entry.get("stw")),
                    "sog": float(entry.get("sog")),
                }
            )
        except AttributeError as e:
            print(e)
            print(entry)

    df = pd.DataFrame(data)
    df = df.sort_values("tws")
    # pylint: disable=unsubscriptable-object
    exclude = config.exclude if config.exclude else []
    df = df[~df["tws"].isin(exclude)]
    fig = plot_tws_group_fits_polar(df, config)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@boatplotter_router.get("/boatplotter")
def get_boatplot():
    return FileResponse("static/boatplot.html")
