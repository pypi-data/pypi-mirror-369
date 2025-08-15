# LinkNex (MVP)
Network-of-Networks (NoN) interactions — minimal toolkit.

## Quick Start
```python
import networkx as nx
from linknex import InterGraph

A = nx.Graph(); A.add_edge("a1","a2")
B = nx.Graph(); B.add_edge("b1","b2")
ig = InterGraph({"Men": A, "Women": B})
ig.add_inter_edge(("Men","a2"), ("Women","b1"), weight=1.0, kind="relationship")
print(ig)
