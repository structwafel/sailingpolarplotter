import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from scipy import optimize
from scipy.interpolate import make_interp_spline
from statsmodels.nonparametric.smoothers_lowess import lowess

with open("tests/data.json") as f:
    raw_data = json.loads(json.load(f)["data"])


data = []
for entry in raw_data:
    try:
        data.append(
            {
                "tws": int(np.round(float(entry.get("tws")))),
                "twa": np.radians(float(entry.get("twa"))),
                "stw": float(entry.get("stw")),
                "sog": float(entry.get("sog")),
            }
        )
    except AttributeError as e:
        print(e)
        print(entry)

df = pd.DataFrame(data)
df = df[df["tws"] == 16]
print(df)
df.loc[-1] = [16, 0, 0, 0]
df.index = df.index + 1
df = df.sort_index()
# Sort the DataFrame by 'rad' for plotting
df_sorted = df.sort_values("twa")


# Create the figure with 4 subplots
# fig, axs = plt.subplots(2, 2, subplot_kw={"polar": True})
fig, axs = plt.subplots(2, 2, figsize=(14, 10), subplot_kw={"polar": True})
axs = axs.flatten()  # Flatten to 1D array for easy indexing

# Scatter plot
for ax in axs:
    ax.scatter(df_sorted["twa"], df_sorted["stw"], label="Data")


# 1. Linear Regression Line
slope, intercept = np.polyfit(df_sorted["twa"], df_sorted["stw"], 1)
axs[0].plot(
    df_sorted["twa"],
    slope * df_sorted["twa"] + intercept,
    label="Linear Fit",
    color="red",
)
axs[0].set_title("Linear Regression")

# 2. Polynomial Regression Line (e.g., 2nd degree)
p = np.poly1d(np.polyfit(df_sorted["twa"], df_sorted["stw"], 2))
axs[1].plot(
    df_sorted["twa"],
    p(df_sorted["twa"]),
    label="Polynomial Fit",
    color="red",
)
axs[1].set_title("Polynomial Regression")

# 3. Moving Average - using a simple rolling window approach
window_size = 5  # Set the window size to your preference
rolling_avg = df_sorted["stw"].rolling(window=window_size, center=True).mean()
axs[2].plot(
    df_sorted["twa"],
    rolling_avg,
    label="Moving Average",
    color="red",
)
axs[2].set_title("Moving Average")

# 4. LOWESS - Locally Weighted Scatterplot Smoothing
lowess_results = lowess(df_sorted["stw"], df_sorted["twa"], frac=0.1)
lowess_x = list(zip(*lowess_results))[0]
lowess_y = list(zip(*lowess_results))[1]
axs[3].plot(
    lowess_x,
    lowess_y,
    label="LOWESS",
    color="red",
)
axs[3].set_title("LOWESS")

# Set theta range from 0 to 180 degrees and other settings for all subplots
for ax in axs:
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_zero_location("N")  # Set North to the top of the plot
    ax.set_theta_direction(-1)  # Set angles to increase clockwise
    ax.legend()

# Adjust the layout so that everything fits without overlap
plt.tight_layout()

# Show the plot
plt.show()
plt.savefig("funfun123.png")

plt.show()
