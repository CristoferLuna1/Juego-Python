import pygame
import core.Animacion as Animacion
from core.Bala import Bala

class Player:
    def __init__(self, x, y):
        animaciones_rutas = {
            'default': ("./assets/sprites/Pink_Monster.png", 32, 32, 1),
            'up': ("./assets/sprites/monsterup.png", 32, 32, 4),
            'down': ("./assets/sprites/monsterdown.png", 32, 32, 4),
            'left': ("./assets/sprites/monsterizquierda.png", 32, 32, 6),
            'right': ("./assets/sprites/monsterderecha.png", 32, 32, 6),
            'dashderecha': ("./assets/sprites/monsterdash.png", 32, 32, 6),
            #'dashizquierda': ("./assets/sprites/monsterdashizquierda.png", 32, 32, 6),
            'ataque': ("./assets/sprites/lanzarpiedraderecha.png", 32, 32, 4),
            'ataqueizquierda': ("./assets/sprites/lanzarpiedraizquierda.png", 32, 32, 4),
            'piedra': ("./assets/sprites/piedra.png", 16, 16, 1)
        }

        self.animaciones = {
            estado: Animacion.Animacion(
                pygame.image.load(ruta).convert_alpha(), w, h, frames, scale_factor=4
            )
            for estado, (ruta, w, h, frames) in animaciones_rutas.items()
        }

        self.estado = "default"
        self.frame_actual = self.animaciones[self.estado].update()

        self.pos = pygame.Vector2(x, y)
        self.width = 120
        self.height = 120
        self.speed = 300  # velocidad base
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.pos
        self.health = 100
        self.bullets = 20
        self.ataque_frame = 0
        self.ataque_en_progreso = False

        # Velocidades
        self.base_speed = 300
        self.dash_speed = 600
        self.is_dashing = False
        self.direccion = ""

    def update(self, dt, event, item_select):
        keys = pygame.key.get_pressed()
        self.estado = "default"
        current_speed = self.base_speed

        if any(keys):
            if keys[pygame.K_LSHIFT]:
                current_speed = self.dash_speed  # velocidad aumentada
                self.is_dashing = True
            else:
                self.is_dashing = False
                current_speed = self.base_speed
            if keys[pygame.K_w]:
                self.estado = "up"
                self.pos.y -= current_speed * dt
            elif keys[pygame.K_s]:
                self.estado = "down"
                self.pos.y += current_speed * dt
            elif keys[pygame.K_a]:
                self.estado = "left"
                self.direccion = "left"
                self.pos.x -= current_speed * dt
            elif keys[pygame.K_d]:
                self.estado = "right"
                self.direccion = "right"
                self.pos.x += current_speed * dt

        # --- ATAQUE ---
        if not hasattr(self, "ataque_en_progreso"):
            self.ataque_en_progreso = False
        # Inicio del ataque (solo si hay balas)
        if hasattr(event, "type") and hasattr(event, "button"):
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not self.ataque_en_progreso
                and self.bullets > 0
                and item_select and item_select.name == "Pistola"
            ):
                self.estado = "ataque"
                self.ataque_en_progreso = True
                # Reinicia la animación de ataque desde el primer frame
                self.animaciones["ataque"].reset()
                if self.direccion == "left":
                    self.animaciones["ataqueizquierda"].reset()
                    self.ataque_en_progreso = True

        # Reproducción del ataque
        if self.ataque_en_progreso:
            if self.direccion == "left":
                self.estado = "ataqueizquierda"
                anim= self.animaciones[self.estado]
                self.frame_actual = anim.update()
            else:
                self.estado = "ataque"
                anim= self.animaciones[self.estado]
                self.frame_actual = anim.update()

            # Verifica si la animación ya terminó
            if anim.inicio >= anim.total_frames() - 1:
                self.ataque_en_progreso = False
                self.estado = "default"

        # Actualizar rect
        self.rect.center = self.pos
        if not self.ataque_en_progreso:  # solo actualizar normal si no está atacando
            self.frame_actual = self.animaciones[self.estado].update()

    def draw(self, surface, offset):
        draw_pos = (self.rect.topleft[0] - offset[0], self.rect.topleft[1] - offset[1])

        # Si está en dash, dibuja la animación dash como "efecto extra"
        if self.is_dashing and 'dashderecha' in self.animaciones:
            dash_effect = self.animaciones['dashderecha'].update()
            if dash_effect:  # Evita error si la animación terminó
                dash_effect.set_alpha(120)  # semitransparente
                surface.blit(dash_effect, draw_pos)  # detrás del jugador

        # Siempre dibujar el personaje principal
        surface.blit(self.frame_actual, draw_pos)

    def shoot(self, mouse_pos, offset):
        # mouse_pos: posición del cursor en la pantalla
        # offset: desplazamiento del mapa
        start_pos = (self.pos.x, self.pos.y)
        target_pos = (mouse_pos[0] + offset[0], mouse_pos[1] + offset[1])
        bala = Bala(start_pos, target_pos)
        return bala



