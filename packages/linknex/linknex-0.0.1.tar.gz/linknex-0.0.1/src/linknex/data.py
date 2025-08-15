from typing import Dict, Tuple, Hashable, List, Any
import networkx as nx

Node = Hashable
Layer = Hashable
Endpoint = Tuple[Layer, Node]

class InterGraph:
    """
    Network-of-Networks 容器：
    - layers: 每层一个 networkx 图（节点集互不重叠）
    - inter_edges: 显式存储跨网边 [((L,u),(R,v), weight, attrs), ...]
    """
    def __init__(self, layers: Dict[Layer, nx.Graph]):
        if not layers:
            raise ValueError("Provide at least one layer graph.")
        # 拷贝以避免外部修改影响内部
        self.layers: Dict[Layer, nx.Graph] = {L: g.copy() for L, g in layers.items()}
        self.inter_edges: List[Tuple[Endpoint, Endpoint, float, Dict[str, Any]]] = []

    def add_inter_edge(self, u: Endpoint, v: Endpoint, weight: float = 1.0, **attrs):
        Lu, nu = u; Lv, nv = v
        if Lu not in self.layers or Lv not in self.layers:
            raise KeyError(f"Layer not found: {Lu} or {Lv}")
        if nu not in self.layers[Lu] or nv not in self.layers[Lv]:
            raise KeyError("Node not found in the specified layer.")
        info = {"weight": float(weight)} | attrs
        self.inter_edges.append((u, v, float(weight), info))

    def copy(self) -> "InterGraph":
        ig = InterGraph(self.layers)
        ig.inter_edges = [(u, v, w, dict(a)) for (u, v, w, a) in self.inter_edges]
        return ig

    def __repr__(self) -> str:
        layers_str = ", ".join([f"{L}({G.number_of_nodes()}n/{G.number_of_edges()}e)"
                                for L, G in self.layers.items()])
        return f"InterGraph(layers=[{layers_str}], inter_edges={len(self.inter_edges)})"
