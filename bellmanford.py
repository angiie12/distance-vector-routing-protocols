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


def main():
    graph = {
        'a': {'b': 7, 'c': 4, 'd': 5},
        'b': {'a': 7, 'c': 2},
        'c': {'a': 4, 'b': 2, 'd': 1},
        'd': {'a': 5, 'c': 1},
    }

    for source in graph:
        d, p = bellman_ford(graph, source)

        print 'Source: %s' % source
        print d
        print p


if __name__ == '__main__':
    main()
