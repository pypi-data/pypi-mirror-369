"""
Tennant Method (Montana Method) for Environmental Flow Estimation.
"""

import pandas as pd
import matplotlib.pyplot as plt
from .base import BaseHydrologicalMethod

class Tennant(BaseHydrologicalMethod):
    """
    Tennant method based on percentages of mean annual flow (MAF).
    """

    def __init__(self, flow_data: pd.Series):
        self.flow_data = flow_data.dropna()
        self.result = None

    def calculate(self):
        maf = self.flow_data.mean()
        levels = {
            "Poor (10%)": 0.1,
            "Fair (20%)": 0.2,
            "Good (30%)": 0.3,
            "Excellent (40%)": 0.4
        }
        self.result = pd.Series({k: v * maf for k, v in levels.items()})
        return self.result

    def plot(self):
        """
        Plot Tennant levels as a color-coded bar chart.
        """
        if self.result is None:
            raise ValueError("Run calculate() before plot().")

        # Define color for each level in the correct order
        color_map = {
            "Poor (10%)": "red",
            "Fair (20%)": "orange",
            "Good (30%)": "gold",
            "Excellent (40%)": "green"
        }

        colors = [color_map.get(label, "gray") for label in self.result.index]

        self.result.plot(kind="bar", color=colors)
        plt.title("Tennant Environmental Flow Recommendations")
        plt.ylabel("Flow")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_with_levels(self):
        """
        Plot the streamflow time series with color-coded Tennant flow level lines.
        """
        if self.result is None:
            raise ValueError("Run calculate() before plot_with_levels().")

        if self.flow_data is None or self.flow_data.empty:
            raise ValueError("No streamflow data to plot.")

        # Drop missing values from time series
        ts = self.flow_data.dropna()

        # Color mapping based on category
        color_map = {
            "Poor (10%)": "red",
            "Fair (20%)": "orange",
            "Good (30%)": "gold",
            "Excellent (40%)": "green"
        }

        # Plot time series
        plt.figure(figsize=(12, 5))
        ts.plot(color="black", label="Streamflow", linewidth=1)

        # Plot Tennant levels with colors
        for label, value in self.result.items():
            color = color_map.get(label, "gray")
            plt.axhline(y=value, linestyle="--", color=color, label=label)

        plt.xlabel("Date")
        plt.ylabel("Flow")
        plt.title("Tennant Method: Streamflow with Environmental Flow Levels")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

