import pygame

class ScenicObjects:
    def __init__(self, position, sizeCoefficient, distanceCoefficient):
        self.position = position
        self.size = sizeCoefficient
        self.distance = distanceCoefficient

class Building(ScenicObjects):
    @staticmethod
    def draw(screen, buildings, maxDistance, distanceRange, camera, DIMENSIONS):
        width = 100
        borderSize = 10

        # drawing the buildigns
        for building in buildings:
            offset = (int(camera.xScroll * building.distance), int(camera.yScroll * building.distance))
            # colourMultiplier = pow(40, building.distance)
            colourMultiplier = 25 * (maxDistance + distanceRange - building.distance)
            colourPalleteMultiplier = (12, 4.8, 7.6)

            # drawing the border of the building
            pygame.draw.rect(screen, (colourPalleteMultiplier[0] / 1.5 * colourMultiplier, colourPalleteMultiplier[1] / 1.5 * colourMultiplier, colourPalleteMultiplier[2] / 1.5 * colourMultiplier), (building.position[0] - offset[0], building.position[1] - offset[1], width * building.size, DIMENSIONS[1] - building.position[1] + offset[1]))

            # drawing the building
            pygame.draw.rect(screen, (colourPalleteMultiplier[0] * colourMultiplier, colourPalleteMultiplier[1] * colourMultiplier, colourPalleteMultiplier[2] * colourMultiplier), (building.position[0] - offset[0] + borderSize//2, building.position[1] - offset[1] + borderSize//2, width * building.size - borderSize, DIMENSIONS[1] - building.position[1] + offset[1]))