from Entities import *
from Window import *
import pygame
from pygame import gfxdraw
import math
import time
import random

# getting the file path
import pathlib
path = pathlib.Path().absolute()

class Object:
    def __init__(self, objectImage, x, y):
        self.image = objectImage
        self.x = x
        self.y = y

class WeaponObject(Object):
    def __init__(self, objectImage, x, y, **stats):
        super().__init__(objectImage, x, y)
        self.image = pygame.image.load(str(path) + "\Images\Items\\" + str(
                    objectImage) + ".png")

        self.damage = stats["damage"]
        self.maxAmmo = stats["ammo"]
        self.currentAmmo = stats["ammo"]
        self.firerate = 1 / stats["firerate"]
        self.accuracy = stats["accuracy"]
        self.inaccuracy = (100 - self.accuracy) / 400
        self.recoil = stats["recoil"]
        self.reloadTime = stats["reload"]
        self.maxTravelDistance = stats["distance"]
        self.vel = stats["velocity"]


class Weapon:
    def __init__(self, **objects):
        self.objects = objects
        self.currentWeapon = "Rifle"
        self.reloading = False
        self.startTime = 0
        self.reloadStart = 0
        self.firing = False
        self.bullets = []
        self.directionFired = None
        self.radiansConversion = 0.0174533
        self.angle = 0
        self.center = (0, 0)

    def draw(self, screen, player, camera):
        for weapon, value in self.objects.items():
            # only updating the current weapon
            if weapon == self.currentWeapon:
                # locating where to place the weapon
                self.rotatedImage, self.centeredRect = self.updateLocation(player, camera)

                # placing the weapon
                screen.blit(self.rotatedImage, self.centeredRect)

    def updateLocation(self, player, camera):
        # only updating the current weapon
        mouseLocation = pygame.mouse.get_pos()      # a tuple with the mouse location

        # checking if the value is zero (zero division error)
        if mouseLocation[0] - (player.x - camera.xScroll) == 0:
            tempAngle = 0
        else:
            tempAngle = (mouseLocation[1] - (player.y - camera.yScroll)) / (mouseLocation[0] - (player.x - camera.xScroll))

        self.angle = math.atan(tempAngle)

        # finding offset
        self.xOffset = math.cos(self.angle) * 15
        self.yOffset = math.sin(self.angle) * 15

        # identifying which direction the gun should point
        if mouseLocation[0] >= (player.x - camera.xScroll):      # to right of player
            # finding center of image
            self.center = (player.x - camera.xScroll + self.xOffset, player.y - camera.yScroll + self.yOffset)

            # getting rect coordinates for rotated image
            rotatedImage = pygame.transform.rotate(self.objects[self.currentWeapon].image, -math.degrees(self.angle))

            # changing the direction that the bullet was fired
            self.directionFired = "right"
        else:                                   # to left of player
            # finding center of image
            self.center = (player.x - camera.xScroll - self.xOffset, player.y - camera.yScroll - self.yOffset)

            # getting rect coordinates for rotated image
            rotatedImage = pygame.transform.flip(pygame.transform.rotate(self.objects[self.currentWeapon].image, math.degrees(self.angle)), True, False)

            # changing the direction that the bullet was fired
            self.directionFired = "left"

        # setting the center of the rotated image
        centerRect = rotatedImage.get_rect(center = self.center)

        return rotatedImage, centerRect

    def reload(self):
        # checking if the weapon is reloading
        if self.reloading:
            # delay between the start of the reload vs. current time > weapon reload time
            if time.time() - self.reloadStart >= self.objects[self.currentWeapon].reloadTime:
                self.objects[self.currentWeapon].currentAmmo = self.objects[self.currentWeapon].maxAmmo     # setting the weapon back to full capacity
                self.reloading = False

    def drawReload(self, screen, ammoObject, DIMENSIONS):
        if self.reloading:
            # drawing shaded circle
            gfxdraw.filled_circle(screen, DIMENSIONS[0] // 2, DIMENSIONS[1] // 2, 20, (0, 0, 0, 100))

            # drawing a circle around the image
            pygame.draw.arc(screen, (255, 255, 255), (DIMENSIONS[0] // 2 - 20, DIMENSIONS[1] // 2 - 20, 41, 41), -((time.time() - self.reloadStart) * (360/self.objects[self.currentWeapon].reloadTime) - 90)  * self.radiansConversion, 90 * self.radiansConversion)

            # drawing icon in centre of screen
            screen.blit(ammoObject.image, (DIMENSIONS[0] // 2 - ammoObject.image.get_width() // 2, DIMENSIONS[1] // 2 - ammoObject.image.get_height() // 2))

    def fire(self, camera):
        object = self.objects[self.currentWeapon]

        # checking if the weapon has bullets left
        if object.currentAmmo > 0 and time.time() - self.startTime >= object.firerate:
            # updating ammunition
            self.objects[self.currentWeapon].currentAmmo -= 1
            self.startTime = time.time()    # starting the next-shot delay

            # applying the inaccuracy
            tempAngle = self.angle + random.uniform(-object.inaccuracy, object.inaccuracy)

            # locating where the muzzle of the gun is
            if (self.directionFired == "right" and tempAngle >= 0 and self.angle >= 0) or (self.directionFired == "right" and tempAngle <= 0 and self.angle <= 0) or (self.directionFired == "left" and tempAngle <= 0 and self.angle >= 0) or (self.directionFired == "lefty" and tempAngle > 0 and self.angle < 0):
                bulletX = (self.center[0] + camera.xScroll) + math.cos(self.angle) * (object.image.get_width() // 4)
                bulletY = (self.center[1] + camera.yScroll) + math.sin(self.angle) * (object.image.get_width() // 4)
                bulletX2 = (self.center[0] + camera.xScroll) + math.cos(tempAngle) * (object.image.get_width() // 4 + 20)
                bulletY2 = (self.center[1] + camera.yScroll) + math.sin(tempAngle) * (object.image.get_width() // 4 + 20)
            else:
                bulletX = (self.center[0] + camera.xScroll) - math.cos(self.angle) * (object.image.get_width() // 4)
                bulletY = (self.center[1] + camera.yScroll) - math.sin(self.angle) * (object.image.get_width() // 4)
                bulletX2 = (self.center[0] + camera.xScroll) - math.cos(tempAngle) * (object.image.get_width() // 4 + 20)
                bulletY2 = (self.center[1] + camera.yScroll) - math.sin(tempAngle) * (object.image.get_width() // 4 + 20)

            # firing the bullet
            self.bullets.append(Bullet(bulletX, bulletY, bulletX2, bulletY2, object.vel, (255, 153, 0), self.objects[self.currentWeapon].maxTravelDistance, tempAngle, self.directionFired))   # x1, y1, x2, y2, vel, color

        # no more bullets
        elif object.currentAmmo <= 0:
            # start reload process
            self.reloadStart = time.time()
            self.reloading = True

class Bullet:
    def __init__(self, x1, y1, x2, y2, vel, color, maxDistance, angle, direction):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vel = vel
        self.color = color
        self.distanceTraveled = 0
        self.maxDistance = maxDistance
        self.angle = angle
        self.direction = direction

    def draw(self, screen, camera):
        pygame.draw.line(screen, self.color, (self.x1 - camera.xScroll, self.y1 - camera.yScroll), (self.x2 - camera.xScroll, self.y2 - camera.yScroll), 2)

    def move(self, deltaTime):
        # moving the bullet
        if self.direction == "right":
            self.x1 += math.cos(self.angle) * self.vel * deltaTime
            self.x2 += math.cos(self.angle) * self.vel * deltaTime
            self.y1 += math.sin(self.angle) * self.vel * deltaTime
            self.y2 += math.sin(self.angle) * self.vel * deltaTime
        elif self.direction == "left":
            self.x1 -= math.cos(self.angle) * self.vel * deltaTime
            self.x2 -= math.cos(self.angle) * self.vel * deltaTime
            self.y1 -= math.sin(self.angle) * self.vel * deltaTime
            self.y2 -= math.sin(self.angle) * self.vel * deltaTime

        # updating the distance moved
        self.distanceTraveled += self.vel * deltaTime

    def collides(self, rect1):
        collisionX = self.x2
        collisionY = self.y2

        if self.x2 < rect1.x:
            collisionX = rect1.x
        elif (self.x2 > rect1.x + rect1.width):
            collisionX = rect1.x + rect1.width
        if self.y2 < rect1.y:
            collisionY = rect1.y
        elif (self.y2 > rect1.y + rect1.height):
            collisionY = rect1.y + rect1.height

        dX = self.x2 - collisionX
        dY = self.y2 - collisionY
        distanceFromObject = math.sqrt((dX * dX) + (dY * dY))

        if distanceFromObject <= 0:
            return True
        return False




