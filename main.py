import pygame
import socket
import pickle
import threading
import struct
import core.Animacion as Animacion
import core.Player as Player
from items.Item import Item
import items.Inventario as Inventario
from core.Bala import Bala
from core.Enemigo import Enemigo


pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("WPOSS")
clock = pygame.time.Clock()

# ---------------- RED ---------------- #
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(('192.168.1.202', 1313))

all_players = {}

# Función para enviar un objeto con pickle + longitud
def send_pickle(sock, obj):
    try:
        payload_bytes = pickle.dumps(obj)  # >>> FIX: nombre más claro, no sombrea 'data'
        length = struct.pack('!I', len(payload_bytes))  # Longitud de 4 bytes
        sock.sendall(length + payload_bytes)
    except Exception as e:
        print(f"Error al enviar datos: {e}")
        print(f"Servidor desconectado")
        pygame.quit()

# Función para recibir un objeto con pickle + longitud
def recv_pickle(sock):
    try:
        # Recibir los 4 bytes de longitud
        length_data = sock.recv(4)
        if not length_data:
            return None
        length = struct.unpack('!I', length_data)[0]

        # Recibir todos los datos
        data = b''
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data += packet

        return pickle.loads(data)
    except Exception as e:
        print(f"Error al recibir datos: {e}")
        return None

# Hilo de escucha de datos del servidor
def escuchar_servidor():
    global all_players
    while True:
        incoming = recv_pickle(cliente)
        if incoming:
            # >>> FIX: asume que el servidor envía un dict {pid: {'x','y','balas':[...]} }
            if isinstance(incoming, dict):
                all_players = incoming
            else:
                # si llega cualquier otra cosa, solo lo reportamos
                print("Paquete no reconocido:", type(incoming))
        else:
            print("Servidor desconectado")
            break

# Lanzar el hilo de escucha
threading.Thread(target=escuchar_servidor, daemon=True).start()
print(f"Conectado al servidor en {cliente.getpeername()}")


# ---------------- FUENTES E INVENTARIO ---------------- #
font = pygame.font.Font(None, 36)

inventario = Inventario.Inventario()
inventario.add_item(Item("Pistola"))
inventario.add_item(Item("Construir"))
inventario.add_item(Item("Escudo"))
inventario.add_item(Item("Pocion"))
inventario.add_item(Item("Llave"))
inventario.add_item(Item("Capa"))
inventario.add_item(Item("xxxxxxx"))
inventario.add_item(Item("xxxxx"))

balas_group = pygame.sprite.Group()
running = True
dt = 0
selected_item = None
count = 20
cooldown_time = 1500  # 1.5 seg de recarga
last_recarga = -cooldown_time
recargando = False
rec_escudo = False
tiempo_inicio_recarga = 0
tiempo_restante_cooldown = 0
escudo_activo = False
escudo_rect = None
ultimo_uso_escudo = 0
tiempo_activacion_escudo = 0

rectangulos = []
rectangulos_colision = []

player = Player.Player(screen.get_width() / 2, screen.get_height() / 2)
enemigo = Enemigo(800, 300)

# ---------------- FUNCIONES ---------------- #

def cuadricula(offset):
    start_x = int(offset.x // 120) * 120
    end_x = start_x + screen.get_width() + 240
    start_y = int(offset.y // 120) * 120
    end_y = start_y + screen.get_height() + 240

    for x in range(start_x, end_x, 120):
        pygame.draw.line(screen, "red", (x - offset.x, 0), (x - offset.x, screen.get_height()))

    for y in range(start_y, end_y, 120):
        pygame.draw.line(screen, "red", (0, y - offset.y), (screen.get_width(), y - offset.y))

def cursorpersonalizado():
    mouse = pygame.mouse.get_pos()
    pygame.draw.circle(screen, "blue", mouse, 15, 8)
    pygame.mouse.set_visible(False)

def pintarcuadrodecuadricula():
    mouse = pygame.mouse.get_pos()
    offset = get_camera_offset(player, screen)
    world_x = int((mouse[0] + offset.x) // 120) * 120
    world_y = int((mouse[1] + offset.y) // 120) * 120

    if [world_x, world_y, 120, 120] not in rectangulos:
        rectangulos.append([world_x, world_y, 120, 120])
        rectangulos_colision.append(pygame.Rect(world_x, world_y, 120, 120))
    else:
        print("Ya existe un rectángulo en esa posición")

def eliminarcuadrodecuadricula():
    mouse = pygame.mouse.get_pos()
    offset = get_camera_offset(player, screen)
    world_x = int((mouse[0] + offset.x) // 120) * 120
    world_y = int((mouse[1] + offset.y) // 120) * 120

    for i, rect in enumerate(rectangulos):
        if rect[0] == world_x and rect[1] == world_y:
            rectangulos.pop(i)
            rectangulos_colision[:] = [rc for rc in rectangulos_colision if rc.topleft != (world_x, world_y)]
            break

def playerhitbox():
    hitbox = pygame.Rect(player.pos.x - 60, player.pos.y - 60, 120, 120)
    offset = get_camera_offset(player, screen)
    draw_hitbox = hitbox.copy()
    draw_hitbox.topleft -= offset
    pygame.draw.rect(screen, "blue", draw_hitbox, 5)
    return hitbox

def recorrercolision():
    for rect in rectangulos_colision:
        if playerhitbox().colliderect(rect):
            if player.rect.right > rect.left and player.pos.x < rect.left:
                player.pos.x = rect.left - player.width / 2
            elif player.rect.left < rect.right and player.pos.x > rect.right:
                player.pos.x = rect.right + player.width / 2
            if player.rect.bottom > rect.top and player.pos.y < rect.top:
                player.pos.y = rect.top - player.height / 2
            elif player.rect.top < rect.bottom and player.pos.y > rect.bottom:
                player.pos.y = rect.bottom + player.height / 2

def reiniciar():
    global escudo_activo, escudo_rect, count, tiempo_restante_cooldown
    rectangulos.clear()
    tiempo_restante_cooldown = 0
    rectangulos_colision.clear()
    player.pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    escudo_activo = False
    escudo_rect = None
    count = 20
    player.health = 100
    balas_group.empty()  # >>> FIX: método correcto para vaciar el grupo

def get_camera_offset(player, screen):
    return pygame.Vector2(
        player.rect.centerx - screen.get_width() // 2,
        player.rect.centery - screen.get_height() // 2
    )

def escoger_item():
    keys = pygame.key.get_pressed()
    for i in range(min(8, len(inventario.items))):
        if keys[pygame.K_1 + i]:
            return inventario.items[i]
    return None

def disparar_pistola(player, screen, offset):
    mouse_pos = pygame.mouse.get_pos()
    mouse_world_pos = pygame.Vector2(mouse_pos[0] + offset.x, mouse_pos[1] + offset.y)
    start_pos = pygame.Vector2(player.pos.x, player.pos.y)
    direction = mouse_world_pos - start_pos

    if direction.length() > 0:
        direction = direction.normalize()
        start_pos += direction * 100  # sale desde fuera del jugador

    nueva_bala = Bala(start_pos, direction)
    balas_group.add(nueva_bala)

def manejar_recarga():
    global recargando, count, tiempo_inicio_recarga, last_recarga
    current_time = pygame.time.get_ticks()

    if count <= 0 and not recargando:
        recargando = True
        tiempo_inicio_recarga = current_time
        print("Recargando...")

    if recargando:
        tiempo_restante = (cooldown_time - (current_time - tiempo_inicio_recarga)) / 1000
        if tiempo_restante <= 0:
            recargando = False
            count = 20
            print("Pistola recargada")
            last_recarga = current_time
        else:
            print(f"Tiempo restante de recarga: {tiempo_restante:.1f} segundos")

def dibujar_recarga():
        tiempo_restante = (cooldown_time - (pygame.time.get_ticks() - tiempo_inicio_recarga)) / 1000
        texto_recargando = font.render(f"Recargando... {tiempo_restante:.1f}s", True, (255, 255, 0))
        if tiempo_restante < 0:
            texto_recargando = font.render("Recarga completa", True, (0, 255, 0))
            recargando = True
            manejar_recarga()
        screen.blit(texto_recargando, (screen.get_width() // 2 - texto_recargando.get_width() // 2, screen.get_height() // 2 - texto_recargando.get_height() // 2))

def activar_escudo():
    global escudo_activo, escudo_rect, ultimo_uso_escudo, tiempo_activacion_escudo
    current_time = pygame.time.get_ticks()
    cooldown_escudo = 5000
    duracion_escudo = 5000

    if escudo_activo:
        if current_time - tiempo_activacion_escudo >= duracion_escudo:
            print("Escudo desactivado")
            escudo_activo = False
            escudo_rect = None
            ultimo_uso_escudo = current_time
        return

    if current_time - ultimo_uso_escudo >= cooldown_escudo:
        print("Escudo activado")
        escudo_activo = True
        tiempo_activacion_escudo = current_time
        escudo_rect = pygame.Rect(player.pos.x - 80, player.pos.y - 80, 160, 160)
    else:
        tiempo_restante = (cooldown_escudo - (current_time - ultimo_uso_escudo)) / 1000
        print(f"Escudo en cooldown: {tiempo_restante:.1f}s restantes")

def dibujar_estado_escudo():
    global escudo_activo, ultimo_uso_escudo, tiempo_activacion_escudo, tiempo_restante_cooldown
    current_time = pygame.time.get_ticks()
    cooldown_escudo = 5000
    duracion_escudo = 5000

    if escudo_activo:
        tiempo_restante_duracion = (duracion_escudo - (current_time - tiempo_activacion_escudo)) / 1000
        if tiempo_restante_duracion > 0:
            texto_duracion = font.render(f"Escudo activo: {tiempo_restante_duracion:.1f}s", True, ("Green"))
            screen.blit(texto_duracion, (10, 160))
        else:
            escudo_activo = False
            ultimo_uso_escudo = current_time
    else:
        tiempo_restante_cooldown = (cooldown_escudo - (current_time - ultimo_uso_escudo)) / 1000
        if tiempo_restante_cooldown > 0:
            texto_cooldown = font.render(f"Escudo cooldown: {tiempo_restante_cooldown:.1f}s", True, ("Orange"))
            screen.blit(texto_cooldown, (10, 190))
        else:
            texto_listo = font.render("Escudo listo", True, (0, 255, 0))
            screen.blit(texto_listo, (10, 220))

def dibujar_escudo():
    global escudo_activo, escudo_rect
    if escudo_activo and escudo_rect:
        offset = get_camera_offset(player, screen)
        escudo_rect.center = player.pos
        draw_shield = escudo_rect.copy()
        draw_shield.topleft -= offset
        pygame.draw.rect(screen, "blue", draw_shield, 5)

def colisionBalaMuro():
    for bala in list(balas_group):
        for rect in rectangulos_colision:
            if bala.rect.colliderect(rect):
                overlap_left = bala.rect.right - rect.left
                overlap_right = rect.right - bala.rect.left
                overlap_top = bala.rect.bottom - rect.top
                overlap_bottom = rect.bottom - bala.rect.top

                min_overlap_x = min(overlap_left, overlap_right)
                min_overlap_y = min(overlap_top, overlap_bottom)

                if min_overlap_x < min_overlap_y:
                    bala.direction.x = -bala.direction.x
                    if overlap_left < overlap_right:
                        bala.rect.right = rect.left
                    else:
                        bala.rect.left = rect.right
                else:
                    bala.direction.y = -bala.direction.y
                    if overlap_top < overlap_bottom:
                        bala.rect.bottom = rect.top
                    else:
                        bala.rect.top = rect.bottom
                bala.pos.x = bala.rect.centerx
                bala.pos.y = bala.rect.centery
                break

def colisionJugadorBala():
    for bala in list(balas_group):
        if bala.rect.colliderect(player.rect):
            balas_group.remove(bala)
            player.health -= 20
            print("Colisión entre jugador y bala")
            if player.health <= 0:
                print("Has perdido")
                screenGameOver()
            break

def screenGameOver():
    global running
    game_over_text = font.render("GAME OVER", True, "red")
    screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2,
                screen.get_height() // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)
    reiniciar()
    running = False

def colisionBalaEscudo():
    global escudo_activo, escudo_rect
    if escudo_activo and escudo_rect:
        for bala in list(balas_group):
            if bala.rect.colliderect(escudo_rect):
                balas_group.remove(bala)
                break

def colisionplayerenemigo():
    if enemigo.rect.colliderect(player.rect):
        player.health -= 10
        empujar_enemigo()
        print("Colisión entre jugador y enemigo")
        if player.health <= 0:
            print("Has perdido")
            screenGameOver()

    if escudo_activo and escudo_rect and enemigo.rect.colliderect(escudo_rect):
        overlap_left = enemigo.rect.right - escudo_rect.left
        overlap_right = escudo_rect.right - enemigo.rect.left
        overlap_top = enemigo.rect.bottom - escudo_rect.top
        overlap_bottom = escudo_rect.bottom - enemigo.rect.top

        min_overlap_x = min(overlap_left, overlap_right)
        min_overlap_y = min(overlap_top, overlap_bottom)

        if min_overlap_x < min_overlap_y:
            if overlap_left < overlap_right:
                enemigo.rect.right = escudo_rect.left
            else:
                enemigo.rect.left = escudo_rect.right
        else:
            if overlap_top < overlap_bottom:
                enemigo.rect.bottom = escudo_rect.top
            else:
                enemigo.rect.top = escudo_rect.bottom

    for bala in list(balas_group):
        if bala.rect.colliderect(enemigo.rect):
            enemigo.recibir_dano(20)
            balas_group.remove(bala)
            if enemigo.vida <= 0:
                enemigo.eliminar()
                print("Enemigo eliminado")

def empujar_enemigo():
    direction_x = enemigo.rect.centerx - player.rect.centerx
    direction_y = enemigo.rect.centery - player.rect.centery
    push_distance = 200
    if direction_x != 0:
        enemigo.rect.centerx += push_distance if direction_x > 0 else -push_distance
    if direction_y != 0:
        enemigo.rect.centery += push_distance if direction_y > 0 else -push_distance

# ---------------- LOOP PRINCIPAL ---------------- #
while running:
    # >>> FIX: calcular offset ANTES de usarlo en eventos (evita "offset referenced before assignment")
    offset = get_camera_offset(player, screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if count <= 0:
                    manejar_recarga()
            if event.key == pygame.K_q:
                selected_item = inventario.items[0]  # Pistola
            if event.key == pygame.K_3:
                selected_item = inventario.items[1]  # Construir

        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected_item and selected_item.name == "Construir":
                if event.button == 1:  # Izquierdo
                    eliminarcuadrodecuadricula()
                elif event.button == 3:  # Derecho
                    pintarcuadrodecuadricula()

            if selected_item and selected_item.name == "Pistola":
                if event.button == 1 and count > 0:
                    disparar_pistola(player, screen, offset)
                    count -= 1
                elif count <= 0:
                    print("Sin balas")

    screen.fill("black")

    current_time = pygame.time.get_ticks()

    # Dibujo de elementos
    cuadricula(offset)
    for rectangulo in rectangulos:
        draw_rect = pygame.Rect(rectangulo)
        draw_rect.topleft -= offset
        pygame.draw.rect(screen, "green", draw_rect)

    # ----------------- JUGADOR LOCAL ----------------- #
    #player.draw(screen, offset)
    player.update(dt)



    # Enviar posición al servidor
    try:
        envia = {
            'x': player.pos.x,
            'y': player.pos.y,
            'balas': [{'x': b.rect.x, 'y': b.rect.y} for b in balas_group],
            'colisiones': [],
            'estado': player.estado,  # Enviar el estado actual del jugador
            'is_dashing': player.is_dashing
        }
        #print(f"Datos a enviar: {envia}")
        send_pickle(cliente, envia)
    except (socket.error, pickle.PicklingError) as e:
        print(f"Error al enviar datos al servidor: {e}")
        running = False


    # ----------------- OTROS JUGADORES ----------------- #
    for pid, pdata in all_players.items():
        if isinstance(pdata, dict):
            # No dibujarme a mí mismo (opcional)
            #print(f"[Logger] Datos recibidos para jugador {pid}: {pdata}")
            if pid != {pid}:
                rect = pygame.Rect(
                    pdata.get('x', 0) - 25 - offset.x,
                    pdata.get('y', 0) - 25 - offset.y,
                    50, 50
                )
                #pygame.draw.rect(screen, "yellow", rect)
                nombre = f"Player {pid}"[:12]  # Limita a 12 caracteres
                nombre_text = font.render(nombre, True, "yellow")
                screen.blit(nombre_text, (rect.x, rect.y - 25))

            estado = pdata.get('estado', player.estado) or 'default'
            is_dashing = pdata.get('is_dashing', False)

            animacion = player.animaciones.get(estado, player.animaciones[estado])
            if animacion:
                frame = animacion.update()
                frame_rect = frame.get_rect(center=(pdata.get('x', 0) - offset.x, pdata.get('y', 0) - offset.y))
                screen.blit(frame, frame_rect)
                if is_dashing:
                    dash_effect = player.animaciones['dash'].update()
                    dash_effect.set_alpha(120)  # semitransparente
                    screen.blit(dash_effect, frame_rect.topleft)

        # Dibuja balas remotas si existen
        for bala_pos in pdata.get('balas', []):
            bala_rect = pygame.Rect(
                bala_pos['x'] - 5 - offset.x,
                bala_pos['y'] - 5 - offset.y,
                20, 20
            )
            pygame.draw.rect(screen, "green", bala_rect)
            #colision bala con jugador
            if bala_rect.colliderect(player.rect):
                colision_data = {
                    'tipo': 'colision_bala_jugador',
                    'jugador': pid,
                    'bala': {'x': bala_pos['x'], 'y': bala_pos['y']},
                    'jugador_afectado': {'x': player.pos.x, 'y': player.pos.y}
                }
                print(f"Colisión detectada: {colision_data}")
                envia['colisiones'].append(colision_data)

    # ----------------- ENEMIGO Y DEMÁS ----------------- #
    dibujar_estado_escudo()
    dibujar_escudo()
    colisionJugadorBala()
    colisionBalaEscudo()
    recorrercolision()
    colisionBalaMuro()
    #player.draw(screen, offset)
    if recargando or rec_escudo:
        # Mostrar "Recargando..." en el centro de la pantalla
        dibujar_recarga()

    for bala in list(balas_group):
        bala.update()
        #bala.draw(screen, offset)

    # Inventario
    inventory_width = 6 * 100 + 5 * 10
    x_centered = (screen.get_width() - inventory_width) // 2
    inventario.display_inventory(screen, x_centered, screen.get_height() - 130, (80, 60))

    # Debug UI

    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
    coord_text = font.render(f"x: {player.pos.x:.2f}, y: {player.pos.y:.2f}", True, "white")
    inventario_text = font.render(f"Ítem seleccionado: {selected_item.name}" if selected_item else "No hay ítem seleccionado", True, "Yellow")
    balas_text = font.render(f"Balas: {count}" if count > 0 else "Recargar", True, "white")
    vida_text = font.render(f"Vida: {player.health}%", True, "Red")

    screen.blit(fps_text, (10, 10))
    screen.blit(coord_text, (10, 40))
    screen.blit(inventario_text, (10, 70))
    screen.blit(balas_text, (10, 100))
    screen.blit(vida_text, (10, 130))

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        running = False
    if pygame.key.get_pressed()[pygame.K_f]:
        selected_item = inventario.items[2]
        activar_escudo()

    cursorpersonalizado()
    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
