################
# The Voxine Project
# Python 3.10.4 (hopefully has some backwards compatibility)
# This is a 3D Slice Renderer
################

# Standard imports
import pygame
import numpy
import math
import os
from copy import copy

# Voxine imports
from voxUtils import coordsToIso, isoToCoords
from voxConstants import PREBAKE_NOBAKE, PREBAKE_MULTIPLY, PREBAKE_MINIMUM
from Model import Model

class Engine:
    def __init__(self, debug = False):
        # Create internal variables
        self.sceneManager = SceneManager(self)
        self.modelManager = ModelManager(self)
        self.currentScene = None
        self.debug = debug
    
    def addScene(self, scene):
        self.sceneManager.addScene(scene)
    
    def loadScene(self, scene):
        self.sceneManager.loadScene(scene)
    
    def getCurrentScene(self):
        if self.currentScene == None:
            raise Exception("No scene loaded")
        return self.sceneManager.getCurrentScene()
    
    def setCurrentScene(self, scene):
        self.currentScene = scene
        self.sceneManager.setCurrentScene(scene)
    
    def getModelManager(self):
        return self.modelManager
    
    def step(self):
        self.getCurrentScene().step()
    
    def draw(self, surf):
        surf.fill((25,25,25))
        camera = self.getCurrentScene().getPrimaryCamera()
        instances = self.getCurrentScene().getInstanceManager().getInstanceList()
        camera.renderShadows(instances, surf)
        camera.renderList(instances, surf)
    
class SceneManager:
    def __init__(self, engine):
        self.engine = engine
        self.scenes = []
        self.currentScene = None
    
    def addScene(self, scene):
        self.scenes.append(scene)
    
    def loadScene(self, scene):
        if scene in self.scenes:
            self.currentScene = scene
            # ...
            self.currentScene.load()
        else:
            raise Exception("Scene not found")
    
    def getCurrentScene(self):
        if self.currentScene == None:
            raise Exception("No scene loaded")
        return self.currentScene
    
    def setCurrentScene(self, scene):
        if scene in self.scenes:
            self.currentScene = scene
        else:
            raise Exception("Scene not found")

class Scene:
    def __init__(self, engine, sceneName = "Unnamed Scene"):
        self.engine = engine
        self.modelManager = self.engine.getModelManager()
        self.cameraManager = CameraManager(self)
        self.instanceManager = InstanceManager(self)
        self.sceneName = sceneName
    
    def load(self):
        # ...
        pass

    def getCameraManager(self):
        return self.cameraManager
    
    def getPrimaryCamera(self):
        if self.cameraManager.getPrimaryCamera() == None:
            raise Exception("No primary camera set for scene " + self.sceneName)
        return self.cameraManager.getPrimaryCamera()
    
    def step(self):
        self.instanceManager.step()
    
    def draw(self, surf, camera = None):
        if camera == None:
            camera = self.getPrimaryCamera()
        self.cameraManager.drawAsCamera(surf, camera)
    
    def setPrimaryCamera(self, camera):
        self.getCameraManager().setPrimaryCamera(camera)
    
    def getInstanceManager(self):
        return self.instanceManager

class CameraManager:
    def __init__(self, scene):
        self.scene = scene
        self.cameras = []
        self.primaryCamera = None
    
    def addCamera(self, camera):
        self.cameras.append(camera)
    
    def setPrimaryCamera(self, camera):
        if camera in self.cameras:
            self.primaryCamera = camera
        else:
            raise Exception("Camera not found for scene " + self.scene.sceneName)
    
    def getPrimaryCamera(self):
        if self.primaryCamera == None:
            raise Exception("No primary camera set for scene " + self.scene.sceneName)
        return self.primaryCamera
    
    def drawAsCamera(self, surf, camera):
        assert(camera in self.cameras)
        camera.renderList(self.scene.instanceManager.getInstanceList(), surf)

class Camera:
    def __init__(self, scene, cameraName = "Unnamed Camera"):
        self.scene = scene
        self.cameraName = cameraName
        self.cameraManager = self.scene.getCameraManager()
        self.cameraManager.addCamera(self)
        self.coords = (0, 0, 0)
        self.isoCoords = (0, 0, 0)
        self.rotation = (0, 0, 0)
    
    def setCoords(self, coords, updateIso = True):
        self.coords = coords
        if updateIso:
            self.updateIsoCoords()

    def setIsoCoords(self, isoCoords, updateCoords = True):
        self.isoCoords = isoCoords
        if updateCoords:
            self.updateCoords()
    
    def setRotation(self, rotation):
        self.rotation = rotation
    
    def updateIsoCoords(self):
        self.isoCoords = coordsToIso(self.coords)
    
    def updateCoords(self):
        self.coords = isoToCoords(self.isoCoords)
    
    def renderShadows(self, instances, surf):
        for instance in instances:
            self.renderShadow(instance, surf)
    
    def renderShadow(self, instance, surf):
        # Check if the instance's model has a rendered shadow
        if instance.getModel().hasShadow():
            return
            # Blit the shadow
            shadow = instance.getModel().baseShadow
            shadow = pygame.transform.rotate(shadow, self.rotation[2])
            shadow = pygame.transform.scale(shadow, instance.snap().get_size())
            coord = copy(instance.getCoords())
            # Zero out the z coord
            coord = (coord[0], coord[1], 0)
            coord = coordsToIso(coord)
            instSize = instance.snap().get_size()
            coord = ( coord[0] + surf.get_width() / 2, coord[1] + surf.get_height() / 2 )
            surf.blit(shadow, (coord[0], coord[1]))
        else:
            coord = copy(instance.getCoords())
            # Zero out the z coord
            coord = (coord[0], coord[1], 0)
            coord = coordsToIso(coord)
            instSize = instance.snap().get_size()
            coord = ( coord[0] + surf.get_width() / 2, coord[1] + surf.get_height() / 2 )
            pygame.draw.ellipse(surf, (0, 0, 0), (coord[0], coord[1], instSize[0], instSize[1]))

    
    def renderList(self, instances, surf):
        # Order instances by render y
        instances = sorted(instances, key=lambda instance: coordsToIso(instance.getCoords())[1]) #TODO: Optimize
        for instance in instances:
            self.renderInstance(instance, surf)
    
    def renderInstance(self, instance, surf):
        blitSurface = instance.snap()
        instanceCoords = instance.getCoords()
        # Apply camera coords
        instanceCoords = (instanceCoords[0] - self.coords[0], instanceCoords[1] - self.coords[1], instanceCoords[2] - self.coords[2])
        # Apply camera rotation (not yet implemented)
        # To Iso
        instanceCoords = coordsToIso(instanceCoords)
        # Add half of the screen size
        instanceCoords = (instanceCoords[0] + surf.get_width() / 2, instanceCoords[1] + surf.get_height() / 2)
        # Blit
        surf.blit(blitSurface, instanceCoords)

class InstanceManager:
    def __init__(self, scene):
        self.scene = scene
        self.instances = []
    
    def addInstance(self, instance):
        self.instances.append(instance)
    
    def getInstanceList(self):
        return self.instances
    
    def step(self):
        for instance in self.instances:
            instance.step(instance)

class Instance:
    def __init__(self, scene, model, coords=(0, 0, 0), rotation=(0, 0, 0), init = None, step = None):
        self.scene = scene
        self.model = model
        self.coords = coords
        self.rotation = rotation
        self.instanceManager = self.scene.instanceManager
        self.instanceManager.addInstance(self)
        if step != None:
            self.step = step
        if init != None:
            self.init = init
        self.init()
        
    def init(self, *args):
        if self.instanceManager.scene.engine.debug:
            print("Warning: Instance.init() not overridden")
    def step(self, *args):
        if self.instanceManager.scene.engine.debug:
            print("Warning: Instance.step() not overridden")
    
    def getCoords(self):
        return self.coords
    
    def getRotation(self):
        return self.rotation
    
    def getModel(self):
        return self.model
    
    def snap(self):
        return self.model.snap(self.rotation[2])

class ModelManager:
    def __init__(self, engine):
        self.engine = engine
        self.models = {}
    
    def getModel(self, modelName):
        if modelName in self.models:
            return self.models[modelName]
        else:
            raise Exception("Model not found")
    
    def removeModel(self, modelName):
        if modelName in self.models:
            del self.models[modelName]
        else:
            raise Exception("Model not found")
    
    def addModelAndLoad(self, name, filename, numSlices, scale = 1, zoom = 4, angles = 180, shading = 0.5, shadowSigma = 1, shadeMode = PREBAKE_MULTIPLY):
        model = Model(filename, numSlices, scale)
        model.compile(angles = angles, zoom = zoom, bake = shadeMode, shading = shading, shadowSigma = shadowSigma)
        self.models[name] = model
    
    def addModel(self, name, model):
        if self.engine.debug and name in self.models:
            print("Warning: Model " + name + " already exists. Overwriting.")
        self.models[name] = model
    
    def loadModel(self, name, filename, numSlices, scale = 1):
        model = Model(self.engine, filename, numSlices, scale)
        model.compile()
        self.addModel(name, model)


    

        