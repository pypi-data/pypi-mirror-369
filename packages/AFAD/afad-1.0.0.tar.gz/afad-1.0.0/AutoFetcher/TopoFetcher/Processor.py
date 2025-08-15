import networkx as nx
import math

from networkx.algorithms import isomorphism


def _calculate_node_similarity(G1, G2):
    """
    Calculates a similarity score based on the number of nodes.
    The score is a percentage based on the smaller graph's size relative to the larger one.
    """
    num_nodes1 = G1.number_of_nodes()
    num_nodes2 = G2.number_of_nodes()

    if num_nodes1 == 0 and num_nodes2 == 0:
        return 1.0  # Both are empty, perfect match
    if num_nodes1 == 0 or num_nodes2 == 0:
        return 0.0  # One is empty, one is not. No similarity.

    return min(num_nodes1, num_nodes2) / max(num_nodes1, num_nodes2)


def _calculate_edge_similarity(G1, G2):
    """
    Calculates a similarity score based on the number of edges.
    The score is a percentage based on the smaller edge count relative to the larger one.
    """
    num_edges1 = G1.number_of_edges()
    num_edges2 = G2.number_of_edges()

    if num_edges1 == 0 and num_edges2 == 0:
        return 1.0  # Both are empty, perfect match
    if num_edges1 == 0 or num_edges2 == 0:
        return 0.0  # One has edges, one does not. No similarity.

    return min(num_edges1, num_edges2) / max(num_edges1, num_edges2)


def _calculate_degree_similarity(G1, G2):
    """
    Calculates a similarity score based on the degree distributions of the graphs.
    This uses the Jensen-Shannon divergence to measure how similar the distributions are.
    A score of 1.0 is a perfect match, 0.0 is no similarity.
    """
    # Get degree sequences
    degrees1 = [d for n, d in G1.degree()]
    degrees2 = [d for n, d in G2.degree()]

    # Handle empty graphs
    if not degrees1 and not degrees2:
        return 1.0
    if not degrees1 or not degrees2:
        return 0.0

    # Calculate frequency distributions
    max_degree = max(max(degrees1) if degrees1 else 0, max(degrees2) if degrees2 else 0)
    hist1 = [0] * (max_degree + 1)
    hist2 = [0] * (max_degree + 1)

    for d in degrees1:
        hist1[d] += 1
    for d in degrees2:
        hist2[d] += 1

    # Normalize to probability distributions
    dist1 = [count / len(degrees1) for count in hist1]
    dist2 = [count / len(degrees2) for count in hist2]

    # Calculate Jensen-Shannon divergence
    def kullback_leibler_divergence(p, q):
        return sum(p[i] * math.log2(p[i] / q[i]) for i in range(len(p)) if p[i] > 0 and q[i] > 0)

    m = [(dist1[i] + dist2[i]) / 2 for i in range(len(dist1))]
    jsd = 0.5 * kullback_leibler_divergence(dist1, m) + 0.5 * kullback_leibler_divergence(dist2, m)

    # Convert divergence to a similarity score (1 - sqrt(jsd) is a common method)
    # We need to make sure jsd is not negative due to floating point errors
    similarity_score = 1.0 - math.sqrt(max(0, jsd))
    return similarity_score


def compare_graphs(G1, G2):
    """
    Compares two NetworkX graphs and returns a similarity score from 0 to 100.

    Args:
        G1 (nx.Graph): The first graph.
        G2 (nx.Graph): The second graph.

    Returns:
        float: A similarity score from 0.0 to 100.0.
    """
    if not isinstance(G1, nx.Graph) or not isinstance(G2, nx.Graph):
        raise TypeError("Both inputs must be NetworkX graph objects.")

    # Assign weights to each similarity component.
    # You can adjust these weights to change the importance of each factor.
    # Ensure the sum of weights is 1.0.
    node_weight = 0.3
    edge_weight = 0.3
    degree_weight = 0.4

    # Calculate individual similarity scores
    node_sim = _calculate_node_similarity(G1, G2)
    edge_sim = _calculate_edge_similarity(G1, G2)
    degree_sim = _calculate_degree_similarity(G1, G2)

    # Calculate the final weighted average similarity score
    final_score = (node_sim * node_weight + edge_sim * edge_weight + degree_sim * degree_weight) * 100

    # Round to two decimal places for a clean output
    return round(final_score, 2)


def find_isomorphic_sub_graphs(G1, G2):
    """
    Finds the largest common subgraph between G1 and G2 based on isomorphism.
    This ignores node labels and focuses on structural similarity.

    Args:
        G1 (nx.Graph): The first graph.
        G2 (nx.Graph): The second graph.

    Returns:
        list: A list of dictionaries, where each dictionary represents a mapping
              from a node in G1 to its corresponding node in G2.
    """
    if not isinstance(G1, nx.Graph) or not isinstance(G2, nx.Graph):
        raise TypeError("Both inputs must be NetworkX graph objects.")

    print("\n--- Finding Isomorphic Subgraphs ---")

    # Use a maximum common subgraph algorithm to find a structural match
    gm = isomorphism.GraphMatcher(G1, G2)

    largest_subgraph_mapping = None
    largest_subgraph_size = 0

    # Iterate through all isomorphic subgraphs and find the largest one
    for subgraph_mapping in gm.subgraph_isomorphisms_iter():
        current_size = len(subgraph_mapping)
        if current_size > largest_subgraph_size:
            largest_subgraph_size = current_size
            largest_subgraph_mapping = subgraph_mapping

    if largest_subgraph_mapping:
        print(f"Largest common subgraph found with {largest_subgraph_size} nodes.")
        print("Mapping from G1 nodes to G2 nodes:")
        for node1, node2 in largest_subgraph_mapping.items():
            print(f"  G1 node '{node1}' is isomorphic to G2 node '{node2}'")
        return largest_subgraph_mapping
    else:
        print("No isomorphic subgraphs found.")
        return None
