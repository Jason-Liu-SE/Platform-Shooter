import pygame
from pygame import mixer
from Objects import *

# getting the file path
import pathlib

path = pathlib.Path().absolute()


class Window:
    @staticmethod
    def createWindow(dimensions):
        mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Balls")

        return pygame.display.set_mode(dimensions)

    @staticmethod
    def importGuiTextures(texture):
        return pygame.image.load(str(path) + "\Images\GUI\\" + str(texture) + ".png")

    @staticmethod
    def importTextures(tiles, tileSize, amountOfTiles):
        for i in range(amountOfTiles):
            tiles.append(pygame.transform.scale(pygame.image.load(str(path) + "\Images\Tile Map\\" + str(i + 1) + ".png").convert(), (tileSize, tileSize)).convert())


class GuiObject(Object):
    def __init__(self, objectImage, x, y):
        super().__init__(objectImage, x, y)
        self.image = Window.importGuiTextures(objectImage)


class GUI:
    def __init__(self, **object):
        self.objects = object
        self.itemFont = pygame.font.SysFont("roboto", 32, True)
        self.ammoFont = pygame.font.SysFont("roboto", 32)

    def update(self, screen, player, weapons, DIMENSIONS):
        # drawing other images
        for key, value in self.objects.items():
            if key != "health" and key != "damage":
                screen.blit(value.image, (value.x, value.y))

        # updating the health
        self.updateHealth(screen, player)

        # updating the ammo
        self.updateAmmo(screen, weapons, DIMENSIONS)

        # updating reload
        weapons.drawReload(screen, self.objects["ammo"], DIMENSIONS)

    def updateHealth(self, screen, player):
        for damageIndex in range(5):
            screen.blit(self.objects["damage"].image, (self.objects["damage"].x + damageIndex * 34, self.objects["damage"].y))

        if player.health // 20 > 0:
            for heartIndex in range(player.health // 20):
                screen.blit(self.objects["health"].image, (self.objects["health"].x + heartIndex * 34, self.objects["health"].y))

    def updateAmmo(self, screen, weapons, DIMENSIONS):
        # finding the current weapon
        object = weapons.objects[weapons.currentWeapon]

        # find location for gun and ammunition text
        gunName = self.itemFont.render(weapons.currentWeapon, True, (30, 30, 30))  # getting object data (name and ammo count)
        ammoCount = self.ammoFont.render(str(object.currentAmmo) + str("/") + str(object.maxAmmo), True, (40, 40, 40))

        gunTextLocation = gunName.get_rect(center=(DIMENSIONS[0] - gunName.get_width() // 2 - 10, DIMENSIONS[1] - gunName.get_height() // 2 - 50))  # finding and setting the dimensions of the text
        ammoTextLocation = ammoCount.get_rect(center=(DIMENSIONS[0] - ammoCount.get_width() // 2 - 10, DIMENSIONS[1] - ammoCount.get_height() // 2 - 15))

        # updating location of ammo symbol
        try:
            self.objects["ammo"].x = DIMENSIONS[0] - ammoCount.get_width() - 20 - self.objects["ammo"].image.get_width()
        except:
            print("GUI does not contain keyworded argument \"ammo\"")

        # drawing the gui
        self.drawWeaponGui(screen, gunName, gunTextLocation, ammoCount, ammoTextLocation)

        # checking if the gun should be reloading
        if weapons.reloading:
            pass

    def drawWeaponGui(self, screen, gunName, gunTextLocation, ammoCount, ammoTextLocation):
        screen.blit(gunName, gunTextLocation)  # displaying the text
        screen.blit(ammoCount, ammoTextLocation)


class Camera:
    def __init__(self, initialCentre, initialHeight, DIMENSIONS, offset):
        # how fast the object will move compared to the camera
        self.speedCoefficientFar = 0.1
        self.speedCoefficientClose = 1
        self.speedCoefficientForeground = 1
        self.speedCoefficientMiddle = 1

        self.initialXScroll = initialCentre - DIMENSIONS[0] // 2 - 16  # centering the player to the center of the map
        self.initialYScroll = initialHeight - DIMENSIONS[1] // 2 - 16 - offset
        self.actualXScroll = self.initialXScroll
        self.actualYScroll = self.initialYScroll
        self.xScroll = 0
        self.yScroll = 0

class Button:
    def __init__(self, name, colour, rect):
        self.name = name
        self.INITIALX = rect[0]
        self.INITIALY = rect[1]
        self.currentX = rect[0]
        self.currentY = rect[1]
        self.INITIALWIDTH = rect[2]
        self.INITIALHEIGHT = rect[3]
        self.currentWidth = rect[2]
        self.currentHeight = rect[3]
        self.currentColour = colour
        self.INITIALCOLOUR = colour
        self.xOffset = self.INITIALWIDTH
        self.yOffset = 0
        self.XEXPANSION = 0
        self.YEXPANSION = 0
        self.hovered = False
        self.fontActive = pygame.font.SysFont("roboto", 72, True)
        self.fontIdle = pygame.font.SysFont("roboto", 78, True, True)
        self.text = None
        self.textLocation = []

    def getRect(self, xOffset=0):
        self.tempX = self.INITIALX - self.XEXPANSION
        self.tempY = self.INITIALY - self.YEXPANSION
        self.tempWidth = self.INITIALWIDTH + self.XEXPANSION * 2
        self.tempHeight = self.INITIALHEIGHT + self.YEXPANSION * 2

        # updating the offset
        if not xOffset <= 0:
            self.xOffset -= 8
        if self.xOffset < 0:
            self.xOffset = 0

        # returning the value
        return (self.tempX, self.tempY, self.tempWidth - xOffset, self.tempHeight)

    def reset(self):
        self.currentX = self.INITIALX
        self.currentY = self.INITIALY
        self.currentColour = self.INITIALCOLOUR
        self.currentWidth = self.INITIALWIDTH
        self.currentHeight = self.INITIALHEIGHT
        self.xOffset = 0
        self.XEXPANSION = 0
        self.YEXPANSION = 0
        self.hovered = False

    def draw(self, screen):
        # drawing the button
        pygame.draw.rect(screen, self.INITIALCOLOUR, self.getRect())

        # button is hovered over
        if self.hovered:
            pygame.draw.rect(screen, self.currentColour, self.getRect(self.xOffset))

            # drawing text
            self.text = self.fontIdle.render(self.name, True, (30, 30, 30))
        else:
            self.text = self.fontActive.render(self.name, True, (15, 15, 15))

        self.textLocation = self.text.get_rect(center=(self.currentX + self.currentWidth // 2, self.currentY + self.currentHeight // 2))
        screen.blit(self.text, self.textLocation)


    def isHovering(self, WHITE):
        mouseLocation = pygame.mouse.get_pos()

        # checking if the button should be pressed
        if not self.hovered:
            if mouseLocation[0] >= self.currentX and mouseLocation[0] <= self.currentX + self.currentWidth and mouseLocation[1] >= self.currentY and mouseLocation[1] <= self.currentY + self.currentHeight:
                self.XEXPANSION = 5
                self.YEXPANSION = 5
                self.currentX = self.INITIALX - self.XEXPANSION
                self.currentY = self.INITIALY - self.YEXPANSION
                self.currentWidth = self.INITIALWIDTH + self.XEXPANSION
                self.currentHeight = self.INITIALHEIGHT + self.YEXPANSION
                self.currentColour = WHITE
                self.hovered = True
                self.xOffset = self.currentWidth