import os
from typing import Dict, Optional
import networkx as nx

_graph = nx.DiGraph()


def add_entry(file_path: str) -> None:
    """Add nodes and edges for a file -> module -> service relation."""
    parts = file_path.split(os.sep)
    if len(parts) > 1 and parts[0] == "server":
        service = parts[1]
    else:
        service = parts[0] if parts else file_path
    module = os.path.splitext(os.path.basename(file_path))[0]
    _graph.add_node(file_path, type="file")
    _graph.add_node(module, type="module")
    _graph.add_node(service, type="service")
    _graph.add_edge(file_path, module)
    _graph.add_edge(module, service)


def get_connections(file_path: str) -> Optional[Dict[str, str]]:
    """Return connected module and service for a file path."""
    if file_path not in _graph:
        return None
    succ = list(_graph.successors(file_path))
    module = succ[0] if succ else None
    service = None
    if module and module in _graph:
        succ2 = list(_graph.successors(module))
        service = succ2[0] if succ2 else None
    return {"file": file_path, "module": module, "service": service}


def clear_graph() -> None:
    _graph.clear()
