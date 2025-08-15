# tests/test_intergraph.py
import networkx as nx
import pytest
from linknex import InterGraph

def make_layers():
    A = nx.Graph(); A.add_edges_from([("a1", "a2"), ("a2", "a3")])
    B = nx.Graph(); B.add_edges_from([("b1", "b2")])
    return {"A": A, "B": B}

def test_create_intergraph_and_add_inter_edge():
    ig = InterGraph(make_layers())
    assert "A" in ig.layers and "B" in ig.layers
    assert ig.layers["A"].number_of_nodes() == 3
    assert ig.layers["B"].number_of_edges() == 1

    # 添加一条跨网边
    ig.add_inter_edge(("A", "a2"), ("B", "b1"), weight=1.2, kind="interaction")
    assert len(ig.inter_edges) == 1

    # 结构内容校验
    (u, v, w, attrs) = ig.inter_edges[0]
    assert u == ("A", "a2")
    assert v == ("B", "b1")
    assert pytest.approx(w, rel=1e-6) == 1.2
    assert attrs["weight"] == 1.2
    assert attrs["kind"] == "interaction"

def test_repr_is_informative():
    ig = InterGraph(make_layers())
    s = repr(ig)
    assert "InterGraph(" in s
    assert "inter_edges=0" in s
    ig.add_inter_edge(("A", "a2"), ("B", "b1"))
    assert "inter_edges=1" in repr(ig)

def test_add_inter_edge_invalid_layer_raises():
    ig = InterGraph(make_layers())
    with pytest.raises(KeyError):
        ig.add_inter_edge(("X", "a2"), ("B", "b1"))

def test_add_inter_edge_invalid_node_raises():
    ig = InterGraph(make_layers())
    with pytest.raises(KeyError):
        ig.add_inter_edge(("A", "not_exists"), ("B", "b1"))
