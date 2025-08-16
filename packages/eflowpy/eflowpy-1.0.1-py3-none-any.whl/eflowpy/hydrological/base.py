import matplotlib.pyplot as plt

class BaseHydrologicalMethod:
    def plot_timeseries(self):
        """
        Plot the original streamflow time series, skipping gaps in the data.
        """
        if not hasattr(self, "flow_data") or self.flow_data is None or self.flow_data.empty:
            raise ValueError("No flow data available to plot.")

        clean_series = self.flow_data.dropna()

        if clean_series.empty:
            raise ValueError("No valid data to plot after removing missing values.")

        clean_series.plot(figsize=(10, 4), color="green", linewidth=1)
        plt.xlabel("Date")
        plt.ylabel("Flow")
        plt.title("Streamflow Time Series")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def get_summary(self):
        """
        Return a summary of the streamflow data.

        Includes mean, median, min, max, time range, missing count, and total count.
        """
        if not hasattr(self, "flow_data") or self.flow_data is None or self.flow_data.empty:
            raise ValueError("No flow data available to summarize.")

        summary = {
            "Start Date": self.flow_data.index.min(),
            "End Date": self.flow_data.index.max(),
            "Mean Flow": self.flow_data.mean(),
            "Median Flow": self.flow_data.median(),
            "Minimum Flow": self.flow_data.min(),
            "Maximum Flow": self.flow_data.max(),
            "Missing Values": self.flow_data.isna().sum(),
            "Total Observations": self.flow_data.size
        }
        return summary

    def print_summary(self):
        """
        Print a formatted summary of the streamflow data.
        """
        summary = self.get_summary()

        print("\n📊 Streamflow Data Summary")
        print("-" * 35)
        for key, value in summary.items():
            print(f"{key:<20}: {value}")
        print("-" * 35)
