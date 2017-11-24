import json
import socket

address = ('127.0.0.1', 2048)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

update_nodes = [
    {2: {1: 7, 3: 2}}, # Client is a source node
    {2: {1: 8}}, # Update cost with node 1
    {4: {1: 5, 3: 1}}, # Node 4 made contact with us, and gave us its table
    {3: {1: 4, 2: 2, 4: 1}}, # Node 3 did the same as node 4
]

for update in update_nodes:
    message = 'update|' + json.dumps(update)
    client.sendto(message, address)

client.sendto('exit|', address)

client.close()
