import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

with open("tests/data.json") as f:
    data = json.loads(json.load(f)["data"])


# max 120 knots, did it dumb, raise it to whatever you want
boat_data = [[] for _ in range(120)]
for entry in data:
    if entry.get("tws") is None:
        continue
    if entry.get("twa") is None:
        continue
    if entry.get("stw") is None:
        continue
    tws = entry["tws"]
    twa = entry["twa"]
    # sog = entry["sog"]
    sog = entry["stw"]
    boat_data[int(np.round(tws))].append((float(twa), float(sog)))


def average_speeds(data):
    for row in data:
        angle_speed_map = defaultdict(lambda: [0, 0])

        for angle, speed in row:
            angle = abs(float(angle))
            speed = float(speed)
            angle_speed_map[angle][0] += speed
            angle_speed_map[angle][1] += 1

        averaged_data = [
            (angle, total_speed / count)
            for angle, (total_speed, count) in angle_speed_map.items()
        ]

        row[:] = sorted(averaged_data, key=lambda x: x[0])
    return data


print("Got all the entries")
data = average_speeds(boat_data)
print("averaged the data")
_, ax = plt.subplots(figsize=(12, 8), subplot_kw={"polar": True})

# Plot settings
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_thetamin(0)
ax.set_thetamax(180)

for tws, row in enumerate(data):
    if tws != 16:
        continue

    if len(row) < 3:
        continue
    # row = sorted(row, key=lambda tup: abs(tup[0]))

    angles = [abs(float(entry[0])) for entry in row]
    speeds = [float(entry[1]) for entry in row]
    angles = list(np.radians(angles))

    # if not smooth_plot:
    #     ax.plot(angles, speeds, label=f"{tws}")

    # else:
    #     coeffs = np.polyfit(angles, speeds, degree)
    #     polynomial = np.poly1d(coeffs)

    #     fitted_angles = np.linspace(min(angles), max(angles), 300)
    #     fitted_speeds = polynomial(fitted_angles)

    #     color = None
    # if original_points:
    test = ax.plot(angles, speeds, "o")
    color = test[0].get_color()

    # if color:
    #     ax.plot(fitted_angles, fitted_speeds, label=f"{tws}", color=color)
    # else:
    #     ax.plot(fitted_angles, fitted_speeds, label=f"{tws}")

box = ax.get_position()
ax.set_position([box.x0 - 0.1, box.y0, box.width, box.height])
ax.legend(title="True Wind Speed (knots)", bbox_to_anchor=(1.2, 0.9), fontsize=12)

plt.title("plot_title", y=1.1, fontsize=20)

plt.savefig("funfunoriginal.png")
plt.show()
