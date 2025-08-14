import networkx as nx
import json
from .hif import *


def write_hif(G: nx.MultiDiGraph, path):
    data = encode_hif_data(G)
    with open(path, "w") as file:
        json.dump(data, file, indent=2)

def encode_hif_data(G: nx.MultiDiGraph):
    incidences = []
    edges = []
    nodes = []
    for u, v, d, k, a in hif_incidences(G, data=True):
        a = a.copy()
        u = a.pop("edge")
        v = a.pop("node")
        incidence = {"direction": d, "edge": u, "node": v, "attrs": {"key": k, **a}}
        incidences.append(incidence)
    for u, d in hif_nodes(G, data=True):
        a = d.copy()
        u = a.pop("node")
        if len(a) > 0 or G.in_degree[u] == G.out_degree[u] == 0:
            node = {"node": u, "attrs": a}
            nodes.append(node)
    for u, d in hif_edges(G, data=True):
        a = d.copy()
        u = a.pop("edge")
        if len(a) > 0 or G.in_degree[u] == G.out_degree[u] == 0:
            edge = {"edge": u, "attrs": a}
            edges.append(edge)
    return {"incidences": incidences, "edges": edges, "nodes": nodes}

def add_incidence(G: nx.MultiDiGraph, incidence):
    attrs = incidence.get("attrs", {})
    edge_id = incidence["edge"]
    node_id = incidence["node"]
    direction = incidence.get("direction")
    # TODO multi-incidence is not part of the HIF standard
    key = attrs.pop("key", 0)
    if "weight" in incidence:
        attrs["weight"] = incidence["weight"]
    hif_add_incidence(G, edge_id, node_id, direction, key, **attrs)

def add_edge(G: nx.MultiDiGraph, edge):
    attrs = edge.get("attrs", {})
    edge_id = edge["edge"]
    if "weight" in edge:
        attrs["weight"] = edge["weight"]
    hif_add_edge(G, edge_id, **attrs)

def add_node(G: nx.MultiDiGraph, node):
    attrs = node.get("attrs", {})
    node_id = node["node"]
    if "weight" in node:
        attrs["weight"] = node["weight"]
    hif_add_node(G, node_id, **attrs)

def read_hif(path):
    with open(path) as file:
        data = json.load(file)
    return read_hif_data(data)

def read_hif_data(data):
    G_attrs = data.get("metadata", {})
    if "network-type" in data:
        G_attrs["network-type"] = data["network-type"]
    G = nx.MultiDiGraph(**G_attrs)
    for i in data["incidences"]:
        add_incidence(G, i)
    for e in data.get("edges", []):
        add_edge(G, e)
    for n in data.get("nodes", []):
        add_node(G, n)
    # note that this is the standard technique for disjoint unions.
    # it means ids are not preserved and we need to save edge and node ids in attributes.
    G = nx.convert_node_labels_to_integers(G)
    return G
