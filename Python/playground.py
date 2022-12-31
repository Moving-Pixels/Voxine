import pygame
from pygame.locals import *
from Model import *
from Voxine import *
import math
import os
size = w,h = 1200,1200
pygame.init()
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
        numDrones = 100
        for i in range(numDrones):
            angle = math.radians(i/numDrones * 360)
            coords = (w/2 + math.cos(angle)*200, h/2 + math.sin(angle)*200)
            screen.blit(models["box"].snapRadians(angle), coords)
            # blitw, blith = models["box"][round(model.rotation/2) % 180].get_size()
            # pygame.draw.rect(screen, (255, 0, 0), (coords[0], coords[1], blitw, blith), 1)
            
            # model.draw(screen, w/2 + math.cos(angle)*200, h/2 + math.sin(angle)*200, zoom = 3, shading = 1, squash = 0.5) # (pygame.mouse.get_pos()[1]/100)%1

        fps = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
        screen.blit(fps, (0, 0))

        wn.blit(screen, (0, 0))
        ############################
        pygame.display.update()
        clock.tick()

def engineMain():
    engine = Engine(debug = True)
    scene1 = Scene(engine)
    engine.addScene(scene1)
    engine.setCurrentScene(scene1)
    camera1 = Camera(scene1)
    scene1.setPrimaryCamera(camera1)
    modelManager = engine.getModelManager()
    modelManager.addModelAndLoad("box", "../testAssets/box.png", 17, 1)

    def instanceStep(self):
        time = pygame.time.get_ticks()
        x = math.sin(time/1000 + self.rotationDelta) * 100
        y = math.cos(time/1000 + self.rotationDelta) * 100
        z = 100 + math.sin(time/100 + self.rotationDelta) * 20
        self.coords = (x, y, z)
        time2 = time/3
        addX = math.sin(time2/1000 + self.rotationDelta) * x
        addY = math.cos(time2/1000 + self.rotationDelta) * y
        addZ = math.sin(time2/100 + self.rotationDelta) * z
        self.coords = (self.coords[0] + addX,
                       self.coords[1] + addY, self.coords[2] + addZ)
        self.rotation[2] += 0.05
    
    for i in range(100):
        instance = Instance(scene1, modelManager.getModel("box"), [0, 0, 0], [0, 0, 0], step=instanceStep, init = NOOP)
        instance.rotationDelta = 360 * i/100
        # To radians
        instance.rotationDelta = instance.rotationDelta * math.pi / 180

    drawSurface = pygame.Surface(size)
    clock = pygame.time.Clock()
    while 1:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
        
        engine.step()
        engine.draw(drawSurface)
        wn.blit(drawSurface, (0, 0))
        pygame.display.update()
        clock.tick(60)
    

        

if __name__ == "__main__":
    engineMain()
    
