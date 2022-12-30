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

# Voxine imports
from Model import *

class Engine:
    def __init__(self, debug = False):
        # Create internal variables
        self.scenes = SceneManager(self)
        self.modelManager = ModelManager(self)
        self.currentScene = None
        self.debug = debug
    
    def addScene(self, scene):
        self.scenes.addScene(scene)
    
    def loadScene(self, scene):
        self.scenes.loadScene(scene)
    
    def getCurrentScene(self):
        if self.currentScene == None:
            raise Exception("No scene loaded")
        return self.scenes.getCurrentScene()
    
    def getModelManager(self):
        return self.modelManager

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

class Scene:
    def __init__(self, engine, sceneName = "Unnamed Scene"):
        self.engine = engine
        self.modelManager = self.engine.getModelManager()
        self.cameraManager = CameraManager(self)
        self.instanceManager = InstanceManager(self)
        self.primaryCamera = None
        self.sceneName = sceneName
    
    def load(self):
        # ...
        pass

    def getCameraManager(self):
        return self.cameraManager
    
    def getPrimaryCamera(self):
        if self.primaryCamera == None:
            raise Exception("No primary camera set for scene " + self.sceneName)
        return self.primaryCamera
    
    def step(self):
        self.instanceManager.step()
    
    def draw(self, surf, camera = None):
        if camera == None:
            camera = self.getPrimaryCamera()
        self.cameraManager.drawAsCamera(surf, camera)

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
        camera.renderList(self.scene.instanceManager.getInstances(), surf)

class Camera:
    def __init__(self, scene, cameraName = "Unnamed Camera"):
        self.scene = scene
        self.cameraName = cameraName
        self.cameraManager = self.scene.getCameraManager()
        self.cameraManager.addCamera(self)
        self.coords = [0, 0, 0]
        self.isoCoords = [0, 0, 0]
        self.rotation = [0, 0, 0]
    
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
        self.isoCoords = self.coordsToIso(self.coords)
    
    def updateCoords(self):
        self.coords = self.isoToCoords(self.isoCoords)
    
    def coordsToIso(self, coords):
        x = coords[0]
        y = coords[1]
        z = coords[2]
        return [x - y, (x + y) / 2 - z]
    
    def isoToCoords(self, isoCoords):
        x = isoCoords[0]
        y = isoCoords[1]
        return [x + y, x - y, -y]
    
    def renderList(self, instances, surf):
        for instance in instances:
            self.renderInstance(instance, surf)
    
    def renderInstance(self, instance, surf):
        blitSurface = instance.snap()
        instanceCoords = instance.getCoords()
        # Apply camera coords
        instanceCoords[0] -= self.coords[0]
        instanceCoords[1] -= self.coords[1]
        instanceCoords[2] -= self.coords[2]
        # Apply camera rotation (not yet implemented)
        # To Iso
        instanceCoords = self.coordsToIso(instanceCoords)
        # Blit
        surf.blit(blitSurface, instanceCoords)

class InstanceManager:
    def __init__(self, scene):
        self.scene = scene
        self.instances = []
    
    def addInstance(self, instance):
        self.instances.append(instance)
    
    def getInstances(self):
        return self.instances
    
    def step(self):
        for instance in self.instances:
            instance.step()

class Instance:
    def __init__(self, scene, model, coords = [0, 0, 0], rotation = [0, 0, 0], step = None):
        self.scene = scene
        self.model = model
        self.coords = coords
        self.rotation = rotation
        self.instanceManager = self.scene.instanceManager
        self.instanceManager.addInstance(self)
        if step != None:
            self.step = step
    
    def step(self):
        if self.instanceManager.scene.engine.debug:
            print("Warning: Instance.step() not overridden")
    
    def getCoords(self):
        return self.coords
    
    def getRotation(self):
        return self.rotation
    
    def getModel(self):
        return self.model
    
    def snap(self):
        return self.model.snap(self.rotation)



    

        