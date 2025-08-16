import pandas as pd
import os

def read_streamflow_data(file_name_or_path, folder=None, missing_value_handling="drop", delimiter=","):
    """
    Reads streamflow data from a CSV/TXT file and returns a Series indexed by date.
    Assumes:
    - First column = Date
    - Second column = Flow

    Parameters:
    - file_name_or_path (str): File name or full path to the streamflow file.
    - folder (str, optional): If provided, combined with file_name_or_path.
    - missing_value_handling (str): "drop" or "fill"
    - delimiter (str): File delimiter (default: ",")

    Returns:
    - pd.Series: Flow data with datetime index.
    """
    file_path = os.path.join(folder, file_name_or_path) if folder else file_name_or_path

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path, delimiter=delimiter)

    if df.shape[1] < 2:
        raise ValueError("Expected at least two columns: [Date, flow]")

    df.columns = ["Date", "Flow"] + list(df.columns[2:])
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    if missing_value_handling == "drop":
        df = df.dropna(subset=["Flow"])
    elif missing_value_handling == "fill":
        df["Flow"] = df["Flow"].fillna(df["Flow"].mean())

    return df["Flow"]


def read_multiple_streamflows(file_name, folder="data/raw", missing_value_handling="drop", delimiter=","):
    """
    Reads streamflow data from a CSV/TXT file with multiple flow columns (e.g., multiple reservoirs).
    Returns a pandas DataFrame indexed by datetime.
    """
    import os
    import pandas as pd

    file_path = file_name if os.path.isabs(file_name) else os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path, delimiter=delimiter)
    df.columns = [col.strip() for col in df.columns]

    if df.shape[1] < 2:
        raise ValueError("Expected at least two columns: [Date, Flow1, Flow2, ...]")

    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    if missing_value_handling == "drop":
        df = df.dropna()
    elif missing_value_handling == "fill":
        df = df.fillna(df.mean(numeric_only=True))

    return df