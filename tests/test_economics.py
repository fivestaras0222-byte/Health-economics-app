from engine.economics import calculate_incremental, evaluate_strategy
from engine.markov import run_markov


def test_basic_cua_example():
    trace = run_markov([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], 1, ["Alive", "Death"])
    a = evaluate_strategy(trace, 120, 0, {"Alive": 0, "Death": 0}, {"Alive": 0.8, "Death": 0}, 1, 0, 0)
    b = evaluate_strategy(trace, 100, 0, {"Alive": 0, "Death": 0}, {"Alive": 0.7, "Death": 0}, 1, 0, 0)
    incremental = calculate_incremental(a, b, "CUA")
    assert a["total_cost"] == 120
    assert b["total_cost"] == 100
    assert a["total_outcome"] == 0.8
    assert b["total_outcome"] == 0.7
    assert round(incremental["cost"], 8) == 20
    assert round(incremental["outcome"], 8) == 0.1
    assert round(incremental["icer"], 8) == 200
