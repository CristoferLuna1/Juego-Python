import pygame

class Bala(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction, velocidad=20):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill("yellow")
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(start_pos)  # Posición real en el mundo
        self.rect.center = self.pos
        self.direction = direction
        self.velocidad = velocidad

    def update(self):
        # Mueve la bala en el mundo
        self.pos += self.direction * self.velocidad
        self.rect.center = self.pos  # Actualiza el rect para colisiones

    def draw(self, surface, offset):
        # Dibuja la bala teniendo en cuenta el desplazamiento de la cámara
        draw_pos = self.rect.topleft - offset
        surface.blit(self.image, draw_pos)
