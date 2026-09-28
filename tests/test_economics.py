from engine.economics import calculate_incremental, convert_strategy_costs, evaluate_strategy
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


def test_direct_usd_cny_rate_converts_all_cost_series():
    strategy = {
        "total_cost": 700.0,
        "cycle_costs": [200.0, 500.0],
        "cumulative_costs": [0.0, 200.0, 700.0],
        "total_outcome": 1.0,
    }
    converted = convert_strategy_costs(strategy, 1 / 7)
    assert converted["total_cost"] == 100.0
    assert converted["cycle_costs"] == [200 / 7, 500 / 7]
    assert converted["cumulative_costs"] == [0.0, 200 / 7, 100.0]
    assert converted["total_outcome"] == 1.0
