from typing import Optional
import xml.etree.ElementTree as ET

import requests

import config
from src.db_connection.postgres import get_db_connection


def set_up_graph_data():
    xml_string = download_graph()
    if xml_string is None:
        print("Problem downloading graph data.")
        return
    valid, xml_data = verify_graph_data(xml_string)
    if not valid:
        print("Problem validating graph data.")
        return
    graph_id, graph_name, nodes, edges = extract_graph_data(xml_data)
    if not verify_unique_ids(nodes):
        print("Problem validating unique node IDs.")
        return
    if not verify_unique_ids(edges):
        print("Problem validating unique edge IDs.")
        return
    set_graph_id(graph_id)
    if graph_id_exists(graph_id):
        print("Graph ID already exists.")
        return
    graph_data = graph_id, graph_name, nodes, edges
    insert_graph_data(graph_data)
    print("Graph data successfully inserted.")


def download_graph() -> Optional[str]:
    """Retrieve xml graph data.

    Based on endpoint in the config file, download and return the data.
    Note that this function assumes the endpoint is wide open, without
    any auth requirements.
    """
    response = requests.get(config.graph_data_endpoint)
    if response.status_code != 200:
        return None
    return response.text


def verify_graph_data(xml_string) -> (bool, ET.Element):
    """Parse and confirm graph data is valid.

    We're using the standard library's xml.etree.ElementTree module to
    parse the XML, because we're not doing any complex operations, and
    we assume the XML is coming from a trusted source.
    If we needed better performance or more complex handling of XML,
    we'd consider a library like LXML, or defusedxml if we didn't trust
    the source.
    """
    node_ids = set()
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        print("Invalid graph data. Check XML structure.")
        return False, None
    if root.tag != 'graph':
        print("Invalid graph data. Root element is not 'graph'.")
        return False, None
    id_elem = root.findall('id')
    if len(id_elem) != 1:
        print("Invalid graph data. Expected one 'id' element.")
        return False, None
    if id_elem[0].text is None:
        print("Invalid graph data. Missing required element 'id'.")
        return False, None
    name_elem = root.findall('name')
    if len(name_elem) != 1:
        print("Invalid graph data. Expected one 'name' element.")
        return False, None
    if name_elem[0].text is None:
        print("Invalid graph data. Missing required element 'name'.")
        return False, None
    nodes_elem = root.findall('nodes')
    if len(nodes_elem) != 1:
        print("Invalid graph data. Expected one 'nodes' element.")
        return False, None
    nodes_list = nodes_elem[0].findall('node')
    if len(nodes_list) == 0:
        print("Invalid graph data. Expected at least one 'node' element.")
        return False, None
    for node_elem in nodes_list:
        node_id_elem = node_elem.findall('id')
        if len(node_id_elem) != 1:
            print("Invalid graph data. Expected one 'id' element in 'node'.")
            return False, None
        if node_id_elem[0].text is None:
            print("Invalid graph data. Missing required element 'id' in 'node'.")
            return False, None
        if node_id_elem[0].text in node_ids:
            print("Invalid graph data. Node ID is not unique.")
            return False, None
        node_ids.add(node_id_elem[0].text)
        node_name_elem = node_elem.findall('name')
        if len(node_name_elem) != 1:
            print("Invalid graph data. Expected one 'name' element in 'node'.")
            return False, None
        if node_name_elem[0].text is None:
            print("Invalid graph data. Missing required element 'name' in 'node'.")
            return False, None
    edges_elem = root.findall('edges')
    if len(edges_elem) != 1:
        print("Invalid graph data. Expected one 'edges' element.")
        return False, None
    edges_list = edges_elem[0].findall('node')
    for edge_elem in edges_list:
        edge_id_elem = edge_elem.findall('id')
        if len(edge_id_elem) != 1:
            print("Invalid graph data. Expected one 'id' element in 'edge'.")
            return False, None
        if edge_id_elem[0].text is None:
            print("Invalid graph data. Missing required element 'id' in 'edge'.")
            return False, None
        edge_from_elem = edge_elem.findall('from')
        if len(edge_from_elem) != 1:
            print("Invalid graph data. Expected one 'from' element in 'edge'.")
            return False, None
        if edge_from_elem[0].text not in node_ids:
            print("Invalid graph data. 'from' node ID not found.")
            return False, None
        edge_to_elem = edge_elem.findall('to')
        if len(edge_to_elem) != 1:
            print("Invalid graph data. Expected one 'to' element in 'edge'.")
            return False, None
        if edge_to_elem[0].text not in node_ids:
            print("Invalid graph data. 'to' node ID not found.")
            return False, None
        edge_cost_elem = edge_elem.findall('cost')
        if len(edge_cost_elem) > 1:
            print("Invalid graph data. Expected one or zero 'cost' elements in 'edge'.")
            return False, None
    return True, root


def extract_graph_data(graph_data: ET.Element) -> (str, str, list, list):
    """Extract graph data from XML."""
    # Grab the top level elements
    graph_id = graph_data.find('id').text
    graph_name = graph_data.find('name').text

    # Loop though each <node> element in <nodes>
    nodes = []
    for node in graph_data.find('nodes'):
        node_id = node.find('id').text
        node_name = node.find('name').text
        nodes.append((node_id, node_name))

    # Loop though each <node> element in <edges>
    edges = []
    for edge in graph_data.find('edges'):
        edge_id = edge.find('id').text
        edge_from = edge.find('from').text
        edge_to = edge.find('to').text
        try:  # If cost is missing or empty, set to zero
            edge_cost_str = edge.find('cost').text
            edge_cost = float(edge_cost_str)
            if edge_cost < 0:
                raise ValueError
        except (TypeError, AttributeError, ValueError):
            edge_cost = 0.0
        edges.append((edge_id, edge_from, edge_to, edge_cost))

    return graph_id, graph_name, nodes, edges


def verify_unique_ids(nodes) -> bool:
    """Check that all node IDs are unique."""
    node_ids = [node[0] for node in nodes]
    return len(node_ids) == len(set(node_ids))


def graph_id_exists(graph_id: str) -> bool:
    """Check if a graph with the given ID already exists."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT graph_id FROM public.graphs WHERE graph_id = %s", (graph_id,))
            result = cur.fetchone()
    return result is not None


def insert_graph_data(graph_data):
    """Insert into PostGres."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.graphs (graph_id, name) VALUES (%s, %s)", (graph_data[0], graph_data[1]))
            for node in graph_data[2]:
                cur.execute("INSERT INTO public.nodes (node_id, name, graph_id) VALUES (%s, %s, %s)", (*node, graph_data[0]))
            for edge in graph_data[3]:
                cur.execute("INSERT INTO public.edges (edge_id, from_node, to_node, cost, graph_id) VALUES (%s, %s, %s, %s, %s)", (*edge, graph_data[0]))
            conn.commit()


def set_graph_id(graph_id):
    """Set the graph id for the query service."""
    with open("graph_id.txt", "w") as f:
        f.write(graph_id)

if __name__ == '__main__':
    set_up_graph_data()
