from copy import *
import pygame
from numba import jit
import numpy, numpy as np
import scipy
from scipy import ndimage
import math
from voxUtils import coordsToIso, pointDistance2D, rotatePoint3D
math.pi2 = math.pi*2


def shadow(surf, shading):
    # Get the pixels from the surf
    image = pygame.surfarray.pixels3d(surf).astype("float32")
    # Multiply each row by the shading, so that the bottom row are * shading and the top row are * 1
    for slice in range(surf.get_height()):
        image[slice, :, :] *= (1 - shading * slice / surf.get_height())
    return surf





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

    def draw(self, surf, x, y, zoom=1, squash=0.5, shading=0.5):
        squash = 1-squash
        rotatedBase = pygame.transform.rotate(pygame.transform.scale(self.slices[0], (int(self.slices[0].get_width()*zoom), int(self.slices[0].get_height()*zoom))), self.rotation)
        rotatedBase = pygame.transform.scale(rotatedBase, (int(rotatedBase.get_width()), int(rotatedBase.get_height()*squash)))
        rotatedShadowSurface = np.ones_like(pygame.surfarray.pixels3d(rotatedBase)).astype("float32")
        blitList = []
        shadowList = []
        # In order to shade the model, we need to draw the slices from the top down, so that the bottom slices are shaded by the top slices
        # This poses a problem, since bottom slices will be drawn over top slices.
        # To solve this, we will use a different blending mode to draw the slices, so that when drawing a slice, it will only draw the pixels that are not already drawn (alpha = 0)
        for i in range(self.numSlices):
            transformed = self.slices[i]
            transformed = pygame.transform.rotate(pygame.transform.scale(transformed, (int(transformed.get_width()*zoom), int(transformed.get_height()*zoom))), self.rotation)
            transformed = pygame.transform.scale(transformed, (int(transformed.get_width()), int(transformed.get_height()*squash)))
            # Calculate a new shadow surface for the next layer as a matrix of 1s and shading-s, where shading is where the pixel is visible
            # and 1 is where the pixel is not visible
            newShadowSurface = np.where(pygame.surfarray.array_alpha(transformed) > 0, shading, 1)
            # Make it a 3d array that has 0:2 as the RGB values, replicating the shading value
            newShadowSurface = np.repeat(newShadowSurface[:, :, np.newaxis], 3, axis=2)
            # Apply rotated shadow by multiplying the current slice pointwise with the shadow surface
            transformedNumpy = pygame.surfarray.pixels3d(transformed).astype("float32")
            transformedNumpy *= rotatedShadowSurface
            # Update the transformed surface with the new values
            pygame.surfarray.pixels3d(transformed)[:] = transformedNumpy
            # Apply the new shadow surface to the old shadow surface
            rotatedShadowSurface *= newShadowSurface
            # Apply gaussian blur to the shadow surface
            rotatedShadowSurface = scipy.ndimage.filters.gaussian_filter(rotatedShadowSurface, 0.75, mode = 'constant', cval = 1.0)
            # Add the transformed surface to the blit list
            blitList.append(transformed)
        
        # Draw the slices from the bottom up
        for i in range(self.numSlices):
            transformed = blitList[self.numSlices-1-i]
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
        surf = pygame.Surface(bbowDim, pygame.SRCALPHA)
        surfMin = pygame.Surface(bbowDim, pygame.SRCALPHA)
        angl360 = 360/angles
        for rot in range(angles):
            print("Rendering: " + str(rot) + "/" + str(angles))
            surf.fill((0, 0, 0, 0))
            # draw start
            self.drawRotate(surf, rot*angl360, zoom, squash, shading)
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