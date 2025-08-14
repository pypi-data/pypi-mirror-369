import networkx as nx


def hif_nodes(G: nx.MultiDiGraph, data=False):
    for e, d in G.nodes(data=True):
        if d["bipartite"] == 0:
            yield e, d if data else e

def hif_edges(G: nx.MultiDiGraph, data=False):
    for e, d in G.nodes(data=True):
        if d["bipartite"] == 1:
            yield e, d if data else e

def hif_edge_nodes(G: nx.MultiDiGraph, edge, data=False):
    for e in G.in_edges(edge, keys=True, data=data):
        yield (e[1], e[0], "tail",) + e[2:]
    for e in G.out_edges(edge, keys=True, data=data):
        yield (e[0], e[1], "head",) + e[2:]

def hif_incidences(G: nx.MultiDiGraph, edge=None, node=None, direction=None, key=None, data=False):
    # TODO search attributes because ids are not preserved
    if edge is not None:
        assert G.nodes[edge]["bipartite"] == 1
        edges = [edge]
    else:
        edges = hif_edges(G)

    if node is not None:
        assert G.nodes[node]["bipartite"] == 0

    for e0 in edges:
        for e in hif_edge_nodes(G, e0, data=data):
            if node is None or node == e[1]:
                if direction is None or direction == e[2]:
                    if key is None or key == e[3]:
                        yield e

def hif_add_edge(G, edge, **attr):
    if not G.has_node(edge):
        G.add_node(("edge", edge), bipartite=1)
    attr["edge"] = edge
    for attr_key, attr_value in attr.items():
        G.nodes[("edge", edge)][attr_key] = attr_value

def hif_add_node(G, node, **attr):
    if not G.has_node(node):
        G.add_node(("node", node), bipartite=0)
    attr["node"] = node
    for attr_key, attr_value in attr.items():
        G.nodes[("node", node)][attr_key] = attr_value

def hif_add_incidence(G: nx.MultiDiGraph, edge, node, direction, key, **attr):
    if not G.has_node(edge):
        G.add_node(("edge", edge), bipartite=1, edge=edge)
    if not G.has_node(node):
        G.add_node(("node", node), bipartite=0, node=node)
    attr["edge"] = edge
    attr["node"] = node
    if direction == "tail":
        G.add_edge(("node", node), ("edge", edge), key, **attr)
    else:
        G.add_edge(("edge", edge), ("node", node), key, **attr)
