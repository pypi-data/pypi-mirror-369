# src/linknex/metrics/paths.py
import networkx as nx
from ..builders import supra_graph

def shortest_path_length(ig, source, target, inter_cost: float = 1.0):
    """
    计算 NoN 上 source→target 的最短路径长度。
    - 层内边权 = 1
    - 跨网边权 = inter_cost (ω)
    source/target 必须是 (Layer, Node) 形式的多层节点标识。
    """
    G = supra_graph(ig)
    # 设置权重
    for (u, v, data) in G.edges(data=True):
        data["weight"] = float(inter_cost if u[0] != v[0] else 1.0)
    return nx.shortest_path_length(G, source=source, target=target, weight="weight")

def efficiency(ig, inter_cost: float = 1.0):
    """
    全局效率 (global efficiency): 所有节点对的平均 1/d(i,j)，
    仅对可达的点对计入，且不重复计算无序对。
    """
    G = supra_graph(ig)
    for (u, v, data) in G.edges(data=True):
        data["weight"] = float(inter_cost if u[0] != v[0] else 1.0)

    import itertools
    total, count = 0.0, 0
    for i, j in itertools.combinations(G.nodes(), 2):
        try:
            d = nx.shortest_path_length(G, source=i, target=j, weight="weight")
            if d > 0:
                total += 1.0 / d
                count += 1
        except nx.NetworkXNoPath:
            continue
    return 0.0 if count == 0 else (2.0 * total / count)  # ×2 折返平均
