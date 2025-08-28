import pygame

class Inventario:
    def __init__(self):
        self.items = []
        self.item_text_cache = {}
        self.needs_redraw = True
        self.inventory_surface = None
        self.visible = False

        # Crear fuentes una vez
        self.font_number = pygame.font.Font(None, 16)
        self.font_item = pygame.font.Font(None, 20)

    def toggle(self):
        """Muestra u oculta el inventario"""
        self.visible = not self.visible

    def add_item(self, item):
        self.items.append(item)
        self.item_text_cache[str(item)] = self.font_item.render(str(item), True, (0, 0, 0))
        self.needs_redraw = True

    def remove_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                self.needs_redraw = True
                return True
        return False

    def get_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                return item
        return None

    def render_inventory_surface(self, item_size):
        width = item_size[0] * 8 + 70
        height = item_size[1] * 1 + 10
        self.inventory_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Fondo del inventario
        inventory_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(self.inventory_surface, (50, 50, 50), inventory_rect)
        pygame.draw.rect(self.inventory_surface, (100, 100, 100), inventory_rect, 3)

        items_to_show = self.items[:8]
        for i, item in enumerate(items_to_show):
            col = i
            item_rect = pygame.Rect(5 + col * (item_size[0] + 5), 5, item_size[0], item_size[1])
            pygame.draw.rect(self.inventory_surface, (255, 255, 255), item_rect)

            # Número del ítem
            number_text = self.font_number.render(str(i + 1), True, (0, 0, 0))
            number_rect = number_text.get_rect(centerx=item_rect.centerx, top=item_rect.top + 2)
            self.inventory_surface.blit(number_text, number_rect)

            # Nombre del ítem
            item_text = self.item_text_cache.get(str(item))
            if item_text:
                text_rect = item_text.get_rect(center=item_rect.center)
                self.inventory_surface.blit(item_text, text_rect)

        self.needs_redraw = False

    def display_inventory(self, screen, x, y, item_size):
        """Dibuja el inventario solo si está visible"""
        if not self.visible:
            return
        if self.needs_redraw or self.inventory_surface is None:
            self.render_inventory_surface(item_size)

        screen.blit(self.inventory_surface, (x, y))
