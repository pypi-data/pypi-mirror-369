"""
Generalized Environmental Flow Criteria (GEFC) Method
"""

import pandas as pd
import matplotlib.pyplot as plt
from .base import BaseHydrologicalMethod

class GEFC(BaseHydrologicalMethod):
    """
    Generalized Environmental Flow Criteria (GEFC) method.
    """

    def __init__(self, flow_data: pd.Series):
        self.flow_data = flow_data.dropna()
        self.result = None

    def calculate(self):
        mean_flow = self.flow_data.mean()
        self.result = pd.Series({
            "Low Flow (30%)": mean_flow * 0.3,
            "Moderate Flow (60%)": mean_flow * 0.6,
            "High Flow (100%)": mean_flow * 1.0
        })
        return self.result

    def plot(self):
        """
        Plot the GEFC thresholds as a bar chart.
        """
        if self.result is None:
            raise ValueError("Run calculate() before plot().")
        self.result.plot(kind="bar", color=["red", "orange", "green"])
        plt.title("GEFC Environmental Flow Recommendations")
        plt.ylabel("Flow")
        plt.tight_layout()
        plt.grid(True)
        plt.show()

    def plot_with_levels(self):
        """
        Overlay GEFC flow thresholds on the streamflow time series.
        """
        if self.result is None:
            raise ValueError("Run calculate() before plot_with_levels().")

        if self.flow_data is None or self.flow_data.empty:
            raise ValueError("No streamflow data to plot.")

        ts = self.flow_data.dropna()

        plt.figure(figsize=(12, 5))
        ts.plot(color="black", linewidth=1, label="Streamflow")

        color_map = {
            "Low Flow (30%)": "red",
            "Moderate Flow (60%)": "orange",
            "High Flow (100%)": "green"
        }

        for label, value in self.result.items():
            plt.axhline(y=value, linestyle="--", color=color_map.get(label, "gray"), label=label)

        plt.xlabel("Date")
        plt.ylabel("Flow")
        plt.title("GEFC Method: Streamflow with Environmental Flow Levels")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
