class Surface:
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

    def draw(self, screen, camera):
        screen.blit(self.image, (self.x - camera.xScroll, self.y - camera.yScroll))
