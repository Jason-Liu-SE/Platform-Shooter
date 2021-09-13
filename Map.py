import concurrent.futures
import time

class Map:
    def __init__(self, location):
        self.location = location
        self.dimensions = [0, 0]
        self.startX = 0
        self.startY = 0
        self.mapValues = []
        self.tileCoordinates = []
        self.collidableTiles = []
        self.tile = []
        self.width = 0
        self.height = 0

    def drawBackground(self, screen, backgroundImage, camera, DIMENSIONS):
        '''xOffset = camera.initialXScroll * camera.speedCoefficientFar
        yOffset = camera.initialYScroll * camera.speedCoefficientFar
        centerX = camera.initialXScroll + 16 + DIMENSIONS[0]//2
        centerY = camera.initialYScroll + 16 + DIMENSIONS[1]//2       # the 100 is from the camera offset'''

        # getting coordinates for the top left corner of the background
        topLeftCornerX = 0 - (camera.xScroll * camera.speedCoefficientFar - camera.initialXScroll * camera.speedCoefficientFar) - (backgroundImage.get_width() - DIMENSIONS[0]) // 2
        topLeftCornerY = 0 - (camera.yScroll * camera.speedCoefficientFar - camera.initialYScroll * camera.speedCoefficientFar) - (backgroundImage.get_height() - DIMENSIONS[1]) // 2
        '''initialX = 0 - (camera.xScroll * camera.speedCoefficientFar - camera.initialXScroll * camera.speedCoefficientFar)
        initialY = 0 - (camera.yScroll * camera.speedCoefficientFar - camera.initialYScroll * camera.speedCoefficientFar)'''

        # drawing the image
        screen.blit(backgroundImage, (topLeftCornerX, topLeftCornerY))


    def storeDimensions(self, tileSize):
        self.dimensions = [len(self.mapValues) + 2, len(self.mapValues[0]) + 2]
        self.width = self.dimensions[1] * tileSize
        self.height = self.dimensions[0] * tileSize

    def createEmptyBorder(self):
        # top and bottom
        self.mapValues.insert(0, [None for i in range(self.dimensions[1])])  # top row
        self.mapValues.insert(len(self.mapValues), [None for i in range(self.dimensions[1])])  # bottom row

        # sides
        for row in range(self.dimensions[0] - 2):
            self.mapValues[row + 1].insert(0, None)
            self.mapValues[row + 1].append(None)

    def fillList(self, lists):
        # fills lists with None placeholder values
        for list in lists:
            for row in range(self.dimensions[0]):
                list.append([None for col in range(self.dimensions[1])])

    def openMap(self):
        with open(self.location, "r") as f:
            for line in f:
                if line.strip():        # making sure that the line has data
                    temp = line.strip() # removing white space
                    self.mapValues.append([integer for integer in temp])    # adding the value into the list, as a list

    def generateMapData(self, tiles, tileSize):
        # reading and storing the map data
        self.openMap()

        # storing dimensions
        self.storeDimensions(tileSize)

        # adding empty border to map values
        self.createEmptyBorder()

        # creating the lists
        self.fillList([self.tileCoordinates, self.tile])

        # creating the appropriate map
        for rowIndex in range(self.dimensions[0]):
            for colIndex in range(self.dimensions[1]):
                # checking what tile it is
                for index in range(len(tiles)):
                    if self.mapValues[rowIndex][colIndex] != None:
                        if int(self.mapValues[rowIndex][colIndex]) == index + 1:  # deciding what tile it is
                            self.tile[rowIndex][colIndex] = tiles[index]
                            break

                # indicating that a tile has been placed
                self.tileCoordinates[rowIndex][colIndex] = [self.startX, self.startY]
                self.startX += tileSize
            # next row
            self.startY += tileSize
            self.startX = 0

        # checking if the tile is collidable
        for rowIndex in range(self.dimensions[0] - 2):
            for colIndex in range(self.dimensions[1] - 2):
                # checking if there is a tile in that location
                if self.tile[rowIndex + 1][colIndex + 1] != None:
                    # at least one of its sides has a air block
                    if self.tile[rowIndex][colIndex + 1] == None or self.tile[rowIndex + 2][colIndex + 1] == None or \
                            self.tile[rowIndex + 1][colIndex] == None or self.tile[rowIndex + 1][colIndex + 2] == None:
                        self.collidableTiles.append(
                            self.tileCoordinates[rowIndex + 1][colIndex + 1])  # make it collidable