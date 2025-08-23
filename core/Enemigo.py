import pygame

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vida = 100

    def draw(self, surface, offset):
        draw_pos = self.rect.topleft - offset
        pygame.draw.rect(surface, "White", (*draw_pos, self.rect.width, self.rect.height))


    def recibir_dano(self, dano):
        self.vida -= dano
        if self.vida <= 0:
            print("Enemigo derrotado")
            self.rect.x = 800

    def perseguir1(self, jugador):
        if self.rect.x < jugador.pos.x:
            self.rect.x += 5
        if self.rect.y < jugador.pos.y:
            self.rect.y += 5
    def perseguir2(self,jugador):
        if self.rect.x > jugador.pos.x:
            self.rect.x -= 5
        if self.rect.y > jugador.pos.y:
            self.rect.y -= 5
    def update(self, jugador):
        self.perseguir1(jugador)
        self.perseguir2(jugador)