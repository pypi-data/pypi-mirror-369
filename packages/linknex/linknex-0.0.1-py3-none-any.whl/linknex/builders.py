# src/linknex/builders.py
from typing import Dict, Tuple, List
import networkx as nx
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from .data import InterGraph, Layer, Node

def supra_adjacency(ig: InterGraph) -> Tuple[csr_matrix, List[Tuple[Layer, Node]]]:
    """
    构造 supra 邻接矩阵：
    - 先把各层节点按顺序排成一个一维列表 order=[(L,n),...]
    - 矩阵对角块是各层的邻接；非对角块是跨网边
    返回 (A_csr, order)
    """
    # 1) 为每个 (L,node) 分配全局索引
    order: List[Tuple[Layer, Node]] = []
    idx: Dict[Tuple[Layer, Node], int] = {}
    k = 0
    for L, G in ig.layers.items():
        for n in G.nodes():
            order.append((L, n))
            idx[(L, n)] = k
            k += 1
    n_tot = k
    M = lil_matrix((n_tot, n_tot), dtype=float)

    # 2) 层内边 → 对角块
    for L, G in ig.layers.items():
        for u, v, d in G.edges(data=True):
            w = float(d.get("weight", 1.0))
            iu, iv = idx[(L, u)], idx[(L, v)]
            M[iu, iv] = M[iu, iv] + w
            M[iv, iu] = M[iv, iu] + w

    # 3) 跨网边 → 非对角块
    for (u, v, w, attrs) in ig.inter_edges:
        iu, iv = idx[u], idx[v]
        ww = float(attrs.get("weight", w))
        M[iu, iv] = M[iu, iv] + ww
        M[iv, iu] = M[iv, iu] + ww

    return M.tocsr(), order

def supra_graph(ig: InterGraph) -> nx.Graph:
    """
    把 supra 矩阵转成一个 networkx 无向图。
    节点名直接用 (Layer, Node) 元组，边权放在 'weight' 属性里。
    """
    A, order = supra_adjacency(ig)
    # 用 scipy 稀疏矩阵构图；注意 from_scipy_sparse_array 需要网络x>=2.6
    G = nx.from_scipy_sparse_array(A)  # 无向
    mapping = {i: order[i] for i in range(len(order))}
    G = nx.relabel_nodes(G, mapping)
    # networkx 默认把权重字段叫 'weight'（在 from_scipy_sparse_array 已处理）
    return G
