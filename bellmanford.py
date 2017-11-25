import json
import socket
import threading
import time


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


def request_listener(server, graph):
    while True:
        request, message = server.recvfrom(1024)[0].split('|')

        if request == 'update':
            loaded = json.loads(message)
            str_source_id = loaded.keys()[0]
            source_id = int(str_source_id)

            items = loaded[str_source_id].items()

            if len(items) == 1:
                destination_id, cost = int(items[0][0]), int(items[0][1])

                graph[source_id][destination_id] = cost
                graph[destination_id][source_id] = cost
            else:
                for destination_id, cost in items:
                    graph[source_id][int(destination_id)] = cost


def routinely_update_neighbors(server, graph, source, addresses, frequency):
    while True:
        update_neighbors(server, source, addresses, {
            source: graph[source]
        })
        time.sleep(frequency)


def update_neighbors(server, source, addresses, mapping):
    for address_id in addresses:
        if address_id != source:
            message = 'update|' + json.dumps(mapping)
            server.sendto(message, addresses[address_id])


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
                    continue
                elif command == 'disable':
                    print 'disable <server-id>'
                    continue

                if command == 'update' and len(response) == 4:
                    source_id = int(response[1])
                    destination_id = int(response[2])
                    cost = int(response[3])

                    # Update table locally
                    graph[source_id][destination_id] = cost
                    graph[destination_id][source_id] = cost

                    update_neighbors(server, source_node, addresses, {
                        source_id: {destination_id: cost}
                    })

                    continue
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
                            next_hop = str(packets[node]) if packets[node] \
                                else 'none'
                            print '%4d %4s %4.0f' % (node, next_hop,
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

                    routinely_update = \
                        threading.Thread(target=routinely_update_neighbors,
                                         args=(server, graph, source_node,
                                               addresses, int(response[4])))
                    routinely_update.daemon = True
                    routinely_update.start()

                    listener = threading.Thread(target=request_listener,
                                                args=(server, graph))
                    listener.daemon = True
                    listener.start()

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
