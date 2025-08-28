import pygame

class Animacion:
    def __init__(self, sprite_sheet, frame_width, frame_height,num_frames,scale_factor=1):
        self.frames = []

        for i in range(num_frames):
            frames = sprite_sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frames = pygame.transform.scale(frames, (frame_width * scale_factor, frame_height * scale_factor))
            self.frames.append(frames)

        self.inicio = 0;
        self.velocidad = 0.15;

    def draw(self, surface, position):
        surface.blit(self.frames[int(self.inicio)], position)

    def update(self):
        self.inicio += self.velocidad
        if self.inicio >= len(self.frames):
            self.inicio = 0
        return self.frames[int(self.inicio)]
    def reset(self):
        self.inicio = 0
    def total_frames(self):
        return len(self.frames)