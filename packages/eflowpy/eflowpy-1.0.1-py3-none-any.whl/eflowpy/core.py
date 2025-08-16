# eflowpy/core.py

import pandas as pd

class EnvironmentalFlow:
    """
    Base class for handling environmental flow calculations.
    This class manages streamflow data and provides basic functionality
    for processing and analyzing it.
    """

    def __init__(self, flow_data):
        """
        Initialize the EnvironmentalFlow class.

        Parameters:
        flow_data (iterable): Streamflow data (daily or monthly values).
        """
        if len(flow_data) == 0:
            raise ValueError("Flow data cannot be empty.")

        self.flow_data = pd.Series(flow_data)  # Store data as a Pandas series for flexibility
        self.average_flow = self.flow_data.mean()  # Calculate average flow

    def validate_data(self):
        """
        Validate the streamflow data for any issues.
        """
        if self.flow_data.isnull().any():
            raise ValueError("Flow data contains missing values.")
        if self.average_flow <= 0:
            raise ValueError("Average flow must be greater than 0.")

    def get_summary(self):
        """
        Provide a summary of the streamflow data.

        Returns:
        dict: A dictionary with basic statistics about the flow data.
        """
        return {
            "count": len(self.flow_data),
            "mean": self.flow_data.mean(),
            "min": self.flow_data.min(),
            "max": self.flow_data.max(),
            "std": self.flow_data.std()
        }
