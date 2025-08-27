import pygame
import threading
from core.Player import Player
from core.Enemigo import Enemigo
from core.Bala import Bala
from items.Item import Item
from items.Inventario import Inventario
from network.network import cliente, send_pickle, recv_pickle, escuchar_servidor
from systems import Grid, weapons, shield, ui, game_state


pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("WPOSS")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
player_template = Player(0,0)

# ---------------- RED ---------------- #
all_players = {}
cliente_id_container = {}
threading.Thread(
    target=escuchar_servidor, args=(all_players, cliente_id_container), daemon=True
).start()
print(f"Conectado al servidor en {cliente.getpeername()}")

# ---------------- JUEGO ---------------- #
player = Player(screen.get_width() / 2, screen.get_height() / 2)
enemigo = Enemigo(800, 300)
balas_group = pygame.sprite.Group()
player_shield = shield.PlayerShield(player.rect.centerx, player.rect.centery)
grid = Grid.Grid(2000, 2000, 32)
ui = ui.UI(font, player_template.animaciones)
arma = weapons.Weapon(player,"Pistola", 10, 20)


inventario = Inventario()
for nombre in ["Pistola", "Construir", "Escudo", "Pocion", "Llave", "Capa"]:
    inventario.add_item(Item(nombre))

running, dt = True, 0
selected_item, count = 0, 20
item_select = ""

# ---------------- LOOP PRINCIPAL ---------------- #
while running:
    offset = grid.update(player, screen)

    # -------- EVENTOS -------- #
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui.handle_events(event, player, inventario.get_item(item_select), balas_group, offset,count)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_v]:
            player.bullets = 0
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_r]:
                arma.start_reload()
            if keys[pygame.K_f]:
                player_shield.activate_shield()
            if keys[pygame.K_q]:
                item_select = "Pistola"

    # -------- UPDATE -------- #
    weapons.Bullet.update_balas(balas_group, dt=0.95)
    arma.update()
    game_state.GameState.check_gameover(player)
    player.update(dt)
    player_shield.update((player.rect.centerx- offset[0], player.rect.centery - offset[1]))
    # -------- ENVIAR DATOS AL SERVER -------- #
    data = {
        'x': player.pos.x,
        'y': player.pos.y,
        'estado': player.estado,
        'is_dashing': player.is_dashing,
        'balas': [{'x': b.rect.x, 'y': b.rect.y} for b in balas_group],
        'colisiones': [],
        'escudo_activo': player_shield.active,
    }
    #print("Enviando datos al servidor:", data)
    send_pickle(cliente, data)

    # -------- DRAW -------- #
    screen.fill("black")
    ui.draw_cuadricula(player, screen, screen.get_width(), screen.get_height(), 120)
    ui.draw_players(screen, font, all_players, player, offset, arma, balas_group, player_shield)
    ui.draw_hud(screen, font, player, clock, inventario, selected_item, count)
    ui.draw_cursor(screen)
    arma.draw_recarga(screen, font)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
