import socket #comunicacion en la red
import threading #manejo de multiples clientes a la vez
import pickle #para serializar y deserealizar objetos de python
import uuid #para generar IDs únicos
import struct #para manejar la longitud de los datos enviados


def send_pickle(sock, obj):
    data = pickle.dumps(obj)
    length = struct.pack('!I', len(data))  # Longitud del objeto serializado
    sock.sendall(length + data)

def recv_pickle(sock):
    # Recibir la longitud del objeto
    length_data = sock.recv(4)
    if not length_data:
        return None
    length = struct.unpack('!I', length_data)[0]

    # Recibir el objeto completo
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet

    return pickle.loads(data)

# Configuración de la red
player_data = {}   # para guardar la posicion del jugador
clients = {}       # asocia cada conexion de socket con un ID de jugador

HOST = '192.168.1.202'
PORT = 1313

def cliente_thread(conn, addr):
    print(f"Conexión establecida con {addr}")
    player_id = str(uuid.uuid4())
    clients[conn] = player_id
    # Imprimir las colisiones recibidas (si existen en el paquete)
    player_data[player_id] = {
        'x': 100,
        'y': 100,
        'balas': list(),  # lista de las balas activas, asegurando una nueva lista por jugador
        'colisiones': [],
        'estado' : 'default'  # lista para almacenar el estado del jugador
    }
    while True:
        try:
            paquete = recv_pickle(conn)  # usar la versión segura
            if not paquete:
                print(f"Conexión cerrada por {addr}")
                break

            player_data[player_id] = paquete

            # Mostrar la información actualizada del jugador
            #print(f"Información actualizada de {player_id}: {player_data[player_id]}")

            # Mandar posiciones actualizadas a todos
            updated_data = player_data.copy()
            # Imprimir colisiones nuevas del jugador actual
            if 'colisiones' in player_data[player_id] and paquete['colisiones']:
                print(f"Colisiones recibidas de {player_id}: {paquete['colisiones']}")
            for client in list(clients.keys()):
                try:
                    send_pickle(client, updated_data)
                except socket.error:
                    client.close()  # Cierra la conexión
                    player_id = clients.get(client)  # obtiene el ID del cliente si existe

                    if client in clients:
                        del clients[client]  # elimina la asociación

                    if player_id in player_data:
                        del player_data[player_id]  # elimina datos del jugador
                    break

        except Exception as e:
            print(f"Error con {addr}: {e}")
            break

    # Limpiar al desconectar
    clients.pop(conn, None)
    player_data.pop(player_id, None)
    conn.close()

# Configuración del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
print("Servidor iniciado, esperando conexiones...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=cliente_thread, args=(conn, addr), daemon=True).start()
