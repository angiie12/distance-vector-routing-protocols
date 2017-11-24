import json
import socket
import sys
import threading


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


def load_topology(filename):
    addresses, graph = {}, {}

    with open(filename, 'r') as topology:
        lines = topology.readlines()
        num_of_nodes = int(lines[0])

        for node in range(num_of_nodes):
            graph.setdefault(node + 1, {})

        for line_num, line in enumerate(lines[2:]):
            if line_num < num_of_nodes:
                tokens = line.split()
                addresses[int(tokens[0])] = (tokens[1], int(tokens[2]))
            else:
                tokens = map(int, line.split())
                graph[tokens[0]][tokens[1]] = tokens[2]

    return addresses, graph


def request_listener(server):
    while True:
        request, _ = server.recvfrom(1024)
        sys.stdout.write('\n%s\n>>> ' % request)
        sys.stdout.flush()


def main():
    addresses = {}
    graph = {}
    running = False
    server = None
    source_node = 0

    print 'Distance Vector Routing Protocols Emulator'

    while True:
        response = raw_input('>>> ').split()

        if response:
            command = response[0].lower()

            if running:
                if command == 'disable' and len(response) == 2:
                    pass
                elif command == 'disable':
                    print 'disable <server-id>'
                    continue

                if command == 'update' and len(response) == 4:
                    pass
                elif command == 'update':
                    print 'update <server-id-1> <server-id-2> <cost>'
                    continue

                if command == 'crash' or command == 'exit':
                    server.close()
                    return
                elif command == 'display':
                    distance_vector, packets = bellman_ford(graph, source_node)

                    for node in distance_vector:
                        if distance_vector[node] != 0:
                            print '%d %d %.0f' % (node, packets[node],
                                                  distance_vector[node])
                elif command == 'packets':
                    print 0
                elif command == 'step':
                    pass
                else:
                    print '"%s" is not a valid command.' % command
            else:
                if command == 'server' and len(response) == 5:
                    addresses, graph = load_topology(response[2])

                    for node in graph:
                        if graph[node]:
                            source_node = node
                            break

                    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    server.bind(addresses[source_node])

                    for address_id in addresses:
                        if address_id != source_node:
                            message = 'update|' + json.dumps({
                                source_node: graph[source_node]
                            })
                            server.sendto(message, addresses[address_id])

                    thread = threading.Thread(target=request_listener,
                                              args=(server,))
                    thread.daemon = True
                    thread.start()

                    print 'Server is running on %s, port %d' % \
                        addresses[source_node]
                    running = True
                elif command == 'exit':
                    return
                else:
                    print 'Server is not running. Start it by typing:'
                    print 'server -t <topology-file> -i ' \
                          '<routing-update-interval>'


if __name__ == '__main__':
    main()
