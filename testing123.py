import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.internal.boatplotting import polynomial_fit

with open("tests/data.json") as f:
    raw_data = json.loads(json.load(f)["data"])

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
# df = df[df["tws"] == 16]

df_sorted = df.sort_values("tws")

# Set up the polar plot
plt.figure(figsize=(10, 8))
ax = plt.subplot(111, polar=True)

# Plot only for even 'tws' values
for tws in df_sorted["tws"].unique():
    if tws % 2 != 0:  # Skip odd 'tws' values
        continue

    tws_df = df_sorted[df_sorted["tws"] == tws]

    # Scatter plot of the raw data points
    if True:
        ax.scatter(
            np.radians(tws_df["twa"]),
            tws_df["stw"],
            # label=f"Scatter TWS {tws}",
        )

    # Fit the polynomial
    coeffs = np.polyfit(np.radians(tws_df["twa"]), tws_df["stw"], 1)
    polynomial = np.poly1d(coeffs)

    # Create a range of x values (in radians) for plotting the fit line
    twa_fit = np.linspace(
        np.radians(tws_df["twa"].min()),
        np.radians(tws_df["twa"].max()),
        500,
    )
    stw_fit = polynomial(twa_fit)

    # Plot the polynomial fit line
    ax.plot(
        twa_fit,
        stw_fit,
        label=f"TWS {tws}",
    )

# Plot customizations
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)  # Clockwise
ax.set_thetamin(0)  # Set the start of the plot to 0 degrees
ax.set_thetamax(180)  # Set the end of the plot to 180 degrees
plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
plt.title(
    f"Polar Plot with Polynomial Fit of Degree {1} for Even TWS Values"
)  # plt.savefig("filename.svg")
plt.savefig("filename.png")

print("saved plot")
# optional plot the scatter plot

# get the polynomial things
# plot the polunomial

# redo for the next tws
