from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.models import BoatPlotterConfig, JsonBoatPlotterConfig


def plot_tws_group_fits_polar(df, config: JsonBoatPlotterConfig):
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(12, 8))

    df_sorted = df.sort_values(by=["tws", "twa"])

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

        if not config.smooth_plot:
            ax.plot(np.radians(tws_df["twa"]), tws_df["stw"], label=f"{tws}")

        else:
            color = None

            if config.original_points:
                test = ax.plot(
                    np.radians(tws_df["twa"]),
                    tws_df["stw"],
                    "o",
                )
                color = test[0].get_color()

            switch = config.method
            if switch == "regression":
                radius_fit, theta_fit = create_polynomial_fit(
                    tws_df["stw"], tws_df["twa"], config.degree
                )
            elif switch == "moving_average":
                radius_fit, theta_fit = create_moving_average(
                    tws_df["stw"], tws_df["twa"], config.degree
                )
            else:
                raise ValueError("Invalid method")

            if color:
                ax.plot(theta_fit, radius_fit, label=f"{tws}", color=color)
            else:
                ax.plot(theta_fit, radius_fit, label=f"{tws}")

    # Plot customizations
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    plt.legend(title="True Wind Speed (knots)", bbox_to_anchor=(1.2, 0.9), fontsize=12)
    plt.title(config.name, y=1.1, fontsize=20)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return buf


def create_moving_average(radius, theta, window_size):
    rolling_avg = radius.rolling(window=window_size, center=True).mean()

    return rolling_avg, np.radians(theta)


def create_polynomial_fit(radius, theta, degree):
    coeffs = np.polyfit(np.radians(theta), radius, degree)
    polynomial = np.poly1d(coeffs)

    # Create a range of x values (in radians) for plotting the fit line
    theta_fit = np.linspace(np.radians(theta.min()), np.radians(theta.max()), 500)
    radius_fit = polynomial(theta_fit)

    return radius_fit, theta_fit


def create_polar_diagram(
    data,
    config: BoatPlotterConfig,
):
    plot_title = config.name
    smooth_plot = config.smooth_plot
    original_points = config.original_points
    degree = config.degree
    to_zero = config.to_zero

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={"polar": True})

    # Plot settings
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)

    data = [[float(num) for num in line.split()] for line in data.strip().split("\n")]

    for row in data:
        tws = int(row[0])
        angles = np.radians(row[1::2])
        speeds = row[2::2]

        if not smooth_plot:
            ax.plot(angles[1:], speeds[1:], label=f"{tws}")

        else:
            coeffs = np.polyfit(angles, speeds, degree)
            polynomial = np.poly1d(coeffs)

            switch = config.method
            # why enum, not even exauhstive
            if switch == "regression":
                if to_zero:
                    fitted_angles = np.linspace(min(angles), max(angles), 300)
                else:
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
            if switch == "moving_average":
                color = None
                if original_points:
                    test = ax.plot(angles[1:], speeds[1:], "o")
                    color = test[0].get_color()
                rolling_avg = (
                    pd.Series(speeds).rolling(window=degree, center=True).mean()
                )

                if color:
                    ax.plot(angles, rolling_avg, label=f"{tws}", color=color)
                else:
                    ax.plot(angles, rolling_avg, label=f"{tws}")

    box = ax.get_position()
    ax.set_position([box.x0 - 0.1, box.y0, box.width, box.height])
    ax.legend(title="True Wind Speed (knots)", bbox_to_anchor=(1.2, 0.9), fontsize=12)

    plt.title(plot_title, y=1.1, fontsize=20)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return buf
