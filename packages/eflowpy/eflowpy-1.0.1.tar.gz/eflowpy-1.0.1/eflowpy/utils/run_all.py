import pandas as pd
from eflowpy.hydrological.tennant import Tennant
from eflowpy.hydrological.gefc import GEFC
from eflowpy.hydrological.sevenq10 import SevenQ10
from eflowpy.hydrological.fdc import FDC

def run_all_methods(flow_series):
    """
    Run all supported hydrological methods on a flow series and return results in a DataFrame.
    """
    results = []

    # Tennant
    tennant = Tennant(flow_series)
    tennant_result = tennant.calculate()
    for label, value in tennant_result.items():
        results.append({"Method": "Tennant", "Metric": label, "Value": value})

    # GEFC
    gefc = GEFC(flow_series)
    gefc_result = gefc.calculate()
    for label, value in gefc_result.items():
        results.append({"Method": "GEFC", "Metric": label, "Value": value})

    # SevenQ10
    sevenq10 = SevenQ10(flow_series)
    q7 = sevenq10.calculate()["7Q10"]
    results.append({"Method": "SevenQ10", "Metric": "7Q10", "Value": q7})

    # FDC percentiles
    fdc = FDC(flow_series)
    fdc.calculate()  # must run before calling get_flow_at_percentile
    for p in [10, 50, 90]:
        q = fdc.get_flow_at_percentile(p)
        results.append({"Method": "FDC", "Metric": f"Q{p}", "Value": q})

    return pd.DataFrame(results)
