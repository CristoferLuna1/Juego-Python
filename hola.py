import pygame
import core.Animacion as Animacion

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Prueba Sprite")
clock = pygame.time.Clock()


#Diccionario animaciones:
animaciones_rutas = {
    'default': ("./data/sprites/Pink_Monster.png",32,32, 1),
    'up': ("./data/sprites/monsterup.png",32,32, 4),
    'down': ("./data/sprites/monsterdown.png",32,32, 4),
    'left': ("./data/sprites/monsterizquierda.png",32,32, 6),
    'right': ("./data/sprites/monsterderecha.png",32,32, 6),
    'dash': ("./data/sprites/monsterdush.png",32,32, 6)
}

animaciones = {
    estado: Animacion.Animacion(
        pygame.image.load(ruta).convert_alpha(),
        w, h, frames, scale_factor=4
    )
    for estado, (ruta, w, h, frames) in animaciones_rutas.items()
}

actual = []

velocidad = 5
x,y= 100,100



def animaciondush():
    global frame_inicio,frames


    for i in range (6):
        frame = sprite_up.subsurface((i * 32, 0, 32, 32))
        frame = pygame.transform.scale(frame, (128, 128)) #escala los frames
        frames.append(frame)


    frame_inicio += frame_velocidad
    if frame_inicio >= len(frames):
        frame_inicio = 0
    frame_inicio += frame_velocidad
    if frame_inicio >= len(frames):
        frame_inicio = 0

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False


    screen.fill((0, 0, 0))  # Limpiar pantalla
    keys = pygame.key.get_pressed()
    # Movimiento derecha
    if (any(keys)):
        #print("keys_ ", keys)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += velocidad
            if x > 1280:
                x = 0
            actual = animaciones['right'].update()
            screen.blit(actual, (x, y))
        # Movimiento arriba
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= velocidad
            if y < 0:
                y = 720
            actual = animaciones['up'].update()
            screen.blit(actual, (x, y))
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += velocidad
            if y > 720:
                y = 0
            actual = animaciones['down'].update()
            screen.blit(actual, (x, y))
        #Movimiento izquierda
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= velocidad
            if x < 0:
                x = 1280
            actual = animaciones['left'].update()
            screen.blit(actual, (x, y))

        # Dash con LSHIFT
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_d] or keys[pygame.K_RIGHT]) or keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocidad = 10
            if x > 1280:
                x = 0
            actual = animaciones['dash'].update()
            screen.blit(actual, (x, y))

    else:
        #print("Idle")
        velocidad = 5
        actual = animaciones['default'].update()
        screen.blit(actual, (x, y))

    #dibujar sprite
    pygame.display.flip()
    # Controlar la velocidad de fotogramas
    clock.tick(60)

pygame.quit()