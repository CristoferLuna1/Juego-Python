import pygame

class PlayerShield(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=40, color=(0, 150, 255)):
        super().__init__()
        self.radius = radius
        self.color = color
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius, 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.active = True

    def update_position(self, player_pos):
        """Mantener el escudo centrado en la posición del jugador"""
        self.rect.center = player_pos

    def draw(self, screen, offset=(0, 0)):
        """Dibuja el escudo en pantalla con un offset aplicado"""
        if self.active:
            screen.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))
