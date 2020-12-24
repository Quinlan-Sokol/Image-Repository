from graphics import *

# class for holding extra information about each image
class Photo:
    name = ""
    path = ""

    border = [Point(0,0), Point(0,0)]

    fullImage = None
    thumbImage = None

    hovering = False
    selected = False

    def __init__(self, name="", path=""):
        # initialize the name and path based on how the Photo is constructed
        self.name = path.split("/")[-1] if name == "" else name
        self.path = path if name == "" else "Images/" + name
        self.fullImage = Image(Point(0,0), self.path)

    # draw the image and its border
    def draw(self, win):
        r = Rectangle(self.border[0], self.border[1])
        r.setFill("darkgrey")

        if self.hovering or self.selected:
            r.setOutline(color_rgb(57, 255, 20))
        else:
            r.setOutline("white")

        r.setWidth(3)
        r.draw(win)

        self.thumbImage = Image(Point(int((self.border[0].x + self.border[1].x)/2)+1,
                                      int((self.border[0].y + self.border[1].y)/2)+1), "Thumbnails/" + self.name)
        self.thumbImage.draw(win)