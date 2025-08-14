# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.8",
#     "matplotlib",
#     "numpy",
#     "orjson",
#     "pandas",
# ]
# ///
"""Calculates propagation loss from cutback measurement."""

import matplotlib.pyplot as plt
import numpy as np

import gdsfactoryhub as dd


def run(
    die_pkey: str,
    resistance_name: str = "resistance",
    device_iv_fit_function_id: str = "linear_fit",
):
    """Calculate sheet resistance from device IV data.

    Args:
        die_pkey (str): Primary key of the die to analyze.
        resistance_name (str): Name of the resistance output in the device IV data.
        device_iv_fit_function_id (str): Function ID for the device IV fit.

    """
    client = dd.create_client_from_env()
    query = client.query()

    datas = [data for data in query.device_data().execute().data if data["die"]["pk"] == die_pkey]
    widths = np.array([d["device"]["cell"]["attributes"]["width_um"] for d in datas])
    lengths = np.array([d["device"]["cell"]["attributes"]["length_um"] for d in datas])
    pkeys = [data["pk"] for data in datas]
    areas = widths * lengths * 1e-12
    datas = {
        data["device_data"]["pk"]: data
        for data in query.analyses().eq("function.function_id", device_iv_fit_function_id).execute().data
        if data["device_data"]["die"]["pk"] == die_pkey
    }
    datas = [datas[pkey] for pkey in pkeys]

    values = np.array([data["output"][resistance_name] for data in datas])

    x = np.linspace(areas.min(), areas.max())
    a, b = np.polyfit(areas, values, deg=1)
    plt.scatter(areas, values, marker="o", color="C0")
    plt.plot(x, a * x + b, color="C1", label=f"sheet resistance: {a:.2e}")
    plt.xlabel("Area [m²]")
    plt.ylabel("Resistance [Ω]")
    plt.legend()
    plt.grid(visible=True)

    return {
        "output": {
            "sheet_resistance": float(a),
        },
        "summary_plot": plt.gcf(),
        "die_pkey": die_pkey,
    }
