def bellman_ford(graph, source):
    d, p = {}, {}

    for node in graph:
        d[node] = float('inf')
        p[node] = None

    d[source] = 0

    for _ in range(len(graph) - 1):
        for u in graph:
            for v in graph[u]:
                if d[v] > d[u] + graph[u][v]:
                    d[v] = d[u] + graph[u][v]
                    p[v] = u

    return d, p


def load_topology(graph, filename):
    with open(filename, 'r') as topology:
        lines = topology.readlines()
        num_of_nodes = int(lines[0])

        for node in range(num_of_nodes):
            graph.setdefault(node + 1, {})

        for line in lines[2 + num_of_nodes:]:
            tokens = map(int, line.split())
            graph[tokens[0]][tokens[1]] = tokens[2]

    return graph


def main():
    graph = load_topology({}, 'topology-a.txt')
    graph = load_topology(graph, 'topology-b.txt')
    graph = load_topology(graph, 'topology-c.txt')
    graph = load_topology(graph, 'topology-d.txt')

    for source in graph:
        d, p = bellman_ford(graph, source)

        print 'Source: %s' % source
        print d
        print p


if __name__ == '__main__':
    main()
