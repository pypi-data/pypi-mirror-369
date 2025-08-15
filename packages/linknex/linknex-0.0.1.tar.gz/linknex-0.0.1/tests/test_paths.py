# tests/test_paths.py
import networkx as nx
from linknex import InterGraph
from linknex.metrics.paths import shortest_path_length, efficiency

def _make_ig():
    A = nx.Graph(); A.add_edges_from([("a1","a2"), ("a2","a3")])  # a1--a2--a3
    B = nx.Graph(); B.add_edges_from([("b1","b2")])               # b1--b2
    ig = InterGraph({"A": A, "B": B})
    # 跨网：A:a2 连接 B:b1
    ig.add_inter_edge(("A","a2"), ("B","b1"), weight=1.0)
    return ig

def test_shortest_path_length_with_inter_cost():
    ig = _make_ig()
    # 从 A:a1 到 B:b2
    d1 = shortest_path_length(ig, ("A","a1"), ("B","b2"), inter_cost=1.0)
    # 路径：a1-a2 (1) + a2-b1 (1) + b1-b2 (1) = 3
    assert d1 == 3.0

    d2 = shortest_path_length(ig, ("A","a1"), ("B","b2"), inter_cost=2.5)
    # 路径：a1-a2 (1) + a2-b1 (2.5) + b1-b2 (1) = 4.5
    assert abs(d2 - 4.5) < 1e-9

def test_global_efficiency_runs():
    ig = _make_ig()
    e = efficiency(ig, inter_cost=2.0)
    # 只校验数值范围合理与非负
    assert e >= 0.0
