import pygame

class PlayerShield(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=80, color=(0, 150, 255)):
        super().__init__()
        self.radius = radius
        self.color = color
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius, 3)
        self.rect = self.image.get_rect(center=(x, y))

        # Estados
        self.active = False
        self.cooling_down = False

        # Tiempos
        self.activation_time = 0
        self.shield_duration = 5     # duración del escudo en segundos
        self.cooldown_time = 5       # tiempo de recarga en segundos
        self.cooldown_start_time = 0

    def update(self, player_pos):
        """Mantener el escudo siempre centrado al jugador y manejar timers"""
        # SIEMPRE sigue al jugador
        self.rect.center = player_pos

        if self.active:
            elapsed = (pygame.time.get_ticks() - self.activation_time) / 1000
            if elapsed >= self.shield_duration:
                self.active = False
                self.cooling_down = True
                self.cooldown_start_time = pygame.time.get_ticks()

        elif self.cooling_down:
            elapsed = (pygame.time.get_ticks() - self.cooldown_start_time) / 1000
            if elapsed >= self.cooldown_time:
                self.cooling_down = False  # listo para usarse de nuevo

    def draw(self, font, screen):
        """Dibuja el escudo y la barra de recarga en pantalla"""
        #if self.active:
            # Dibujar el escudo en sí
            #screen.blit(self.image, self.rect)

        if self.cooling_down:
            # Mostrar mensaje y barra de recarga
            elapsed = (pygame.time.get_ticks() - self.cooldown_start_time) / 1000
            progress = min(1, elapsed / self.cooldown_time)

            recar_shield_text = font.render("Recargando escudo", True, (255, 255, 255))
            rect = recar_shield_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 40))
            screen.blit(recar_shield_text, rect)

            # Barra
            bar_width, bar_height = 200, 20
            x = screen.get_width()//2 - bar_width//2
            y = screen.get_height()//2 + 70
            pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
            pygame.draw.rect(screen, (0, 150, 255), (x, y, bar_width * progress, bar_height))

    def activate_shield(self):
        """Activa el escudo si no está en recarga"""
        if not self.active and not self.cooling_down:
            self.active = True
            self.activation_time = pygame.time.get_ticks()
