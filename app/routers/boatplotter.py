import json
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import APIRouter, Response

from app.internal.boatplotting import plot_tws_group_fits_polar

boatplotter_router = APIRouter()
from app.models import JsonInputData


@boatplotter_router.get("/boatplotter/jsonapi")
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
    df = df[~df["tws"].isin(config.exclude)]
    print(df)
    fig = plot_tws_group_fits_polar(df, config)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)  # Close the figure to free memory
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


@boatplotter_router.get("/boatplotter/plot.png", response_class=Response)
def get_plot(json: JsonInputData):
    fig, ax = plt.subplots()  # Create your plot with matplotlib
    # Plotting code here...
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(content=output.getvalue(), media_type="image/png")
