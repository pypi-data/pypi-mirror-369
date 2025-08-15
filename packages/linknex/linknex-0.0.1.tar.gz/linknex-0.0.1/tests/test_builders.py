# tests/test_builders.py
import networkx as nx
import numpy as np
from linknex import InterGraph
from linknex import supra_adjacency, supra_graph

def make_layers():
    A = nx.Graph(); A.add_edges_from([("a1","a2"), ("a2","a3")])
    B = nx.Graph(); B.add_edges_from([("b1","b2")])
    return {"A": A, "B": B}

def test_supra_adjacency_shape_and_blocks():
    ig = InterGraph(make_layers())
    ig.add_inter_edge(("A","a2"), ("B","b1"), weight=2.0)

    M, order = supra_adjacency(ig)
    # 共有 3 + 2 = 5 个多层节点
    assert M.shape == (5, 5)
    assert len(order) == 5

    # 验证层内边 (A: a1-a2, a2-a3) 权重=1
    pos = {t:i for i,t in enumerate(order)}
    i_a1, i_a2, i_a3 = pos[("A","a1")], pos[("A","a2")], pos[("A","a3")]
    assert M[i_a1, i_a2] == 1 and M[i_a2, i_a1] == 1
    assert M[i_a2, i_a3] == 1 and M[i_a3, i_a2] == 1

    # 验证层内边 (B: b1-b2) 权重=1
    i_b1, i_b2 = pos[("B","b1")], pos[("B","b2")]
    assert M[i_b1, i_b2] == 1 and M[i_b2, i_b1] == 1

    # 验证跨网边 (A:a2)-(B:b1) 权重=2
    assert M[i_a2, i_b1] == 2 and M[i_b1, i_a2] == 2

def test_supra_graph_nodes_and_edges():
    ig = InterGraph(make_layers())
    ig.add_inter_edge(("A","a2"), ("B","b1"), weight=1.5)

    G = supra_graph(ig)
    # 节点名是 (Layer, Node)
    assert ("A","a1") in G and ("B","b2") in G

    # 层内边存在
    assert G.has_edge(("A","a1"), ("A","a2"))
    # 跨网边存在，且权重=1.5
    assert G.has_edge(("A","a2"), ("B","b1"))
    w = G[("A","a2")][("B","b1")].get("weight", None)
    assert w == 1.5
