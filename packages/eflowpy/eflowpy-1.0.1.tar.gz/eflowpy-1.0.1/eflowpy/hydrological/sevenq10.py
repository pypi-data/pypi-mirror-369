"""
7Q10 Method for Low Flow Estimation.
"""

import pandas as pd
import matplotlib.pyplot as plt
from .base import BaseHydrologicalMethod

class SevenQ10(BaseHydrologicalMethod):
    """
    7Q10 method: lowest 7-day average flow in a year, typically with a 10-year recurrence.
    """

    def __init__(self, flow_data: pd.Series):
        self.flow_data = flow_data.dropna()
        self.result = None

    def calculate(self):
        rolling_7day = self.flow_data.rolling(window=7).mean().dropna()
        min_7day = rolling_7day.min()
        self.result = pd.Series({"7Q10": min_7day})
        return self.result

    def plot(self):
        """
        Plot the streamflow time series with the 7Q10 line.
        """
        if self.result is None:
            raise ValueError("Run calculate() before plot().")

        ts = self.flow_data.dropna()

        plt.figure(figsize=(12, 5))
        ts.plot(color="black", linewidth=1, label="Streamflow")

        q7 = self.result["7Q10"]
        plt.axhline(y=q7, color="blue", linestyle="--", label=f"7Q10 = {q7:.2f}")

        plt.xlabel("Date")
        plt.ylabel("Flow")
        plt.title("7Q10 Method: Streamflow with 7Q10 Threshold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
