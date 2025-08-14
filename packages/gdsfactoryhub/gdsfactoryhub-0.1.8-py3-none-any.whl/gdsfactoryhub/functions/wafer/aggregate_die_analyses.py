# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gdsfactoryhub==0.1.8",
#     "numpy",
#     "matplotlib",
# ]
# ///
"""Aggregate die analyses into a wafer map."""

import itertools

import matplotlib.pyplot as plt
import numpy as np

import gdsfactoryhub as dd


def run(
    wafer_pkey: str,
    die_function_id: str,
    output_key: str,
    min_output: float | None = None,
    max_output: float | None = None,
):
    """Aggregate die analyses into a wafer map.

    Args:
        wafer_pkey (str): The primary key of the wafer.
        die_function_id (str): The function ID of the die analyses to aggregate.
        output_key (str): The key in the output dictionary to aggregate.
        min_output (float | None, optional): Minimum output value to include. Defaults to None.
        max_output (float | None, optional): Maximum output value to include. Defaults to None.

    """
    utils = dd.create_client_from_env().utils()
    analyses = dict(utils.wafer().get_die_analyses(pk=wafer_pkey))

    xy = np.array(list(analyses))
    xs = np.arange(xy[:, 0].min(), xy[:, 0].max() + 1, 1)
    ys = np.arange(xy[:, 1].min(), xy[:, 1].max() + 1, 1)
    X, Y = np.meshgrid(xs, ys)
    Z = np.nan * np.zeros_like(X)
    output = {}
    for (i, x), (j, y) in itertools.product(enumerate(xs), enumerate(ys)):
        x, y = int(x), int(y)
        analysis_set = analyses.get((x, y), [])
        analysis_set = [
            a for a in analysis_set if a.function.function_id == die_function_id if output_key in (a.output or {})
        ]
        if not analysis_set:
            continue
        analysis = next(iter(analysis_set))
        if analysis is None:
            continue
        if analysis.output is None:
            continue
        _output = float(analysis.output[output_key])
        if min_output is not None and _output < min_output:
            continue
        if max_output is not None and _output > max_output:
            continue
        Z[i, j] = output[x, y] = _output

    mean_output = float(np.nanmean(np.array(list(output.values()))))

    plt.axis("scaled")
    plt.pcolormesh(X, Y, Z)
    plt.grid(visible=True, which="minor")
    plt.xticks(xs)
    plt.xticks(ys)
    plt.xticks(np.concatenate([xs - 0.5, [xs[-1] + 0.5]]), minor=True)
    plt.yticks(np.concatenate([ys - 0.5, [ys[-1] + 0.5]]), minor=True)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.colorbar()

    return {
        "output": {f"mean_{output_key}": mean_output},
        "summary_plot": plt.gcf(),
        "wafer_pkey": wafer_pkey,
    }
