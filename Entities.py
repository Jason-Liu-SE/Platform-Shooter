import math
import pygame


class Entity:
    def __init__(self, name, health, x, y, image, mass, xVel, yVel, r):
        self.collidable = False
        self.health = health
        self.name = name
        self.x = x
        self.y = y
        self.dX = 0
        self.dY = 0
        self.image = image
        self.mass = mass
        self.xVel = xVel
        self.yVel = yVel
        self.falling = True
        self.radius = r
        self.distanceFromObject = 0
        self.accelerationCoefficient = 1
        self.gravityCoefficient = 0.5

    def gravity(self, deltaTime):
        # moving the player
        self.y += (1 / 2) * self.mass * pow(self.yVel, 2) * deltaTime

        # increasing the downwards gravity
        self.yVel += 0.4 * self.gravityCoefficient * deltaTime

        # setting max falling velocity
        if self.yVel > 7:
            self.yVel = 7

    def collides(self, rect1):
        self.collisionX = self.x
        self.collisionY = self.y

        if self.x < rect1.x:
            self.collisionX = rect1.x
        elif (self.x > rect1.x + rect1.width):
            self.collisionX = rect1.x + rect1.width
        if self.y < rect1.y:
            self.collisionY = rect1.y
        elif (self.y > rect1.y + rect1.height):
            self.collisionY = rect1.y + rect1.height

        self.dX = self.x - self.collisionX
        self.dY = self.y - self.collisionY
        self.distanceFromObject = math.sqrt((self.dX * self.dX) + (self.dY * self.dY))

        if self.distanceFromObject <= self.radius:
            return True
        return False

    def move(self, keys, deltaTime):
        # update horizontal position
        if self.xVel > 0:
            self.x += (1 / 2) * self.mass * pow(self.xVel, 2) * deltaTime
        if self.xVel < 0:
            self.x -= (1 / 2) * self.mass * pow(self.xVel, 2) * deltaTime

        # applying friction
        if len(set(keys)) == 1 and not (self.falling):
            self.friction(deltaTime)

        # applying air resistance
        if len(set(keys)) == 1 and self.falling:
            self.airResistance(deltaTime)

        # update vertical position
        if (self.yVel < 0):
            self.y -= (1 / 2) * self.mass * pow(self.yVel, 2) * deltaTime
            self.yVel += 0.4 * self.accelerationCoefficient * deltaTime

        if (self.yVel >= 0 and self.falling):
            self.gravity(deltaTime)

    def friction(self, deltaTime):
        if self.xVel > 0:  # counteract left force
            self.xVel -= 0.2 * self.accelerationCoefficient * deltaTime
            # removed too much force
            if self.xVel < 0:
                self.xVel = 0
        elif self.xVel < 0:  # counteract right force
            self.xVel += 0.2 * self.accelerationCoefficient * deltaTime
            # removed too much force
            if self.xVel > 0:
                self.xVel = 0

    def airResistance(self, deltaTime):
        if self.xVel > 0:
            self.xVel -= 0.03 * self.accelerationCoefficient * deltaTime
        elif self.xVel < 0:
            self.xVel += 0.03 * self.accelerationCoefficient * deltaTime

    def checkForCollision(self, surface):
        if surface != None:
            if (self.collides(
                    surface) and self.distanceFromObject < self.radius):  # checking if the user is not in the air
                # check if the user hit the side, top or bottom
                if self.collisionX == self.x and self.collisionY != self.y:  # hit top or bottom
                    if self.y < self.collisionY:  # top
                        self.sideCollided = "top"
                    elif self.y > self.collisionY:  # bottom
                        self.sideCollided = "bottom"
                elif self.collisionX != self.x and self.collisionY == self.y:  # hit one of the sides
                    if self.x - surface.x > 0:  # right
                        self.sideCollided = "right"
                    elif self.x - surface.x <= 0:  # left
                        self.sideCollided = "left"
                else:
                    self.sideCollided = "corner"

                # using the collision data
                # checking whether it was the top or bottom
                if self.sideCollided == "top":  # top
                    # stopping their motion
                    self.yVel = 0
                    self.falling = False

                    # checking if the player is in the ground
                    self.y = round(self.y - (self.y + 16 - (surface.y)))
                # hit the bottom
                elif self.sideCollided == "bottom":
                    # stopping their motion
                    self.yVel = 0
                    self.falling = True

                    # checking if the player is in the ground
                    self.y = round(self.y - (self.y - 16 - (surface.y + surface.height)))

                # hit a side
                # checking if the player is in the surface
                # checking which side was hit
                elif self.sideCollided == "right":  # right
                    self.xVel = 0
                    self.x = surface.x + surface.width + self.radius
                elif self.sideCollided == "left":  # left
                    self.xVel = 0
                    self.x = surface.x - self.radius

                # hit a corner
                elif self.sideCollided == "corner":
                    # checking which corner was hit
                    # top side
                    if self.y - 16 < surface.y:
                        self.yVel = 0
                        self.falling = False

                        # checking if the player is in the ground
                        self.y = self.y - math.sqrt(pow(self.radius, 2) - pow(self.dX, 2)) - self.dY

                    # bottom side
                    elif self.y + 16 > surface.y + surface.height:
                        self.falling = True

                        # check if the player is in the ground
                        if round(self.distanceFromObject) < self.radius:
                            self.y = self.y + (math.sqrt(16.01 * 16.01 - self.dX * self.dX) - self.dY)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - 16 - camera.xScroll, self.y - 16 - camera.yScroll))


class Enemy(Entity):
    pass


class Player(Entity):
    def checkForDeath(self, map):
        # is below the map
        if self.y > map.height:
            return True

        # health has dropped to 0
        if self.health == 0:
            return True
        return False

    def titleScreen(self, DIMENSIONS, mapWidth, camera, deltaTime):
        # determining if the direction of the movement has to be changed
        if self.x - DIMENSIONS[0] < 0 or self.x + DIMENSIONS[0] > mapWidth:
            self.xVel *= -1

        # moving the camera
        self.x += self.xVel * deltaTime


    def reset(self, camera, initialX, initialY, DIMENSIONS, offset):
        # resetting camera
        camera.actualXScroll = initialX - DIMENSIONS[0] // 2 - 16
        camera.actualYScroll = initialY - DIMENSIONS[1] // 2 - 16 - offset

        # resetting the player
        self.health -= 20
        self.x = initialX
        self.y = initialY
        self.xVel = 0
        self.yVel = 0
        self.falling = True
        self.sideCollided = None