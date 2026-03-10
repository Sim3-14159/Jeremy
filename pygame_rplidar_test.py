import pygame
from modules.gui import GUI


while True:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    gui = GUI(screen)

    pygame.mouse.set_visible(False)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_h:
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())

        gui.update()
        gui.draw()

    pygame.quit()