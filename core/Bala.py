import pygame

class Bala(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, velocidad=20):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=start_pos)

        self.pos = pygame.Vector2(start_pos)
        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length() != 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2(0, 0)
        self.velocidad = velocidad

    def update(self, dt=1):
        # Actualizamos posición sin límite
        self.pos += self.direction * self.velocidad * dt
        self.rect.center = self.pos
