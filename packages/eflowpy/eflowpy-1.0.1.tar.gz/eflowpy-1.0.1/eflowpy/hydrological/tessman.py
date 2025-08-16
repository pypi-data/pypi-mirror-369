"""
Tessman Method for Environmental Flow Estimation.

Reference:
Tessman, S. A. (1980). Environmental assessment, technical appendix E, in-stream flow recommendations for the Fort Union Basin. Montana Department of Natural Resources and Conservation.

This method estimates environmental flows based on monthly mean flows.
"""

import pandas as pd

class Tessman:
    """
    Class to apply the Tessman Method for environmental flow estimation.
    """

    def __init__(self, flow_data: pd.Series):
        """
        Initialize the TessmanMethod.

        Parameters:
        flow_data (pd.Series): Daily streamflow data indexed by datetime.
        """
        self.flow_data = flow_data
        self.result = None

    def calculate(self) -> pd.DataFrame:
        """
        Calculate environmental flows using the Tessman method.

        Returns:
        pd.DataFrame: DataFrame with Qlow, Qmed, Qhigh for each month.
        """
        monthly_mean = self.flow_data.resample("M").mean()
        df = pd.DataFrame(index=monthly_mean.index)
        df["Qlow"] = monthly_mean * 0.4
        df["Qmed"] = monthly_mean * 0.6
        df["Qhigh"] = monthly_mean * 1.0
        self.result = df
        return df
