import json
from collections import defaultdict

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

df = px.data.wind()
fig = px.line_polar(
    df,
    r="frequency",
    theta="direction",
    color="strength",
    line_close=True,
    color_discrete_sequence=px.colors.sequential.Plasma_r,
    template="plotly_dark",
)
fig.show()


def create_polar_diagram_plotly(
    data,
    plot_title,
    smooth_plot,
    original_points,
    degree,
    min_true_winds,
    max_true_winds,
    even,
    uneven,
):
    data = json.loads(data)
    boat_data = [[] for _ in range(120)]
    for entry in data:
        if (
            entry.get("tws") is None
            or entry.get("twa") is None
            or entry.get("stw") is None
        ):
            continue
        tws = int(np.round(entry["tws"]))
        twa = abs(float(entry["twa"]))
        stw = float(entry["stw"])
        boat_data[tws].append((twa, stw))

    def average_speeds(data):
        averaged_data = []
        for row in data:
            angle_speed_map = defaultdict(lambda: [0, 0])
            for angle, speed in row:
                angle_speed_map[angle][0] += speed
                angle_speed_map[angle][1] += 1
            averaged_data.append(
                [
                    (angle, total_speed / count)
                    for angle, (total_speed, count) in angle_speed_map.items()
                ]
            )
        return averaged_data

    data = average_speeds(boat_data)

    fig = go.Figure()

    for tws, row in enumerate(data):
        if tws < min_true_winds or tws > max_true_winds:
            continue
        if even and tws % 2 != 0:
            continue
        if uneven and tws % 2 == 0:
            continue
        if len(row) < 3:
            continue

        angles, speeds = zip(*sorted(row))
        angles = np.deg2rad(angles)  # Convert to radians for Plotly

        if smooth_plot:
            coeffs = np.polyfit(angles, speeds, degree)
            polynomial = np.poly1d(coeffs)
            fitted_angles = np.linspace(min(angles), max(angles), 300)
            fitted_speeds = polynomial(fitted_angles)
            fig.add_trace(
                go.Scatterpolar(
                    r=fitted_speeds,
                    theta=np.rad2deg(fitted_angles),
                    name=f"{tws} knots",
                )
            )
            if original_points:
                fig.add_trace(
                    go.Scatterpolar(
                        r=speeds,
                        theta=np.rad2deg(angles),
                        mode="markers",
                        name=f"{tws} knots (original)",
                    )
                )
        else:
            fig.add_trace(
                go.Scatterpolar(r=speeds, theta=np.rad2deg(angles), name=f"{tws} knots")
            )

    fig.update_layout(
        title=plot_title,
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, max(map(max, data)) + 2]  # Adjust axis range
            ),
            angularaxis=dict(direction="clockwise", thetaunit="degrees"),
        ),
        legend_title="True Wind Speed (knots)",
    )

    fig.show()


with open("tests/data.json") as f:
    data = json.load(f)
    data_json = data["data"]

# Example usage
# data_json = "..."  # Your JSON data here
create_polar_diagram_plotly(
    data_json, "Polar Diagram", True, True, 3, 5, 20, True, False
)
