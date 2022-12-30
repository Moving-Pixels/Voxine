import pygame
from pygame.locals import *
from Model import *
import math
import os
size = w,h = 800,600

wn = pygame.display.set_mode(size, DOUBLEBUF)
pygame.display.set_caption("Test")
screen = pygame.Surface(size)
pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

models = {}
def main():
    # print current working directory
    
    global models
    clock = pygame.time.Clock()
    boxModel = Model("../testAssets/box.png",17,1)
    model = boxModel
    models["box"] = model.compile(zoom=3)

    while 1:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
        ############################

        screen.fill((25, 25, 25))
        #model.setRotation(pygame.mouse.get_pos()[0])
        mx, my = pygame.mouse.get_pos()
        model.setRotation(model.rotation + 0.1 /
                          (math.sqrt((mx-w/2)**2 + (my-h/2)**2)/500))
        numDrones = 1000
        for i in range(numDrones):
            angle = math.radians(i/numDrones * 360)
            coords = (w/2 + math.cos(angle)*200, h/2 + math.sin(angle)*200)
            screen.blit(models["box"][round(model.rotation/2) % 180], coords)
            # blitw, blith = models["box"][round(model.rotation/2) % 180].get_size()
            # pygame.draw.rect(screen, (255, 0, 0), (coords[0], coords[1], blitw, blith), 1)
            
            #model.draw(screen, w/2 + math.cos(angle)*200, h/2 + math.sin(angle)*200, zoom = 3, shading = 1, squash = 0.5) # (pygame.mouse.get_pos()[1]/100)%1

        fps = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
        screen.blit(fps, (0, 0))

        wn.blit(screen, (0, 0))
        ############################
        pygame.display.update()
        clock.tick()

if __name__ == "__main__":
    main()
