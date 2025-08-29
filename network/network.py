import pickle
import socket
import struct



# Dirección IP y puerto del servidor al que se conectará el cliente
def get_server_address():
     # Crear un socket TCP/IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        IP_LOCAL = s.getsockname()[0]
    except Exception as e:
        print(f"Error al conectar con el servidor: {e}")
        IP_LOCAL = "127.0.0.1"  #"192.168.1.202"
    finally:
        s.close()
    return IP_LOCAL


IP_SERVIDOR = get_server_address()
PUERTO = 1313


# Conectar el socket al servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((IP_SERVIDOR, PUERTO))
def recv_pickle(sock):
    # Primero recibimos 4 bytes con el tamaño
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]

    # Luego recibimos el resto de los datos
    data = recvall(sock, msglen)
    return pickle.loads(data)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_pickle(sock, data):
    """
    Envía un objeto serializado (pickle) a través del socket,
    asegurándose de que el receptor sepa cuántos bytes esperar.
    """
    try:
        # Serializamos el objeto
        serialized_data = pickle.dumps(data)
        # Empaquetamos la longitud (4 bytes en big endian)
        data_length = struct.pack("!I", len(serialized_data))
        # Enviamos primero la longitud y luego los datos
        sock.sendall(data_length + serialized_data)

    except Exception as e:
        print(f"Error al enviar datos: {e}")
        sock.close()


def escuchar_servidor(all_players, cliente_id_container):
    while True:
        try:
            data = recv_pickle(cliente)
            if data is None:
                break

            if isinstance(data, dict) and data.get("type") == "id":
                # Guardar ID único asignado por el servidor
                cliente_id_container["id"] = data["player_id"]
                print(f"Mi ID único es: {cliente_id_container['id']}")
                continue

            # Si no es un paquete de tipo "id", debe ser el diccionario de jugadores
            all_players.clear()
            all_players.update(data)

        except Exception as e:
            print(f"Error en la escucha del servidor: {e}")
            cliente.close()
            break

