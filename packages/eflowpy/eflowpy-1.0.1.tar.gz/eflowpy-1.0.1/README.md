# eflowpy

**eflowpy** is a Python package for estimating environmental flow requirements using hydrological methods based on streamflow time series data. It provides a consistent and extensible interface for calculating commonly used flow-based environmental indicators.

## Features

- Calculate environmental flow recommendations using:
  - Tennant Method
  - Flow Duration Curve (FDC)
  - GEFC (Generalized Environmental Flow Criteria)
  - 7Q10 Method
  - Tessman Method
- Built-in plotting support:
  - Time series plots
  - Flow threshold overlays

## Installation
To install `eflowpy` from PyPI:
```bash
pip install eflowpy
```
---

## How to Use

### Quick Start Example

```python
import pandas as pd
from eflowpy.hydrological.tennant import Tennant
from eflowpy.utils.data_reader import read_streamflow_data

# Load streamflow time series from file
flow_series = read_streamflow_data("gauge_12013059_daily.csv", folder="path/to/your/data")

# Run Tennant method
tennant = Tennant(flow_series)
tennant.print_summary()
result = tennant.calculate()
print(result)

# Plot bar chart and streamflow overlay
tennant.plot()
tennant.plot_with_levels()
```

## Method Applicability

The table below shows which environmental flow methods in `eflowpy` can be applied to daily or monthly streamflow datasets:

| Method       | Daily Data | Monthly Data | Notes                                                                 |
|--------------|------------|--------------|-----------------------------------------------------------------------|
| **Tennant**  | ✅ Yes     | ✅ Yes       | Uses mean flow → works for both temporal scales                       |
| **FDC**      | ✅ Yes     | ✅ Yes       | Based on sorting values by exceedance probability                     |
| **GEFC**     | ✅ Yes     | ✅ Yes       | Relies on mean flow thresholds (30%, 60%, 100%)                       |
| **7Q10**     | ✅ Yes     | ❌ No        | Requires 7-day rolling min, so daily data is mandatory                |
| **Tessman**  | ✅ Yes     | ✅ Yes       | Designed for monthly flow but also works with daily (via resampling)  |

## License
This project is licensed under the **MIT License**.
