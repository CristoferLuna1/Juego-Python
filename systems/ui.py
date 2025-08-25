import pygame

class UI:
    def __init__(self, font, player_animations):
        self.font = font
        self.player_animations = player_animations

    def draw_health(self, surface, player):
        text = self.font.render(f"HP: {player.health}", True, "red")
        surface.blit(text, (20, 20))

    def draw_name(self, surface, name, pos):
        text = self.font.render(name, True, "yellow")
        surface.blit(text, (pos[0], pos[1] - 30))

    def draw_inventory(self, surface, inventory, selected_item):
        # posición fija en pantalla
        x, y = 20, 100

        for i, item in enumerate(inventory.items):  # ojo: depende de cómo guardas el inventario
            color = "yellow" if selected_item == item else "white"
            text = self.font.render(item.name, True, color)
            surface.blit(text, (x, y + i * 20))

    def draw_cuadricula(self, player, surface, ancho, alto, tam_celda, color="red"):
        """
        Dibuja una cuadrícula en la pantalla.

        :param surface: superficie de pygame donde se dibuja
        :param ancho: ancho de la pantalla en píxeles
        :param alto: alto de la pantalla en píxeles
        :param tam_celda: tamaño de cada celda en píxeles
        :param color: color de las líneas de la cuadrícula
        """
        #desplazar lineras verticales y horizontales con el jugador
        offset_x = player.rect.x % tam_celda
        offset_y = player.rect.y % tam_celda

        # Líneas verticales
        for x in range(0, ancho, tam_celda):
            pygame.draw.line(surface, color, (x - offset_x, 0), (x - offset_x, alto))

        # Líneas horizontales
        for y in range(0, alto, tam_celda):
            pygame.draw.line(surface, color, (0, y - offset_y), (ancho, y - offset_y))



    def draw_cursor(self,screen):
        pygame.mouse.set_visible(False)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Dibujar un círculo pequeño como cursor personalizado
        pygame.draw.circle(screen, "Blue", (mouse_x, mouse_y), 20,10)

    def draw_players(self, screen, font, all_players, local_player, offset):
        for pid, pdata in all_players.items():
            if not isinstance(pdata, dict):
                continue

            px = pdata.get("x", 0) - offset[0]
            py = pdata.get("y", 0) - offset[1]

            # Dibujar sprite según estado (si tienes sprite por estado guardado)
            estado = pdata.get("estado", "default")
            anim = self.player_animations.get(estado)
            frame = anim.update() if anim else None
            if frame:
                rect = frame.get_rect(center=(px, py))
                screen.blit(frame, rect)
            if all_players[pid].get("is_dashing", False):
                estado_dash = self.player_animations.get("dash")
                screen.blit(estado_dash.update(), rect)
            # Barra de vida
            vida_max = pdata.get("vida_max", 100)
            vida_actual = pdata.get("vida", 100)
            vida_ratio = max(0, min(1, vida_actual / vida_max))
            barra_ancho, barra_alto = 30, 5
            pygame.draw.rect(screen, (255, 0, 0), (px - barra_ancho//2, py - 25, barra_ancho, barra_alto))
            pygame.draw.rect(screen, (0, 255, 0), (px - barra_ancho//2, py - 25, int(barra_ancho * vida_ratio), barra_alto))

            # Nombre
            nombre = pdata.get("nombre", f"Player {pid}")[:15]
            nombre_texto = font.render(nombre, True, (255, 255, 255))
            rect = nombre_texto.get_rect(center=(px, py - 40))
            screen.blit(nombre_texto, rect)



    def draw_hud(self,screen, font, player, clock, inventario, selected_item, count):
        """
        Dibuja el HUD en pantalla con la información del jugador, reloj y el inventario.

        Parámetros:
            screen: superficie principal donde se dibuja (pygame.display.set_mode).
            font: fuente de texto para los textos del HUD.
            player: objeto o diccionario con la información del jugador (ej: vida, energía).
            clock: objeto pygame.time.Clock para mostrar FPS o tiempo.
            inventario: lista/diccionario con los ítems del jugador.
            selected_item: índice del ítem actualmente seleccionado.
            count: cantidad del ítem seleccionado.
        """

        # Fondo del HUD (parte superior)
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, screen.get_width(), 80))

        # Vida del jugador
        vida_text = font.render(f"Vida: {player.health}", True, (255, 0, 0))
        screen.blit(vida_text, (20, 20))

        # FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        screen.blit(fps_text, (screen.get_width() - 100, 20))

        #Mostrar coordenadas:
        coordenadas_text = font.render(f"Coordenadas: {player.rect.x}, {player.rect.y}", True, (255, 255, 255))
        screen.blit(coordenadas_text, (20, 60))

        # Inventario (barras abajo)
        inv_y = screen.get_height() - 80
        inv_x = 20
        item_size = 50
        for i, item in enumerate(inventario.items):
            rect = pygame.Rect(inv_x + i * (item_size + 10), inv_y, item_size, item_size)
            color = (100, 100, 100)
            if i == selected_item:  # resaltar ítem seleccionado
                color = (200, 200, 0)
            pygame.draw.rect(screen, color, rect, border_radius=5)

            # Nombre del ítem
            item_text = font.render(item.name, True, (255, 255, 255))
            screen.blit(item_text, (rect.x + 5, rect.y + 5))

        # Cantidad del ítem seleccionado
        if 0 <= selected_item < len(inventario.items):
            cant_text = font.render(f"x{count}", True, (255, 255, 255))
            screen.blit(cant_text, (inv_x + selected_item * (item_size + 10), inv_y - 25))



    def handle_events(self,event, player, inventario, balas_group, offset):
        """
        Maneja los eventos de UI e interacción del jugador
        """
        # Cerrar el juego
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            # Abrir inventario
            if event.key == pygame.K_i:
                inventario.toggle()

        # Disparo con click izquierdo
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                bala = player.shoot(event.pos, offset)
                if bala:
                    balas_group.add(bala)