###################################
######### INTIAL STUFF ############
###################################
# importing the necessary files
from Entities import *
from Window import *
from Surfaces import *
from Map import *
from Objects import *
from ScenicObjects import *
import pygame
import time
import concurrent.futures
import multiprocessing

# getting the file path
import pathlib

path = pathlib.Path().absolute()

# constants
WIDTH = 1280
HEIGHT = 720
DIMENSIONS = (WIDTH, HEIGHT)

###################################
############# VARIABLES ###########
###################################
# pygame
screen = Window.createWindow(DIMENSIONS)

backgroundImage = pygame.image.load(str(path) + "\\Images\\Background.jpg").convert()
blurredBackgroundImage = pygame.image.load(str(path) + "\\Images\\BlurredBackground.jpg").convert()

# game
running = True
clock = pygame.time.Clock()
elapse = time.time()  # used for FPS independence
deltaTime = 1
deltaTimeAverage = 0
timesThroughLoop = 0

# textures
tiles = []
tileSize = 32
amountOfTiles = 3
Window.importTextures(tiles, tileSize, amountOfTiles)

# map
map = Map(str(path) + "\Images\Tile Map\\test.txt")
map.generateMapData(tiles, tileSize)
surfaces = []

# creating map objects
# buildings
buildings = []
maxDistance = 0.8
distanceRange = 0.4

for _ in range (20):
    # finding random values for the building
    x = random.randint(0, map.width)
    y = random.randint(map.height // 20, map.height // 3)
    size = random.uniform(1, 3)
    distance = random.uniform(maxDistance - distanceRange, maxDistance)       # 0 match player speed; 1 moves with background

    # creating a new building
    buildings.append(Building((x, y), size, distance))

# sorting the buildings in order
buildings.sort(key=lambda building: building.distance)

# player
initialHeight = 0
initialCentre = map.width // 2

# creating the drawable surface
for row in range(map.dimensions[0]):
    for col in range(map.dimensions[1]):
        if map.tile[row][col] != None:
            surfaces.append(
                Surface(map.tileCoordinates[row][col][0], map.tileCoordinates[row][col][1], tileSize, tileSize,
                        map.tile[row][col]))

# collidable surfaces (need to use multiprocessing to increase speed)
tempX = []
tempY = []

for x, y in map.collidableTiles:
    tempX.append(x)
    tempY.append(y)

# initial height
for x, y, in map.collidableTiles:
    if x == initialCentre - 16:
        initialHeight = y - 32
        break

# GUI
health = GuiObject("Health", 16, 16)
damage = GuiObject("Damage", 16, 16)
ammo = GuiObject("Ammo", WIDTH - 128, HEIGHT - 38)
gui = GUI(health=health, damage=damage, ammo=ammo)

# start menu buttons
GREEN = (128, 255, 80)
RED = (220, 20, 60)
WHITE = (245, 245, 245)
play = Button("PLAY", GREEN, [DIMENSIONS[0] // 2 - 200, DIMENSIONS[1] // 2 - 50, 400, 100])
quit = Button("QUIT", RED, [DIMENSIONS[0] // 2 - 190, DIMENSIONS[1] // 2 + 80, 380, 90])
lastUpPosition = [0, 0]

offset = 100  # camera
camera = Camera(initialCentre, initialHeight, DIMENSIONS, offset)

# weapons
rifle = WeaponObject("Rifle", 0, 0, damage=44, ammo=30, firerate=14, accuracy=80, recoil=1, reload=2.2, distance=WIDTH * 2, velocity=30)  # objectImage, x, y, ammo, firerate (bullets per second with no reload), accuracy %, recoil, reload (seconds), max travelable distance
pistol = WeaponObject("Pistol", 0, 0, damage=34, ammo=8, firerate=6, accuracy=95, recoil=1, reload=0.8, distance=WIDTH * 1.5, velocity=30)
weapons = Weapon(Rifle=rifle, Pistol=pistol)

# player
playerImage = pygame.image.load(str(path) + "\\Images\\Player.png")

# player jump/gravity
mass = 1
player = Player("Hyqer", 100, initialCentre, initialHeight, playerImage, mass, 0, 0,
                playerImage.get_height() // 2)  # creating the player
player.xVel = 1

#########################################
########## FUNCTIONS ####################
#########################################
def titleScreen(screen, lastUpPosition, player, **button):
    global running

    # storing buttons
    play = button["play"]
    quit = button["quit"]

    # determining if a button is hovered over
    mouseLocation = pygame.mouse.get_pos()      # mouse location

    if mouseLocation[0] >= play.currentX and mouseLocation[0] <= play.currentX + play.currentWidth and mouseLocation[1] >= play.currentY and mouseLocation[1] <= play.currentY + play.currentHeight:    # play button
        if lastUpPosition[0] >= play.currentX and lastUpPosition[0] <= play.currentX + play.currentWidth and lastUpPosition[1] >= play.currentY and lastUpPosition[
            1] <= play.currentY + play.currentHeight:
            # clicked the button
            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1]:
                player.collidable = True
    elif mouseLocation[0] >= quit.currentX and mouseLocation[0] <= quit.currentX + quit.currentWidth and mouseLocation[1] >= quit.currentY and mouseLocation[1] <= quit.currentY + quit.currentHeight:  # play button
        if lastUpPosition[0] >= quit.currentX and lastUpPosition[0] <= quit.currentX + quit.currentWidth and lastUpPosition[1] >= quit.currentY and lastUpPosition[
            1] <= quit.currentY + quit.currentHeight:  # play button
            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1]:
                running = False
    else:       # neither button is hovered over
        play.reset()
        quit.reset()

    # checking if the button should indicate that it has been pressed
    play.isHovering(WHITE)
    quit.isHovering(WHITE)

    # drawing buttons
    play.draw(screen)
    quit.draw(screen)


def hitsSurface(x, y):
    for surface in surfaces:
        if surface.x == x and surface.y == y:
            return surface

def getKeyPresses(keys):
    # the playing is on the ground
    if keys[pygame.K_a] and not (player.falling) and len(set(keys)) == 2:
        if player.xVel > -4 * player.accelerationCoefficient:
            player.xVel -= 0.3 * player.accelerationCoefficient
    if keys[pygame.K_d] and not (player.falling) and len(set(keys)) == 2:
        if player.xVel < 4 * player.accelerationCoefficient:
            player.xVel += 0.3 * player.accelerationCoefficient
    # arial movement
    if keys[pygame.K_a] and player.falling and len(set(keys)) == 2:
        if player.xVel > -3 * player.accelerationCoefficient:
            player.xVel -= 0.2 * player.accelerationCoefficient
    if keys[pygame.K_d] and player.falling and len(set(keys)) == 2:
        if player.xVel < 3 * player.accelerationCoefficient:
            player.xVel += 0.2 * player.accelerationCoefficient
    # both directional keys are pressed
    if keys[pygame.K_d] and keys[pygame.K_a] and not (player.falling):
        player.xVel = 0
    # reloading
    if keys[pygame.K_r] and not weapons.reloading and weapons.objects[weapons.currentWeapon].currentAmmo != weapons.objects[weapons.currentWeapon].maxAmmo:
        weapons.reloadStart = time.time()
        weapons.reloading = True

    # player jump
    if (keys[pygame.K_SPACE] and not (player.falling)):
        player.yVel = -9.8 * player.gravityCoefficient
        player.falling = True

    # reset key
    if keys[pygame.K_e]:
        player.reset(camera, initialCentre, initialHeight, DIMENSIONS, offset)

def getMousePresses():
    # checking for mouse events
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):  # quiting
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # firing
            if event.button == 1:
                weapons.firing = True
        elif event.type == pygame.MOUSEBUTTONUP:  # stopped firing
            if event.button == 1:
                weapons.firing = False
    return True

def drawImages(screen):
    # drawing the background
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, HEIGHT))

    if player.collidable:
        map.drawBackground(screen, backgroundImage, camera, DIMENSIONS)
    else:
        map.drawBackground(screen, blurredBackgroundImage, camera, DIMENSIONS)

    # draw close-background
    Building.draw(screen, buildings, maxDistance, distanceRange, camera, DIMENSIONS)

    # drawing the map
    for surface in surfaces:
        if surface != None:
            # draw the tiles that are within the viewable space, +1 in each direction
            if surface.x - camera.xScroll >= -tileSize and surface.x - camera.xScroll <= WIDTH + tileSize and surface.y - camera.yScroll >= -tileSize and surface.y - camera.yScroll <= HEIGHT + tileSize:
                surface.draw(screen, camera)

    # draw mid layer (same as player)

    # drawing the player
    if player.collidable:
        player.draw(screen, camera)

        # drawing bullets
        for bullet in weapons.bullets:
            bullet.draw(screen, camera)

        # drawing weapons
        weapons.draw(screen, player, camera)

    # draw foreground

    # drawing the GUI
    if player.collidable:
        gui.update(screen, player, weapons, DIMENSIONS)

    # checking if the player is in the title screen
    if not player.collidable:
        titleScreen(screen, lastUpPosition, player, play = play, quit = quit)

    # updating
    clock.tick(1000)
    pygame.display.update()

##########################################
################ MAIN ####################
##########################################
# finding the collidable surfaces
with concurrent.futures.ThreadPoolExecutor() as executor:
    collidableSurfaces = list(executor.map(hitsSurface, tempX, tempY))

# creating the game loop
while (running):
    ########## INITIAL SETTINGS ##########
    player.falling = True
    tempBullets = weapons.bullets  # temp list to ensure that the for loop iterates correctly

    ############# TIME ###################
    # calculate time difference
    deltaTime = time.time() - elapse
    elapse = time.time()

    if deltaTime > 1 / 30:  # making sure that the ball doesn't teleport through tiles
        deltaTime = 1 / 30

    # removing the stuttering and jittering
    if timesThroughLoop > 120:
        timesThroughLoop /= 2
        deltaTimeAverage /= 2

    timesThroughLoop += 1
    deltaTimeAverage += deltaTime

    deltaTime = deltaTimeAverage / timesThroughLoop * 60

    ############ MOVING CAMERA ###########
    camera.actualXScroll += (player.x - camera.actualXScroll - (
            DIMENSIONS[0] + player.radius * 2 - player.image.get_width()) // 2) / 10 * deltaTime
    camera.actualYScroll += (player.y - camera.actualYScroll - (
            DIMENSIONS[1] + player.radius * 2) // 2 - offset) / 10 * deltaTime

    ############## COLLISION DETECTION ################
    # checking if the player has collided with a surface
    if player.collidable:
        for surface in collidableSurfaces:
            if surface.x - camera.xScroll >= -tileSize and surface.x - camera.xScroll <= WIDTH + tileSize and surface.y - camera.yScroll >= -tileSize and surface.y - camera.yScroll <= HEIGHT + tileSize:
                player.checkForCollision(surface)

                # checks if the bullet hit an object (only if on screen)
                for bullet in tempBullets:
                    if bullet.collides(surface):
                        # removing bullet
                        weapons.bullets.remove(bullet)
                        break

    ############## EVENTS ################
    # checking if the user pressed a key
    keys = pygame.key.get_pressed()

    if player.collidable:
        getKeyPresses(keys)

    # mouse events
    running = getMousePresses()
    if not player.collidable:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # checking where the mouse was last up
    if not pygame.mouse.get_pressed()[0] or not pygame.mouse.get_pressed()[0]:
        lastUpPosition = pygame.mouse.get_pos()

    ############## UPDATING ################
    # drawing images
    drawImages(screen)

    # checking if the gun should be reloading or fired
    # firing the gun only when cocked (delay in between shots)
    if player.collidable:
        if weapons.firing and not weapons.reloading and time.time() - weapons.startTime >= weapons.objects[weapons.currentWeapon].firerate and player.collidable:
            weapons.fire(camera)
        weapons.reload()

    # fixing stuttering camera
    camera.xScroll = camera.actualXScroll
    camera.yScroll = camera.actualYScroll

    # moving
    if player.collidable:
        player.move(keys, deltaTime)  # player
    else:
        player.titleScreen(DIMENSIONS, map.width, camera, deltaTime)

    # moving bullets
    if player.collidable:
        for bullet in tempBullets:
            # moves beyong the maximum effective range
            if bullet.distanceTraveled <= bullet.maxDistance:  # checking if the bullet has not reached its maximum effective range
                bullet.move(deltaTime)
            else:
                weapons.bullets.remove(bullet)

        # checking if the player has died
        if player.checkForDeath(map):
            player.reset(camera, initialCentre, initialHeight, DIMENSIONS, offset)


"""# starting the game
if __name__ == "__main__":
processor1 = multiprocessing.Process(target=main)
processor1.start()
processor1.join()"""
