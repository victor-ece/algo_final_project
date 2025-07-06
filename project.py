import networkx as nx
import csv
import time


def read_csv_to_graph(file_path):
    G = nx.Graph()
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            u, v, = int(row[0]), int(row[1])
            G.add_edge(u, v)
        for u, v in G.edges():
            G[u][v]['capacity'] = 1
    return G

def read_csv_to_graph2(file_path):
    G = nx.read_edgelist(file_path, nodetype=int)

    nx.set_edge_attributes(G, 1, 'capacity')
    return G

def is_connected_dfs(G):
    components = []

    nodes = list(G.nodes())
    first_component_nodes = set(nx.dfs_preorder_nodes(G, source=nodes[0]))
    visited = set((first_component_nodes))

    # Early exit: graph is connected
    if len(visited) == len(G):
        return None

    components.append(G.subgraph(first_component_nodes).copy())

    # Continue DFS for remaining components
    for node in G.nodes():
        if node not in visited:
            component_nodes = set(nx.dfs_preorder_nodes(G, source=node))
            visited.update(component_nodes)
            components.append(G.subgraph(component_nodes).copy())

    return components
    
def recursive_clustering(G, depth):
    global stats_per_depth, final_clusters
    if depth not in stats_per_depth:
        stats_per_depth[depth] = []
        stats_per_depth[depth].append(len(G.nodes()))
    else:
        stats_per_depth[depth] = stats_per_depth[depth] + [len(G.nodes())]

    if len(G) <= 5:
        final_clusters.append(G)
        return
    
    components = is_connected_dfs(G)
    if components is not None:
        print(f"Graph is disconnected at depth {depth}, found {len(components)} components")
        for component in components:
            recursive_clustering(component, depth + 1)
        return
               
    u, v = find_best_st(G)
    
    cut_value, S, T = min_cut(G, u, v)
    split_tree_data.append((depth, len(G.nodes()), len(S.nodes()), len(T.nodes())))

    recursive_clustering(S, depth + 1)
    recursive_clustering(T, depth + 1)

    return

def find_best_st(G, top_k=4):
    # Get top-k degree nodes
    top_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:top_k]

    max_dist = -1
    best_pair = (None, None)

    # Try all pairs among top-k
    for i in range(len(top_nodes)):
        for j in range(i + 1, len(top_nodes)):
            u, v = top_nodes[i], top_nodes[j]
            dist = nx.shortest_path_length(G, source=u, target=v)
            if dist > max_dist:
                max_dist = dist
                best_pair = (u, v)


    return best_pair

def min_cut(G,u,v):

    cut_value, (S, T) = nx.minimum_cut(G, u, v)

    #print(f"Partition S (size {len(S)})")
    #print(f"Partition T (size {len(T)}")
    subgraph_S = G.subgraph(S).copy()
    subgraph_T = G.subgraph(T).copy()

    return cut_value, subgraph_S, subgraph_T

def main():
    file_path = 'erdos_coauthors.txt'  # Change this to the desired file path
    all_execution_times = []
    all_graph_sizes = []

    global stats_per_depth, final_clusters, split_tree_data
    
    split_tree_data = [] 
    final_clusters = []
    stats_per_depth = {}
    
    print(f"\n=========================================")
    print(f"Processing graph: {file_path}")
    print(f"=========================================")
    
    if file_path == 'karate.edgelist':
        G = read_csv_to_graph(file_path)
    else:
        G = read_csv_to_graph2(file_path)
        
    all_graph_sizes.append(len(G.nodes()))

    start_time = time.time()
    recursive_clustering(G, 0)
    end_time = time.time()
    total_time = end_time - start_time
    all_execution_times.append(total_time)

    print("\n--- Run Summary ---")
    print(f"Clustering finished for {file_path}.")
    print(f"Found {len(final_clusters)} final clusters.")
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()