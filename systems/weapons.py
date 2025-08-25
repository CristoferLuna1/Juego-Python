import pygame

class Weapon:
    def __init__(self, name, damage, cooldown):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.time_since_last_shot = 0

    def update(self, dt):
        self.time_since_last_shot += dt

    def can_shoot(self):
        return self.time_since_last_shot >= self.cooldown

    def shoot(self, pos, direction, bullet_group):
        if self.can_shoot():
            bullet = Bullet(pos, direction, self.damage)
            bullet_group.add(bullet)
            self.time_since_last_shot = 0

    def draw(self, balas_group, screen, offset):
        """
        Dibuja las balas en pantalla con un offset de cámara.

            :param balas_group: pygame.sprite.Group con las balas activas
            :param screen: superficie de pygame donde se dibujan
            :param offset: tupla (offset_x, offset_y) para simular cámara
            """
        offset_x, offset_y = offset

        for bala in balas_group:
            # Ajustar posición con respecto a la cámara
            pos = (bala.rect.x - offset_x, bala.rect.y - offset_y)
            screen.blit(bala.image, pos)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill("yellow")
        self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.Vector2(direction) * 400
        self.damage = damage

    def update(self, dt):
        self.rect.center += self.velocity * dt

    def update_balas(balas_group):
        """Actualiza la posición de todas las balas y las elimina si salen de la pantalla."""
        for bala in balas_group:
            bala.update()  # si tu clase Bala ya tiene un método update()

            # ejemplo: eliminar si sale de la pantalla
            if bala.rect.x > 800 or bala.rect.x < 0 or bala.rect.y > 600 or bala.rect.y < 0:
                balas_group.remove(bala)