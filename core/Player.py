import pygame
import core.Animacion as Animacion

class Player:
    def __init__(self, x, y):
        animaciones_rutas = {
            'default': ("./data/sprites/Pink_Monster.png", 32, 32, 1),
            'up': ("./data/sprites/monsterup.png", 32, 32, 4),
            'down': ("./data/sprites/monsterdown.png", 32, 32, 4),
            'left': ("./data/sprites/monsterizquierda.png", 32, 32, 6),
            'right': ("./data/sprites/monsterderecha.png", 32, 32, 6),
            'dash': ("./data/sprites/monsterdash.png", 32, 32, 6)
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

        # Velocidades
        self.base_speed = 300
        self.dash_speed = 600
        self.is_dashing = False

    def update(self, dt):
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
                self.pos.x -= current_speed * dt
            elif keys[pygame.K_d]:
                self.estado = "right"
                self.pos.x += current_speed * dt


        # Actualizar rect y frame
        self.rect.center = self.pos
        self.frame_actual = self.animaciones[self.estado].update()

def draw(self, surface, offset):
    draw_pos = self.rect.topleft - offset

    # Si está en dash, dibuja la animación dash como "efecto extra"
    if self.is_dashing:
        dash_effect = self.animaciones['dash'].update()
        dash_effect.set_alpha(120)  # semitransparente
        surface.blit(dash_effect, draw_pos)  # atrás

    # Siempre dibujar el personaje principal (movimiento normal)
    surface.blit(self.frame_actual, draw_pos)


