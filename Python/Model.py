from copy import *
import pygame
from numba import jit
import numpy, numpy as np
import math
from voxUtils import coordsToIso, pointDistance2D
math.pi2 = math.pi*2


def shadow(surf, shading):
    # Get the pixels from the surf
    image = pygame.surfarray.pixels3d(surf).astype("float32")
    # Multiply each pixel by the shading value
    numpy.multiply(image, numpy.float32(shading), out=image)


class Model:
    def __init__(self, filename, numSlices, scale=1):
        image = pygame.image.load(filename).convert_alpha()
        self.slices = []
        height = image.get_height() / numSlices
        self.rendered = None

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

    def setRotation(self, value):
        self.rotation = value % 360

    def draw(self, surf, x, y, zoom=1, squash=0.5, shading=1):
        squash = 1-squash
        for i in range(self.numSlices):
            j = self.numSlices - 1 - i
            transformed = self.slices[j]
            transformed = pygame.transform.rotate(pygame.transform.scale(transformed, (int(
                transformed.get_width()*zoom), int(transformed.get_height()*zoom))), self.rotation)
            transformed = pygame.transform.scale(transformed, (int(
                transformed.get_width()), int(transformed.get_height()*squash)))
            #pygame.transform.smoothscale(transformed,(int(transformed.get_width()),int(transformed.get_height()*squash)))
            #shadow(transformed,1-shading)
            for k in range(int(self.scale*zoom)):
                surf.blit(transformed, (x-transformed.get_width()/2, y -
                          transformed.get_height()/2 - k + zoom*len(self.slices)/2 - i*zoom))


    def _draw(self, surf, x, y, zoom=1, squash=0.5, shading=1):
        squash = 1-squash
        for i in range(self.numSlices):
            j = self.numSlices-1-i
            transformed = pygame.transform.rotozoom(
                self.slices[j], self.rotation, zoom)
            transformed = pygame.transform.scale(transformed, (int(
                transformed.get_width()), int(transformed.get_height()*squash)))
            #shadow(transformed,1-shading)

            tSize = (x-transformed.get_width()/2, y - transformed.get_height() /
                     2 + self.scale*zoom*self.numSlices/2 - i*zoom*self.scale)

            for k in range(int(self.scale*zoom)):
                surf.blit(transformed, (tSize[0], tSize[1]-k))

    def drawRotate(self, surf, rotation, zoom, squash, shading):
        temp = self.rotation
        self.setRotation(rotation)
        self.draw(surf, surf.get_width()/2,
                  surf.get_height()/2, zoom, squash, shading)
        self.setRotation(temp)

    def compile(self, angles=180, zoom=1, squash=0.5, shading=0):
        self.rendered = []
        # Calculate the size of the buffer surface
        # It is determined by the base of the model size times the zoom, then rotated 45 degrees (max)
        # To calculate the diagonal, we use the pythagorean theorem. One issue is that we are in the isometric space, so the projected angle is not rectangular.
        # We will simulate the bounding box of the whole model, then calculate the coords of certaing corners. Project them in the isometric space, and calculate the dimensions.
        w = self.slices[0].get_width()*zoom
        h = self.slices[0].get_height()*zoom
        zheight = self.numSlices*zoom
        # pleft   = coordsToIso((0, 0, 0))
        # print("pleft: " + str(pleft))
        # pright  = coordsToIso((w, h, 0))
        # print("pright: " + str(pright))
        # ptop    = coordsToIso((w, 0, zheight))
        # print("ptop: " + str(ptop))
        # pbot    = coordsToIso((0, h, 0))
        # print("pbot: " + str(pbot))
        pleft = coordsToIso((0, h, 0))
        print("pleft: " + str(pleft))
        pright  = coordsToIso((w, 0, 0))
        print("pright: " + str(pright))
        ptop    = coordsToIso((w, h, 0))
        print("ptop: " + str(ptop))
        pbot    = coordsToIso((0, 0, zheight))
        print("pbot: " + str(pbot))
        bbowDim = (math.ceil(pointDistance2D(pleft, pright)), math.ceil(pointDistance2D(pbot, ptop)))
        print("Bounding box: " + str(bbowDim))
        surf = pygame.Surface(bbowDim, pygame.SRCALPHA)
        surfMin = pygame.Surface(bbowDim, pygame.SRCALPHA)
        angl360 = 360/angles
        zoom2 = 2*zoom
        for rot in range(angles):
            print("Rendering: " + str(rot) + "/" + str(angles))
            surf.fill((255, 0, 0, 255))
            # draw start
            self.drawRotate(surf, rot*angl360, zoom2, squash, shading)
            # draw end

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