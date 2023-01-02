from copy import *
import pygame
from numba import jit
import numpy as np
import scipy
from scipy import ndimage
import math
from voxUtils import coordsToIso, pointDistance2D, rotatePoint3D
from voxConstants import PREBAKE_NOBAKE, PREBAKE_MULTIPLY, PREBAKE_MINIMUM

## Model Class ##
# This class is used to store and render 3D models. Usually, user code will use the ModelManager class to load models.
class Model:
    
    def __init__(self, filename, numSlices, scale=1):
        image = pygame.image.load(filename).convert_alpha()
        self.slices = []
        height = image.get_height() / numSlices
        self.rendered = None
        self.baseShadow = None

        self.numSlices = numSlices
        for i in range(numSlices):
            slc = pygame.Surface((image.get_width(), height), pygame.SRCALPHA)
            slc.blit(image, (0, -i*height))
            self.slices.append(slc)
        if scale > 1:
            for i in range(numSlices):
                width, height = self.slices[i].get_size()
                width *= scale
                height *= scale
                self.slices[i] = pygame.transform.scale(
                    self.slices[i], (width, height))

        self.rotation = 0
        self.scale = scale
    
    def hasShadow(self):
        return self.baseShadow != None

    def setRotation(self, value):
        self.rotation = value % 360

    def draw(self, surf, x, y, zoom=1, squash=0.5):
        squash = 1-squash
        for i in range(self.numSlices):
            j = self.numSlices - 1 - i
            transformed = self.slices[j]
            transformed = pygame.transform.rotate(
                pygame.transform.scale(
                    transformed, 
                    (int(transformed.get_width()*zoom), int(transformed.get_height()*zoom))
                ), 
            self.rotation )

            transformed = pygame.transform.scale(
                transformed, 
                (int(transformed.get_width()), int(transformed.get_height()*squash))
            )

            for k in range(int(zoom)):
                surf.blit(transformed, (x-transformed.get_width()/2, y - transformed.get_height()/2 - k + zoom*len(self.slices)/2 - i*zoom))

    def drawRotate(self, surf, rotation, zoom, squash):
        temp = self.rotation
        self.setRotation(rotation)
        self.draw(surf, surf.get_width()/2, surf.get_height()/2, zoom, squash)
        self.setRotation(temp)
    
    def bake(self, shading = 0.5, shadowSigma = 0.75, method = PREBAKE_MULTIPLY):
        # The bake method will pre-render shadows
        # This will allow for faster compiling, and wont require additional memory, but will render a model reload if we want to change the shading
        lightMask = np.ones((self.slices[0].get_width(), self.slices[0].get_height(), 3))
        for i in range(self.numSlices):
            # Calculate the shadow mask for the current slice
            shadowMask = np.where(pygame.surfarray.array_alpha(self.slices[i]) > 0, shading, 1)
            # Make it a 3d array that has 0:2 as the RGB values, replicating the shading value
            shadowMask = np.repeat(shadowMask[:, :, np.newaxis], 3, axis=2)
            # Apply the light mask to the current slice
            sliceNumpy = pygame.surfarray.pixels3d(self.slices[i]).astype("float32")
            sliceNumpy *= lightMask
            # Update the slice with the new values
            pygame.surfarray.pixels3d(self.slices[i])[:] = sliceNumpy
            # Apply the shadow mask to the light mask, based on the method
            if method == PREBAKE_MULTIPLY:
                lightMask *= shadowMask
            elif method == PREBAKE_MINIMUM:
                lightMask = np.minimum(lightMask, shadowMask)
            # Apply gaussian blur to the light mask
            lightMask = scipy.ndimage.filters.gaussian_filter(lightMask, shadowSigma, mode = 'constant', cval = 1.0)
        
        # The base shadow is then the light mask. We will convert it to a surface
        self.baseShadow = pygame.Surface((self.slices[0].get_width(), self.slices[0].get_height()), pygame.SRCALPHA)
        # Set the alpha channel to the 255*(1-lightMask) value
        pygame.surfarray.pixels_alpha(self.baseShadow)[:] = 255*(1-lightMask[:,:,0])

    def compile(self, angles=180, zoom=1, squash=0.5, bake = PREBAKE_MULTIPLY, shading=0.5, shadowSigma = 1):
        self.rendered = []
        # Calculate the size of the buffer surface
        # It is determined by the base of the model size times the zoom, then rotated 45 degrees (max)
        # We will simulate the bounding box of the whole model, then calculate the coords of certaing corners. Project them in the isometric space, and calculate the dimensions.
        w = self.slices[0].get_width() * zoom
        h = self.slices[0].get_height() * zoom
        zheight = self.numSlices * zoom
        pleft   = (0, h, 0)
        pright  = (w, 0, 0)
        ptop    = (w, h, 0)
        pbot    = (0, 0, zheight)
        # Rotate the points around the origin on the z axis
        # midPoint = (w/2, h/2, zheight/2)
        # pleft   = rotatePoint3D(pleft, midPoint, (0,0,45))
        # pright  = rotatePoint3D(pright, midPoint, (0,0,45))
        # ptop    = rotatePoint3D(ptop, midPoint, (0,0,45))
        # pbot    = rotatePoint3D(pbot, midPoint, (0,0,45))
        # Project the points in the isometric space
        pleft   = coordsToIso(pleft)
        pright  = coordsToIso(pright)
        ptop    = coordsToIso(ptop)
        pbot    = coordsToIso(pbot)
        # Finally, calculate the dimensions of the bounding box
        bbowDim = (math.ceil(pointDistance2D(pleft, pright)), math.ceil(pointDistance2D(pbot, ptop)))
        print("Bounding box: " + str(bbowDim))
        # If the bake flag is set, we will bake the shadows into the non-rotated model
        if bake:
            self.bake(shading, shadowSigma, bake)
        surf = pygame.Surface(bbowDim, pygame.SRCALPHA)
        surfMin = pygame.Surface(bbowDim, pygame.SRCALPHA)
        angl360 = 360/angles
        for rot in range(angles):
            print("Rendering: " + str(rot) + "/" + str(angles))
            surf.fill((0, 0, 0, 0))
            # draw start
            self.drawRotate(surf, rot*angl360, zoom, squash)
            render = pygame.transform.rotozoom(surf, 0, 0.5)
            self.rendered.append(render)
            surfMin.blit(render, (0, 0))

        Model.shrink(surfMin, self.rendered)
        print("Shrunk size: " + str(self.rendered[0].get_size()))
        return self
        
    def snap(self, rotation):
        assert(self.rendered != None)
        return self.rendered[round(rotation*len(self.rendered)/360) % len(self.rendered)]
    
    def snapRadians(self, rotation):
        degrees = rotation*180/math.pi
        return self.snap(degrees)

    @staticmethod
    def shrink(mask, arr):
        # find center of the mask surface
        # get the alpha channel of the mask surface
        alphaMask = pygame.surfarray.pixels_alpha(mask)
        rows = np.any(alphaMask, axis=1)
        cols = np.any(alphaMask, axis=0)
        topMost, bottomMost = np.where(cols)[0][[0, -1]]
        leftMost, rightMost = np.where(rows)[0][[0, -1]]
        # resize the bounding box of each surface in arr to the the new shrinked size
        for i in range(len(arr)):
            arr[i] = pygame.Surface.subsurface(arr[i], (leftMost, topMost, (rightMost - leftMost), (bottomMost-topMost)))