"""Pure Markov cohort simulation functions."""
from __future__ import annotations

import numpy as np
import pandas as pd


def run_markov(initial_distribution: list[float], transition_matrix: list[list[float]],
               cycles: int, states: list[str]) -> pd.DataFrame:
    """Simulate state membership at cycle start, including cycle 0."""
    current = np.asarray(initial_distribution, dtype=float)
    transition = np.asarray(transition_matrix, dtype=float)
    trace = [current.copy()]
    for _ in range(cycles):
        current = current @ transition
        trace.append(current.copy())
    frame = pd.DataFrame(trace, columns=states)
    frame.index.name = "cycle"
    return frame
