'''
By James Verley
1/09/2019

my own attempt at a 3d renderer thing from scratch. inspired by retro 3d dungeon games
uses pygame.draw.rect to draw each pixel
sorry for the poor commentation and convention following
'''

import pygame, sys, math, random, os
from pygame.locals import *

pygame.init()
FPS = 20
size = width, height = 800, 600
pixelSize = 4
resX, resY = width // pixelSize, height // pixelSize
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Jimmy 3D")
fpsClock = pygame.time.Clock()
mousePos = [0,0]

keys = []
wallTexture = pygame.image.load(os.path.join('wall_tex.png'))
ceilingTexture = pygame.image.load(os.path.join('ceil_texture.jpg'))
floorTexture = pygame.image.load(os.path.join('floor_texture.jpg'))

# subtract 1 from image dimensions so that the pixel index modulo always returns a float less than or equal to actual dimension
wallTextureWidth = wallTexture.get_width()-1 ; wallTextureHeight = wallTexture.get_height()-1
ceilingTextureWidth = ceilingTexture.get_width()-1 ; ceilingTextureHeight = ceilingTexture.get_height()-1
floorTextureWidth = floorTexture.get_width()-1 ; floorTextureHeight = floorTexture.get_height()-1

#testScene = [[(-5, 1), (-1, 5)], [(-1, 5), (0, 4)], [(0, 4), (1, 5)], [(1, 5), (5,-1)]]
#testScene = [[(5,5), (6,5)], [(6,5), (6,6)], [(6,6), (5,6)], [(5,6), (5,5)], [(3,3), (4,3)], [(4,3), (4,4)], [(4,4), (3,4)], [(3,4), (3,3)], [(1,3), (2,3)], [(2,3), (2,4)], [(2,4), (1,4)], [(1,4), (1,3)]]
testScene = [[(-3.5,5), (-3,6)], [(-3,6), (1,4.5)], [(1,4.5), (2,2)], [(2,2), (3,4.5)], [(3,4.5), (3.5,1)], [(3.5,1), (3,0)], [(3,0), (1.5,-1)], [(1.5,-1), (-2,-1)], [(-2,-1), (-2.5,-0.5)], [(-2.5,-0.5), (-5,-3)], [(-5,-3), (-6,-2.5)], [(-6,-2.5), (-3,1)], [(-3,1), (-3,2)], [(-3,2), (-1,2)], [(-1,2), (-1,4)], [(-1,4), (-3.5,5)], ]
#testScene = [[(random.randint(-100,100)/25, random.randint(-100,100)/25), ((random.randint(-100,100)/25, random.randint(-100,100)/25))] for i in range(10)]

def transformedVector(vector, translation, angle):
    vector = vector[0] - translation[0], vector[1] - translation[1]
    unitX = math.cos(angle)
    unitY = math.sin(angle)
    return [vector[0] * unitX + vector[1] * unitY, -vector[0] * unitY + vector[1] * unitX]

def TransformScene(scene, translation, rotation):
    newScene = []
    for line in scene:
        newScene.append([
            transformedVector(line[0], translation, rotation),
            transformedVector(line[1], translation, rotation)
        ])
    return newScene

def DrawTexRayGroundAndGeometry(x, intercept, line, dist, viewDist, sceneTranslation, sceneRotation, rTheta):
    lineIntOrgDist = math.sqrt((intercept[0]-line[0][0])**2 + (intercept[1] - line[0][1])**2)
    u = lineIntOrgDist / math.sqrt((line[1][0]-line[0][0])**2 + (line[1][1]-line[0][1])**2)

    apparentSize = 1 / dist * viewDist
    apparentHeight = apparentSize * resY

    if apparentSize > 1:
        apparentSize = 1
    heightRange = int(apparentSize * resY // 2)
    shade = apparentSize

    for h in range(-resY // 2, resY // 2):
        if h in range(-heightRange, heightRange):
            v = h / apparentHeight + 0.5

            pix = wallTexture.get_at([int(u*wallTextureWidth),int(v*wallTextureHeight)])#tex = color*((u*9%2>1)^(v*9%2>1))
            #pix = ceilingTexture.get_at([int(u*ceilingTexture.get_width()),int(v*ceilingTexture.get_height())])#tex = color*((u*9%2>1)^(v*9%2>1))
            color = (shade*pix[0], shade*pix[1], shade*pix[2])

            pygame.draw.rect(screen, color, ((x + resX//2) * pixelSize, (resY//2+h) * pixelSize,pixelSize,pixelSize))
        else:
            groundIntDist = viewDist/5*(resY//2)/abs(h)*math.sqrt((x/resX)**2+1) # cameraHeight * (1/2 * resY) / hPix
            groundIntVec = transformedVector([0, groundIntDist], [0,0], -sceneRotation - rTheta)
            groundIntPos = [groundIntVec[0]-sceneTranslation[1]/5, groundIntVec[1]+sceneTranslation[0]/5]

            if h > 0:
                pix = ceilingTexture.get_at([int(groundIntPos[0]*300 % ceilingTextureWidth),int(groundIntPos[1]*300 % ceilingTextureHeight)])#tex = color*((u*9%2>1)^(v*9%2>1))
            else:
                pix = floorTexture.get_at([int(groundIntPos[0]*300 % floorTextureWidth),int(groundIntPos[1]*300 % floorTextureHeight)])#tex = color*((u*9%2>1)^(v*9%2>1))
                #pix = wallTexture.get_at([int(groundIntPos[0]*300 % ceilingTexture.get_width()),int(groundIntPos[1]*300 % wallTexture.get_height())])#tex = color*((u*9%2>1)^(v*9%2>1))

            floorShade = 0.15 / groundIntDist * viewDist

            color = (floorShade*pix[0], floorShade*pix[1], floorShade*pix[2])
            #print(viewDist + groundIntDist)
            pygame.draw.rect(screen, color, ((x + resX//2) * pixelSize, (h+resY//2) * pixelSize,pixelSize,pixelSize))


def DrawTexRayGround(x, sceneTranslation, viewDist, sceneRotation, rTheta):
    for h in range(-resY // 2, resY // 2):
        if h == 0:
            pygame.draw.rect(screen, (0,0,0), ((x + resX//2) * pixelSize, (h+resY//2) * pixelSize,pixelSize,pixelSize))
        else:
            groundIntDist = viewDist/5*(resY//2)/abs(h)*math.sqrt((x/resX)**2+1) # cameraHeight * (1/2 * resY) / hPix
            groundIntVec = transformedVector([0, groundIntDist], [0,0], -sceneRotation - rTheta)
            groundIntPos = [groundIntVec[0]-sceneTranslation[1]/5, groundIntVec[1]+sceneTranslation[0]/5]

            if h > 0:
                pix = ceilingTexture.get_at([int(groundIntPos[0]*300 % ceilingTextureWidth),int(groundIntPos[1]*300 % ceilingTextureHeight)])#tex = color*((u*9%2>1)^(v*9%2>1))
            else:
                pix = floorTexture.get_at([int(groundIntPos[0]*300 % floorTextureWidth),int(groundIntPos[1]*300 % floorTextureHeight)])#tex = color*((u*9%2>1)^(v*9%2>1))

            floorShade = 0.15 / groundIntDist * viewDist
            color = (floorShade*pix[0], floorShade*pix[1], floorShade*pix[2])

            if h < 0: # draw ground texture
                pygame.draw.rect(screen, color, ((x + resX//2) * pixelSize, (h+resY//2) * pixelSize,pixelSize,pixelSize))
            elif h > 0: # draw ceiling texture
                pygame.draw.rect(screen, color, ((x + resX//2) * pixelSize, (h+resY//2) * pixelSize,pixelSize,pixelSize))

def DrawScene(scene, viewDist, clipDist, groundOffset, sceneRotation, lensDiameter):
    for x in range(-resX//2, resX//2):
        rTheta = math.acos(x / resX * lensDiameter) # for now, just have a pi/2 fov
        minDist = math.inf
        minLine = []
        minInt = []
        for line in scene:
            xDiff = line[1][0] - line[0][0]
            if abs(xDiff) > 0: # the line isn't side-on and invisible
                yDiff = line[1][1] - line[0][1]
                grad =  yDiff / xDiff
                rayToGradDelta = math.tan(rTheta) - grad
                if rayToGradDelta != 0:
                    xi = (line[0][1] - grad * line[0][0]) / rayToGradDelta
                    if line[0][0] > line[1][0]: # flip the line points if point 1 is actually to the right of point 2
                        line = [line[1], line[0]]
                    if xi > line[0][0] and xi < line[1][0]: # the ray equation intercepted a surface
                        yi = grad * xi + line[0][1] - grad * line[0][0]
                        dist = math.sqrt(xi**2 + yi**2)
                        if dist < minDist and yi >= clipDist: # the surface is in front of the camera, and in front of previous surface
                            minInt = [xi, yi]
                            minLine = line
                            minDist = dist

        if minDist < math.inf: # draw a vertical line
            minDist /= math.sqrt((x/resX)**2+1) # lens perspective correction
            #DrawTexRay(x, minInt, minLine, minDist, viewDist)
            DrawTexRayGroundAndGeometry(x, minInt, minLine, minDist, viewDist, groundOffset, sceneRotation, rTheta)
        else: # just draw ground and ceiling
            DrawTexRayGround(x, groundOffset, viewDist, sceneRotation, rTheta)


def main():
    sceneTranslation = [0,0]
    sceneRotation = 0
    viewDist = 1
    clipDist = 0
    lensDiameter = 1.5

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        mousePos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        sceneRotation = mousePos[0] / width * math.pi * 2 # rotate scene according to mousePos
        #viewDist = mousePos[1] / height * 10

        #print(pygame.K_LEFT)
        moveDir = [0, 0]
        if keys[pygame.K_LEFT]:
            moveDir[0] -= 0.2
        if keys[pygame.K_RIGHT]:
            moveDir[0] += 0.2
        if keys[pygame.K_UP]:
            moveDir[1] += 0.2
        if keys[pygame.K_DOWN]:
            moveDir[1] -= 0.2

        moveDir = transformedVector([0,0], moveDir, -sceneRotation)
        sceneTranslation = [sceneTranslation[0]-moveDir[0], sceneTranslation[1]-moveDir[1]]

        transformedScene = TransformScene(testScene, sceneTranslation, sceneRotation)

        DrawScene(transformedScene, viewDist, clipDist, sceneTranslation, sceneRotation, lensDiameter)

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()
