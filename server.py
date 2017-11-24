import json
import socket

from bellmanford import bellman_ford


def update(graph, message):
    loaded = json.loads(message)
    key = loaded.keys()[0]
    node = int(key)

    for k, v in loaded[key].items():
        graph[node][int(k)] = v

    return graph


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 2048))

    addresses = {
        1: ('127.0.0.1', 2048),
        2: ('127.0.0.1', 2049),
        3: ('127.0.0.1', 2050),
        4: ('127.0.0.1', 2051),
    }

    source_node = 1  # Since we are 127.0.0.1:2048

    graph = {1: {2: 7, 3: 4, 4: 5}, 2: {}, 3: {}, 4: {}}

    while True:
        command, message = server.recvfrom(1024)[0].split('|')

        if command == 'update':
            graph = update(graph, message)
            print graph

            d, _ = bellman_ford(graph, source_node)

            for u in d:  # Print graph
                src = '%s:%d' % addresses[source_node]
                dst = '%s:%d' % addresses[u]

                print '%s -> %s  cost: %.0f' % (src, dst, d[u])

        elif command == 'exit':
            # sendto('crash|$node', (address, port))
            print 'Shutting down server...\nBye.'
            server.close()
            exit()

        print

    server.close()

if __name__ == '__main__':
    main()
