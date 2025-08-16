"""
Flow Duration Curve (FDC) Method
"""

from .base import BaseHydrologicalMethod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class FDC(BaseHydrologicalMethod):
    """
    Flow Duration Curve method to estimate environmental flows based on exceedance probabilities.
    """

    def __init__(self, flow_data: pd.Series):
        self.flow_data = flow_data.dropna()
        self.result = None

    def calculate(self):
        sorted_flows = np.sort(self.flow_data.values)[::-1]
        exceedance = np.arange(1, len(sorted_flows) + 1) / (len(sorted_flows) + 1)
        self.result = pd.Series(data=sorted_flows, index=exceedance, name="flow")
        return self.result

    def plot(self):
        if self.result is None:
            raise ValueError("Run calculate() before plot().")
        self.result.plot()
        plt.xlabel("Exceedance Probability")
        plt.ylabel("Flow")
        plt.title("Flow Duration Curve (FDC)")
        plt.grid(True)
        plt.show()

        
    def get_flow_at_percentile(self, percentile: float) -> float:
        """
        Get the flow value at a specified exceedance percentile.

        Parameters:
        percentile (float): Exceedance percentile (e.g., 10 for Q10, 95 for Q95)

        Returns:
        float: Interpolated flow value at the given percentile.
        """
        if self.result is None:
            raise ValueError("Run calculate() before using get_flow_at_percentile().")

        exceedance_probs = self.result.index.values * 100  # convert to percentage
        flow_values = self.result.values

        # Validate range
        if percentile < min(exceedance_probs) or percentile > max(exceedance_probs):
            raise ValueError(f"Percentile {percentile} is out of range! Must be between {min(exceedance_probs)} and {max(exceedance_probs)}.")

        # Interpolate
        interp_func = interp1d(exceedance_probs, flow_values, kind="linear", fill_value="extrapolate")
        return float(interp_func(percentile))
    

    def plot_with_percentiles(self, percentiles: list):
        """
        Plot the Flow Duration Curve and annotate specific percentiles.

        Parameters:
        percentiles (list): List of exceedance percentiles to mark (e.g., [10, 50, 95])
        """
        if self.result is None:
            raise ValueError("Run calculate() before using plot_with_percentiles().")

        exceedance_probs = self.result.index.values * 100  # in percentage
        flow_values = self.result.values

        # Interpolation function
        interp_func = interp1d(exceedance_probs, flow_values, kind="linear", fill_value="extrapolate")

        # Create base plot
        plt.figure(figsize=(8, 5))
        plt.plot(exceedance_probs, flow_values, label="Flow Duration Curve", color="blue")

        # Annotate given percentiles
        for p in percentiles:
            if p < min(exceedance_probs) or p > max(exceedance_probs):
                print(f"Warning: Percentile {p} is out of range. Skipped.")
                continue
            q_val = interp_func(p)
            plt.scatter(p, q_val, color="red")
            plt.text(p, q_val, f"Q{int(p)}={q_val:.2f}", fontsize=9, ha="right", va="bottom")

        plt.xlabel("Exceedance Probability (%)")
        plt.ylabel("Flow")
        plt.title("Flow Duration Curve with Q-values")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()



