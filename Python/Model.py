from copy import *
import pygame
import numpy
import math
math.pi2 = math.pi*2


def shadow(surf, shading):
    image = pygame.surfarray.pixels3d(surf).astype("float32")
    numpy.multiply(image, numpy.float32(shading), out=image)


class Model:
    def __init__(self, filename, numSlices, scale=1):
        image = pygame.image.load(filename).convert_alpha()
        self.slices = []
        height = image.get_height() / numSlices

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
        res = []
        surf = pygame.Surface((4*100, 4*100), pygame.SRCALPHA)
        surfMin = pygame.Surface((4*100, 4*100), pygame.SRCALPHA)
        surfMin.fill((0, 0, 0, 0))
        for rot in range(angles):
            surf.fill((0, 0, 0, 0))
            # draw start
            self.drawRotate(surf, rot*360/angles, 2*zoom, squash, shading)
            # draw end

            render = pygame.transform.rotozoom(surf, 0, 0.5)

            res.append(render)
            surfMin.blit(render, (0, 0))
            #pygame.image.save(render,"renders\\"+str(rot) + tag + ".png")
        Model.shrink(surfMin, res)
        return res

    @staticmethod
    def shrink(mask, arr):
        # find center of the mask surface
        dimensions = mask.get_size()
        topMost = dimensions[1]
        leftMost = dimensions[0]
        bottomMost = 0
        rightMost = 0
        # iterate through pixels of the mask surface
        for x in range(dimensions[0]):
            for y in range(dimensions[1]):
                if mask.get_at((x, y))[3] != 0:
                    # if pixel is not transparent, update the top and bottom most values
                    if y > bottomMost:
                        bottomMost = y
                    elif y < topMost:
                        topMost = y
                    # update the left and right most values
                    if x > rightMost:
                        rightMost = x
                    elif x < leftMost:
                        leftMost = x

        # resize the bounding box of each surface in arr to the the new shrinked size
        for surface in arr:
            surface = pygame.Surface.subsurface(
                surface, (leftMost, topMost, (rightMost - leftMost), (bottomMost-topMost)))