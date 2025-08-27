import pygame

class Weapon:
    def __init__(self, player, name, damage, cooldown, max_bullets=20, reload_time=1.5):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.time_since_last_shot = 0
        self.max_bullets = max_bullets
        self.player = player
        self.bullets = player.bullets  # balas actuales

        # recarga
        self.reload_time = reload_time
        self.reloading = False
        self.reload_start_time = 0

    def shoot(self, pos, direction, bullet_group):
        if self.reloading:
            return None  # no dispara mientras recarga
        if self.bullets > 0:
            bullet = Bullet(pos, direction, self.damage)
            bullet_group.add(bullet)
            self.bullets -= 1
            print("Disparo! Balas restantes:", self.bullets)
            return bullet
        return None

    def start_reload(self):
        print("Hola")
        print("Bullet: ", self.player.bullets)
        print("Max Bullet: ", self.max_bullets)
        if not self.reloading and self.player.bullets < self.max_bullets:
            print("Recargando...")
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()  # milisegundos

    def update(self):
        if self.reloading:
            elapsed = (pygame.time.get_ticks() - self.reload_start_time) / 1000
            if elapsed >= self.reload_time:
                self.player.bullets = self.max_bullets
                self.reloading = False

    def draw_recarga(self, screen, font):
        if self.reloading:
            elapsed = (pygame.time.get_ticks() - self.reload_start_time) / 1000
            progress = min(1, elapsed / self.reload_time)

            # Texto
            recargando_text = font.render("Recargando...", True, (255, 255, 255))
            rect = recargando_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 40))
            screen.blit(recargando_text, rect)

            # Barra de progreso
            bar_width, bar_height = 200, 20
            x = screen.get_width()//2 - bar_width//2
            y = screen.get_height()//2 + 70
            pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (x, y, int(bar_width * progress), bar_height))


    def draw(self, balas_group, screen, offset):
        """Dibuja todas las balas con offset de cámara"""
        offset_x, offset_y = offset
        for bala in balas_group:
            pos = (bala.pos.x - offset_x, bala.pos.y - offset_y)
            screen.blit(bala.image, pos)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage, velocidad=400):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))  # amarillo
        self.pos = pygame.Vector2(pos)   # posición global en el mundo
        self.rect = self.image.get_rect(center=self.pos)
        self.velocity = pygame.Vector2(direction) * velocidad
        self.damage = damage

    def update(self, dt):
        """Mueve la bala según su velocidad"""
        self.pos += self.velocity * dt
        self.rect.center = self.pos

    @staticmethod
    def update_balas(balas_group, dt):
        """Actualiza todas las balas sin eliminar ninguna"""
        for bala in balas_group:
            bala.update(dt)
