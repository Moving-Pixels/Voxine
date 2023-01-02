import pygame
from pygame.locals import *
from Model import *
from Voxine import *
from voxUtils import NOOP
import math
import os
import time
from PIL import Image, ImageDraw
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
    boxModel = Model("../testAssets/Marshall.png",41,1)
    model = boxModel
    models["box"] = model.compile(zoom=1)

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
    print("Loading models...")
    time1 = time.time()
    print("Model 1 of 1: box")
    #modelManager.addModelAndLoad("Marshall",    "testAssets/Marshall.png",      41,     scale = 1, zoom = 2, angles = 360)
    #modelManager.addModelAndLoad("box",         "testAssets/box.png",           17,     scale = 1, zoom = 4, angles = 360)
    #modelManager.addModelAndLoad("ufo",         "testAssets/ufo.png",           17,     scale = 1, zoom = 4, angles = 360)
    #modelManager.addModelAndLoad("mushroom",    "testAssets/mushroom.png",      7,      scale = 1, zoom = 4, angles = 360)
    modelManager.addModelAndLoad("monument1",    "testAssets/monument.png",      126,    scale = 1, zoom = 2, angles = 30, shading = 0)
    modelManager.addModelAndLoad("monument2",    "testAssets/monument.png",      126,    scale = 1, zoom = 2, angles = 30, shading = 0.25)
    modelManager.addModelAndLoad("monument3",    "testAssets/monument.png",      126,    scale = 1, zoom = 2, angles = 30, shading = 0.5)
    modelManager.addModelAndLoad("monument4",    "testAssets/monument.png",      126,    scale = 1, zoom = 2, angles = 30, shading = 0.75)
    modelManager.addModelAndLoad("monument5",    "testAssets/monument.png",      126,    scale = 1, zoom = 2, angles = 30, shading = 1)
    print("Done loading models in " + str(time.time() - time1) + " seconds")



    def instanceStep(self):
        time = pygame.time.get_ticks()
        self.rotation[2] += 1
        z=100
        return
        x =       math.sin( time/1000 + self.rotationDelta ) * 200
        y =       math.cos( time/1000 + self.rotationDelta ) * 200
        z = 100 # 100 + math.sin( time/100  + self.rotationDelta ) * 20
        self.coords = (x, y, z)
        time2 = time/3
        addX = math.sin( time2/1000 + self.rotationDelta ) * 200
        addY = math.cos( time2/1000 + self.rotationDelta ) * 200
        addZ = 0 # math.sin( time2/100  + self.rotationDelta ) * 20 
        self.coords = (self.coords[0] + addX,
                       self.coords[1] + addY, self.coords[2] + addZ)
        self.rotation[2] += (300 - (abs(x) + abs(y)))/150
    
    def rotateStep(self):
        self.rotation = (self.rotation[0], self.rotation[1], self.rotation[2] + 1)
    # for i in range(1):
    #     instance = Instance(scene1, modelManager.getModel("box"), [0, 0, 0], [0, 0, 0], step=instanceStep, init = NOOP)
    #     instance.rotationDelta = 360 * i/25
    #     # To radians
    #     instance.rotation[2] = instance.rotationDelta
    #     instance.rotationDelta = instance.rotationDelta * math.pi / 180
    #rob = Instance(scene1, modelManager.getModel("Marshall"),(-400,-400,0),(0,0,0),step=rotateStep,init=NOOP)
    #box = Instance(scene1, modelManager.getModel("box"),(-200,-200,0),(0,0,0),step=rotateStep,init=NOOP)
    #ufo = Instance(scene1, modelManager.getModel("ufo"),(400,400,0),(0,0,0),step=rotateStep,init=NOOP)
    #mushroom = Instance(scene1, modelManager.getModel("mushroom"),(200,200,0),(0,0,0),step=rotateStep,init=NOOP)
    monument1 = Instance(scene1, modelManager.getModel("monument1"),(-400, 0,100),(0,0,0),step=rotateStep,init=NOOP)
    monument2 = Instance(scene1, modelManager.getModel("monument2"),(-300,-100,100),(0,0,0),step=rotateStep,init=NOOP)
    monument3 = Instance(scene1, modelManager.getModel("monument3"),(-200,-200,100),(0,0,0),step=rotateStep,init=NOOP)
    monument4 = Instance(scene1, modelManager.getModel("monument4"),(-100,-300,100),(0,0,0),step=rotateStep,init=NOOP)
    monument5 = Instance(scene1, modelManager.getModel("monument5"),(0,-400,100),(0,0,0),step=rotateStep,init=NOOP)


        

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
    
