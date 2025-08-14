# HIF for NetworkX

This package provides methods to load standard [HIF](https://github.com/pszufe/HIF-standard) higher-order network data into NetworkX objects, and functions to work with such graphs.

This library establishes a direct mapping between the Hypergraph and Bipartite Graph representations without introducing new classes. It is the hope of this project to be replaced by upstream support.

## Mapping hypergraphs to bipartite graphs

The HIF standard models a hypergraph where:
* H=(V,E,I) where V={v} is a finite, non-empty set of vertices or nodes
* E={e} is a finite, non-empty set of edges or hyperedges, and
* I⊆E×V is a set of incidences, that is, pairs (v,e) of nodes and edges.

To map this to a NetworkX bipartite graph it is important to adhere to the convention of using the `bipartite` attribute, while also avoiding overlap between node and hyperedge IDs.
* `G: nx.Graph`
* `G.add_node((v, 0), bipartite=0)`
* `G.add_node((e, 1), bipartite=1)`
* `G.add_edge((v, 0), (e, 1))`
