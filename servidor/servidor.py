import socket   # comunicacion en la red
import threading   # manejo de multiples clientes a la vez
import pickle   # para serializar y deserializar objetos de python
import uuid     # para generar IDs únicos
import struct   # para manejar la longitud de los datos enviados




def send_pickle(sock, obj):
    """Serializa y envía un objeto con su longitud primero."""
    data = pickle.dumps(obj)
    length = struct.pack('!I', len(data))  # Longitud del objeto serializado
    sock.sendall(length + data)


def recv_pickle(sock):
    """Recibe un objeto serializado respetando su longitud."""
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

def get_local_server():
    """Obtiene la dirección IP y el puerto del servidor local."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        HOST = s.getsockname()[0]
    except Exception as e:
        print(f"Error al obtener la dirección del servidor: {e}")
    finally:
        s.close()
    return HOST


HOST = get_local_server()  # IP del servidor local
PORT = 1313

# Configuración de la red
player_data = {}   # para guardar la posición del jugador
clients = {}       # asocia cada conexión de socket con un ID de jugador

def cliente_thread(conn, addr):
    print(f"Conexión establecida con {addr}")
    player_id = str(uuid.uuid4())
    clients[conn] = player_id

    # Estado inicial del jugador
    player_data[player_id] = {
        'x': 100,
        'y': 100,
        'balas': list(),   # lista de balas activas
        'colisiones': [],
        'estado': 'default',
        'vida': 100,
        'vida_max': 100,
        'nombre': f"Jugador_{player_id[:5]}",
    }

    # Enviar al cliente su ID único
    send_pickle(conn, {"type": "id", "player_id": player_id})

    while True:
        try:
            paquete = recv_pickle(conn)  # usar la versión segura
            if not paquete:
                print(f"Conexión cerrada por {addr}")
                break

            # Actualizar datos de este jugador
            player_data[player_id].update(paquete)

            # Mostrar info si quieres debug
            #print(f"Info {player_id}: {player_data[player_id]}")

            # Mandar posiciones actualizadas a todos
            updated_data = player_data.copy()

            # Si hay colisiones, mostrarlas
            if 'colisiones' in player_data[player_id] and paquete.get('colisiones'):
                print(f"Colisiones de {player_id}: {paquete['colisiones']}")

            # Reenviar a todos los clientes
            for client in list(clients.keys()):
                try:
                    send_pickle(client, updated_data)
                except socket.error:
                    client.close()
                    cid = clients.get(client)

                    if client in clients:
                        del clients[client]

                    if cid in player_data:
                        del player_data[cid]
                    break

        except Exception as e:
            #print(f"Error con {addr}: {e}")
            print(f"Cerrando sesion con el cliente {addr}")
            break

    # Limpiar al desconectar
    clients.pop(conn, None)
    player_data.pop(player_id, None)
    conn.close()


# Configuración del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((HOST, PORT))
except OSError as e:
    print(f"Error: El puerto {PORT} ya está en uso o no se puede enlazar. {e}")
    try:
        PORT = 5000
        server.bind((HOST, PORT))
        print(f"Puerto cambiado a {PORT}")
    except OSError as e2:
        print(f"Error: El puerto 5000 también está en uso o no se puede enlazar. {e2}")
        exit(1)

server.listen(5)
print("Servidor iniciado, esperando conexiones...")
print(f"Servidor escuchando en {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    threading.Thread(target=cliente_thread, args=(conn, addr), daemon=True).start()
