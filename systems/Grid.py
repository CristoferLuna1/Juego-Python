import pygame

class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = [[None for _ in range(width)] for _ in range(height)]

    def world_to_grid(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)

    def grid_to_world(self, gx, gy):
        return gx * self.cell_size, gy * self.cell_size

    def place_object(self, obj, x, y):
        gx, gy = self.world_to_grid(x, y)
        self.cells[gy][gx] = obj

    def remove_object(self, x, y):
        gx, gy = self.world_to_grid(x, y)
        self.cells[gy][gx] = None

    def get_object(self, x, y):
        gx, gy = self.world_to_grid(x, y)
        return self.cells[gy][gx]

    def draw(self, screen, offset=(0, 0)):
        """Dibuja la grilla en la pantalla"""
        color = (40, 40, 40)  # gris oscuro
        for row in range(self.rows):
            pygame.draw.line(
                screen,
                color,
                (offset[0], offset[1] + row * self.cell_size),
                (offset[0] + self.cols * self.cell_size, offset[1] + row * self.cell_size),
            )
        for col in range(self.cols):
            pygame.draw.line(
                screen,
                color,
                (offset[0] + col * self.cell_size, offset[1]),
                (offset[0] + col * self.cell_size, offset[1] + self.rows * self.cell_size),
            )

    def update(self, player, screen):
        """Actualiza la posición de la cámara en cada frame"""
        return self.get_camera_offset(player, screen)

    @staticmethod
    def get_camera_offset(player, screen):
        """
        Calcula el offset para que la cámara siga al jugador.
        """
        screen_w, screen_h = screen.get_size()
        offset_x = player.pos.x - screen_w // 2
        offset_y = player.pos.y - screen_h // 2
        return offset_x, offset_y
