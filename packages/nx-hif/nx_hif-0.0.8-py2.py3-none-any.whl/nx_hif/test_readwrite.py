import json
import pathlib
from .readwrite import read_hif, encode_hif_data


def test_inet_franchu_readwrite():
    G = read_hif("data/inet/franchu.json")
    data = encode_hif_data(G)
    reencoded = json.dumps(data, indent=2)
    expected = pathlib.Path("data/inet/franchu.json").read_text()
    assert reencoded == expected
