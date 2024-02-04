import io
import json
import signal
from collections import defaultdict
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from app.models import BoatPlotterConfig


def parse_data_to_df(raw_data: str, speed: str = "stw"):
    raw_data_list: List[Dict[str, Any]] = json.loads(raw_data)
    data = []

    entry: Any
    for entry in raw_data_list:
        try:
            if all(key in entry for key in ["tws", "twa", speed]):
                data.append(
                    {
                        "tws": int(np.round(float(entry.get("tws")))),
                        "twa": np.radians(float(entry.get("twa"))),
                        speed: float(entry.get(speed)),
                        # "sog": float(entry.get("sog")),
                    }
                )
        except AttributeError as e:
            print(e)
            print(entry)

    return pd.DataFrame(data).sort_values("rad")


def plot_tws_group_fits_polar(df, config: BoatPlotterConfig):
    """
    For each 'tws' group in the dataframe, fit a polynomial of specified degree
    and plot the raw data points (optionally) and the polynomial fit line on a polar plot.

    Parameters:
    - df: pandas DataFrame with the data containing 'twa', 'stw', and 'tws'.
    - degree: The degree of the polynomial fit.
    - plot_scatter: Whether to plot the scatter plot of the raw data.
    """

    # Ensure DataFrame is sorted for plotting
    df_sorted = df.sort_values(["tws", "twa"])

    # Set up the polar plot
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(10, 8))
    # plt.figure(figsize=(10, 8))
    # ax = plt.subplot(111, polar=True)

    # Plot only for even 'tws' values
    for tws in df_sorted["tws"].unique():
        if config.even and tws % 2 != 0:
            continue
        if config.uneven and tws % 2 == 0:
            continue
        if config.min_true_winds > tws:
            continue
        if config.max_true_winds < tws:
            continue

        tws_df = df_sorted[df_sorted["tws"] == tws]

        # Scatter plot of the raw data points
        if config.original_points:
            ax.scatter(
                np.radians(tws_df["twa"]),
                tws_df["stw"],
                # label=f"Scatter TWS {tws}",
            )

        # TODO(lgx) switch statement for other fits
        radius_fit, theta_fit = create_polynomial_fit(
            tws_df["stw"],
            tws_df["twa"],
            config.degree,
        )

        # Plot the polynomial fit line
        ax.plot(
            theta_fit,
            radius_fit,
            label=f"{tws}",
        )

    # Plot customizations
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)  # Clockwise
    ax.set_thetamin(0)  # Set the start of the plot to 0 degrees
    ax.set_thetamax(180)  # Set the end of the plot to 180 degrees
    plt.legend(title="TWS (Kn)", loc="upper left", bbox_to_anchor=(1.05, 1))
    plt.title(config.name)

    return fig


def create_polynomial_fit(radius, theta, degree):
    coeffs = np.polyfit(np.radians(theta), radius, degree)
    polynomial = np.poly1d(coeffs)

    # Create a range of x values (in radians) for plotting the fit line
    theta_fit = np.linspace(np.radians(theta.min()), np.radians(theta.max()), 500)
    radius_fit = polynomial(theta_fit)

    return radius_fit, theta_fit


def create_regression_line(df: pd.DataFrame, degree: int = 1) -> pd.DataFrame:
    fig, ax = plt.subplots()
    ax = ax.flatten()
    slope, intercept = np.polyfit(df["twa"], df["stw"], degree)
    df["stw"] = slope * df["twa"] + intercept
    return df
    ax.plot(
        df["twa"],
        slope * df["twa"] + intercept,
        label="Linear Fit",
    )
    ax.set_title("Linear Regression")

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)


def polynomial_fit(df, x_column, y_column, degree, pre_filter=None, post_filter=None):

    # Apply pre-filtering if specified
    if pre_filter:
        for condition, value in pre_filter.items():
            df = df.query(f"{condition} == @value")

    # Perform the polynomial fit
    coeffs = np.polyfit(df[x_column], df[y_column], degree)
    polynomial = np.poly1d(coeffs)

    # Create a range of x-values for the fitted polynomial
    fitted_x = np.linspace(df[x_column].min(), df[x_column].max(), len(df) * 10)
    fitted_y = polynomial(fitted_x)

    # Convert fitted values to a DataFrame
    fit_df = pd.DataFrame({x_column: fitted_x, y_column: fitted_y})

    # Apply post-filtering if specified
    if post_filter:
        for condition, value in post_filter.items():
            fit_df = fit_df.query(f"{condition} == @value")

    return fit_df[x_column], fit_df[y_column]


def create_polar_diagram(
    data, plot_filename, plot_title, smooth_plot, original_points, degree
):
    # print("Creating polar diagram")
    # return
    _, ax = plt.subplots(figsize=(12, 8), subplot_kw={"polar": True})

    # Plot settings
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)

    for row in data:
        tws = row[0]
        angles = np.radians(row[1::2])
        speeds = row[2::2]

        if not smooth_plot:
            ax.plot(angles[1:], speeds[1:], label=f"{tws}")

        else:
            coeffs = np.polyfit(angles, speeds, degree)
            polynomial = np.poly1d(coeffs)

            fitted_angles = np.linspace(min(angles[1:]), max(angles[1:]), 300)
            fitted_speeds = polynomial(fitted_angles)

            color = None
            if original_points:
                test = ax.plot(angles[1:], speeds[1:], "o")
                color = test[0].get_color()

            if color:
                ax.plot(fitted_angles, fitted_speeds, label=f"{tws}", color=color)
            else:
                ax.plot(fitted_angles, fitted_speeds, label=f"{tws}")

    box = ax.get_position()
    ax.set_position([box.x0 - 0.1, box.y0, box.width, box.height])
    ax.legend(title="True Wind Speed (knots)", bbox_to_anchor=(1.2, 0.9), fontsize=12)

    plt.title(plot_title, y=1.1, fontsize=20)

    plt.savefig(plot_filename)
    return "Polar diagram created"
