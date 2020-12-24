from graphics import *
from math import floor, sqrt
from functools import reduce
from operator import add
from Photo import Photo
from os import listdir, remove
from PIL import Image, ImageChops
from tkinter.font import Font
from tkinter.filedialog import askopenfilenames, askopenfilename, askdirectory

wSize = (1500, 1000)
mousePos = Point(0, 0)
scrollCount = 0
prevScroll = 0
windowOpen = True

images = []
filteredImages = []

hoverImage = None
searchImage = None

add_error = False
add_error_lst = []

hoverAdd = False
hoverDelete = False
hoverDeselect = False
hoverDownload = False
hoverSearch = False
hoverSet = False
hoverClear = False

# text search field
textField = Entry(Point(1240, 250), 50)
textField.setSize(16)
textField.setFill("darkgrey")
prevText = ""

# image tolerance field
toleranceField = Entry(Point(1190, 45), 8)
toleranceField.setSize(16)
toleranceField.setFill("darkgrey")

searchTolerance = 50
comparisonDict = {}

def createText(win, pos, string, color="black", face="helvetica", size=12, style="normal"):
    t = Text(pos, string)
    t.setFace(face)
    t.setSize(size)
    t.setStyle(style)
    t.setTextColor(color)
    t.draw(win)


def createRectangle(win, p1, p2, fcolor="", ocolor="black", width=1):
    r = Rectangle(p1, p2)
    r.setFill(fcolor)
    r.setOutline(ocolor)
    r.setWidth(width)
    r.draw(win)


def createLine(win, p1, p2, color="black", width=1, arrow="none"):
    l = Line(p1, p2)
    l.setOutline(color)
    l.setWidth(width)
    l.setArrow(arrow)
    l.draw(win)


# clear all items but those in ex from the window
def clear(win, ex=[]):
    for item in win.items[:]:
        if str(item.__class__.__name__) not in ex:
            item.undraw()


# link mouse motion to a variable
def motion(e):
    global mousePos
    mousePos = Point(e.x, e.y)


# link mouse scroll to a variable
def mouse_wheel(e):
    if len(filteredImages) > 4:
        global scrollCount
        global prevScroll
        prevScroll = scrollCount
        scrollCount += 1 if e.delta > 0 else -1

        if scrollCount > 0:
            scrollCount = 0

        if len(window.find_overlapping(20, window.height-75, 20, window.height+1)) == 2:
            scrollCount = prevScroll+1


# calculates the new coordinates of each image
def setImageTable(lst):
    splitList = [lst[x:x+4] for x in range(0, len(lst), 4)]
    for y in range(len(splitList)):
        for x in range(len(splitList[y])):
            i = x + (y * 4)
            x1 = 9*(x+1) + 366*x
            y1 = 300 + (scrollCount*30) + 366*y + 9*y
            x2 = 9*x + 366*(x+1)
            y2 = 300 + 366 + (scrollCount*30) + 366*y + 9*y

            lst[i].border = [Point(x1, y1), Point(x2, y2)]


# load images into the list
def loadImages():
    return [Photo(f) for f in listdir("Images/") if ".png" in f]


# generate any new thumbnails required, resizing to fit in the border
def createThumbnails(lst):
    cache = [f for f in listdir("Thumbnails/") if ".png" in f]
    for image in filter(lambda x : x.name not in cache, lst):
        name = image.name
        im = Image.open(image.path)

        w = im.width
        h = im.height
        if w > h:
            im = im.resize((354, int(h * (354 / w))))
        else:
            im = im.resize((int(w * (362 / h)), 362))

        im.save("Thumbnails/" + name)


# draws the top interface and buttons
def drawMenu(win):
    # background
    createRectangle(win, Point(0, 0), Point(wSize[0], 290), fcolor="lightgrey", ocolor="black", width=2)

    # 'add' button
    createRectangle(win, Point(25, 25), Point(150, 65), fcolor=(color_rgb(60, 60, 60) if hoverAdd else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(87, 45), "Add Images", color="white", size=16, style="bold")

    # draw files unable to be added
    if add_error:
        createText(win, Point(95, 75), "Unable to add the following", color="red", size=15)
        createText(win, Point(95, 90), "due to existing names:", color="red", size=15)
        for y in range(len(add_error_lst)):
            if y == 11:
                createText(win, Point(95, 90 + 15 * (y + 1)), "and " + str(len(add_error_lst) - y) + " more images", color="red", size=15)
                break
            createText(win, Point(95, 90 + 15 * (y+1)), add_error_lst[y], color="red", size=15)

    # 'delete' button
    createRectangle(win, Point(220, 25), Point(380, 65), fcolor=(color_rgb(60, 60, 60) if hoverDelete else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(300, 45), "Delete Selection", color="white", size=16, style="bold")

    # 'deselect' button
    createRectangle(win, Point(450, 25), Point(580, 65), fcolor=(color_rgb(60, 60, 60) if hoverDeselect else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(515, 45), "Deselect All", color="white", size=16, style="bold")

    # draw selected files
    lst = sorted(list(map(lambda x : x.name, filter(lambda x : x.selected, images))))
    if len(lst) > 0:
        createText(win, Point(515, 80), "Selected:", color="red", size=15)
        for y in range(len(lst)):
            if y == 11:
                createText(win, Point(515, 85 + 15 * (y + 1)), "and " + str(len(lst) - y) + " more images", color="red", size=15)
                break
            createText(win, Point(515, 85 + 15 * (y+1)), lst[y], color="red", size=15)

    # 'download' button
    createRectangle(win, Point(650, 25), Point(830, 65), fcolor=(color_rgb(60, 60, 60) if hoverDownload else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(740, 45), "Download Selection", color="white", size=16, style="bold")

    # 'search' button
    createRectangle(win, Point(900, 25), Point(1030, 65), fcolor=(color_rgb(60, 60, 60) if hoverSearch else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(965, 45), "Image Search", color="white", size=16, style="bold")

    # draws the selected search image
    if searchImage is not None:
        createText(win, Point(965, 80), "Selected:", color="red", size=15)
        createText(win, Point(965, 98), searchImage.filename.split("/")[-1], color="red", size=15)

        # 'clear' button
        createRectangle(win, Point(930, 115), Point(1000, 145), fcolor=(color_rgb(60, 60, 60) if hoverClear else "black"), ocolor=color_rgb(70, 102, 255), width=1)
        createText(win, Point(965, 130), "Clear", color="white", size=14, style="bold")

    # 'set' button
    createRectangle(win, Point(1255, 30), Point(1305, 60), fcolor=(color_rgb(60, 60, 60) if hoverSet else "black"), ocolor=color_rgb(70, 102, 255), width=1)
    createText(win, Point(1280, 45), "Set", color="white", size=14, style="bold")

    createText(win, Point(975, 250), "Search:", size=16)
    createText(win, Point(1105, 45), "Tolerance:", size=16)


# determines if Point p is within a rectangle
def inRect(p, r1, r2):
    return r1.x <= p.x <= r2.x and r1.y <= p.y <= r2.y


# draws the info bar on the bottom of the window
def drawInfoBar(win):
    # outline / background
    createRectangle(win, Point(0, wSize[1]-40), Point(wSize[0], wSize[1]), fcolor="black", ocolor=color_rgb(70, 102, 255), width=2)
    createLine(win, Point(20, wSize[1]-41), Point(20, wSize[1]), color="black", width=1)

    # draws the info from the hovered image
    if hoverImage is not None:
        name_width = Font(font=('courier', 16, "bold")).measure(hoverImage.name)
        createText(win, Point(25 + name_width/2, wSize[1]-22), hoverImage.name, color="white", face="courier", size=16, style="bold")

        res_string = str(hoverImage.fullImage.getWidth()) + " x " + str(hoverImage.fullImage.getHeight())
        res_width = Font(font=('courier', 16, "bold")).measure(res_string)
        createText(win, Point(wSize[0]-25-res_width/2, wSize[1]-22), res_string, color="white", face="courier",size=16, style="bold")


# adds the new images in lst to the program
def addImages(lst):
    global add_error, add_error_lst
    add_error = False
    add_error_lst = []

    # list of existing images
    cache = [f for f in listdir("Images/") if ".png" in f]
    lst2 = []

    for path in lst:
        name = path.split("/")[-1]
        if name not in cache: #new image
            images.append(Photo(path=path))
            lst2.append(images[-1])

            im = Image.open(path)
            im.save("Images/" + name)

            # calculates the values needed for image searches
            comparisonDict[images[-1].name] = compare(searchImage, images[-1])
        else: # existing images, shows in the menu
            add_error = True
            add_error_lst.append(name)

    #generates thumbnails for the new images
    createThumbnails(lst2)


# filters the images for image searching and text searching
def filterImages():
    return [im for im in images if textField.getText().lower() in im.name[:-4].lower() and comparisonDict[im.name] <= searchTolerance]


# compares 2 images and returns a value 0 <= x <= 100, where 0 is a perfect match
def compare(image1, image2):
    if image1 is None:
        return 0

    im1 = image1
    h1 = im1.histogram()
    p1 = image1.width * image1.height

    im2 = Image.open(image2.path)
    h2 = im2.histogram()
    p2 = image2.fullImage.getWidth() * image2.fullImage.getHeight()

    # returns the average percent difference between each value of the histogram
    return sum(map(lambda x, y: 0 if (x == 0 and y == 0) else (abs((x / p1) - (y / p2)) / (((x / p1) + (y / p2)) / 2)), h1, h2)) / len(h1) * 100


# generates values for the dictionary of comparisons to the given image to search by
def createComparisons(im):
    dic = dict()
    for image in images:
        dic[image.name] = compare(im, image)
    return dic


# callback function for closing the window
def onClose():
    global windowOpen
    windowOpen = False
    window.master.destroy()


# initialize the window
window = GraphWin("Image Repository", wSize[0], wSize[1], autoflush=False)
window.setBackground("black")
window.bind("<Motion>", motion)
window.bind("<MouseWheel>", mouse_wheel)
window.master.protocol("WM_DELETE_WINDOW", onClose)

#initialize the images and comparisons
images = loadImages()
filteredImages = images[:]
createThumbnails(images)
comparisonDict = createComparisons(searchImage)

# draw the text fields
textField.draw(window)
toleranceField.draw(window)
toleranceField.setText(searchTolerance)

while windowOpen:
    # clear entire window except the text fields
    clear(window, ex=["Entry"])

    # recalculate image positions
    setImageTable(filteredImages)

    for image in filteredImages:
        # check if the cursor is hovering over an image, not the top menu or info bar
        if inRect(mousePos, image.border[0], image.border[1]) and not inRect(mousePos, Point(0, 0), Point(wSize[0], 290)) and not inRect(mousePos, Point(0, wSize[1]-40), Point(wSize[0], wSize[1])):
            hoverImage = image
            image.hovering = True
        else:
            image.hovering = False

        # draw the image
        image.draw(window)

    # determine if the mouse is over any of the buttons
    hoverAdd = inRect(mousePos, Point(25, 25), Point(150, 65))
    hoverDelete = inRect(mousePos, Point(220, 25), Point(380, 65))
    hoverDeselect = inRect(mousePos, Point(450, 25), Point(580, 65))
    hoverDownload = inRect(mousePos, Point(650, 25), Point(830, 65))
    hoverSearch = inRect(mousePos, Point(900, 25), Point(1030, 65))
    hoverSet = inRect(mousePos, Point(1255, 30), Point(1305, 60))
    hoverClear = inRect(mousePos, Point(930, 115), Point(1000, 145))

    #draw the top menu, info bar
    drawMenu(window)
    drawInfoBar(window)
    hoverImage = None

    # dealing if a user click
    click = window.checkMouse()
    if click is not None:
        if inRect(click, Point(0, 0), Point(wSize[0], 290)): #menu click
            if inRect(click, Point(25, 25), Point(150, 65)): #add
                files = askopenfilenames(title="Select Images", filetypes=(("png files","*.png"),("all files","*.*")))
                addImages(files)
                filteredImages = filterImages()
            if inRect(click, Point(220, 25), Point(380, 65)): #delete
                selectedImages = list(filter(lambda x : x.selected, images))
                for image in selectedImages:
                    images.remove(image)
                    remove("Images/" + image.name)
                filteredImages = filterImages()
            if inRect(click, Point(450, 25), Point(580, 65)): #deselect
                for image in images:
                    image.selected = False
            if inRect(click, Point(650, 25), Point(830, 65)): #download
                path = askdirectory()
                if path != "":
                    selectedImages = list(filter(lambda x: x.selected, images))
                    for image in selectedImages:
                        im = Image.open(image.path)
                        im.save(path + "/" + image.name)
            if inRect(click, Point(900, 25), Point(1030, 65)): #image search
                try:
                    searchImage = Image.open(askopenfilename(title="Select Image", filetypes=(("png files","*.png"),("all files","*.*"))))
                    comparisonDict = createComparisons(searchImage)
                    filteredImages = filterImages()
                except(AttributeError):
                    pass
            if inRect(click, Point(1255, 30), Point(1305, 60)): #set
                searchTolerance = 0 if toleranceField.getText() == "" else int(toleranceField.getText())
                filteredImages = filterImages()
            if inRect(click, Point(930, 115), Point(1000, 145)): #clear search image
                searchImage = None
                comparisonDict = createComparisons(searchImage)
                filteredImages = filterImages()
        elif not inRect(mousePos, Point(0, wSize[1]-40), Point(wSize[0], wSize[1])): #photo click
            for image in filteredImages:
                if inRect(click, image.border[0], image.border[1]):
                    image.selected = not image.selected

    # anytime the text search field is updated, recalculate the images
    curText = textField.getText()
    if prevText != curText:
        filteredImages = filterImages()
        scrollCount = 0
    prevText = curText

    # limit the characters allowed in the tolerance field
    toleranceText = "".join([c for c in toleranceField.getText() if c.isdigit()])
    if toleranceText == "":
        pass
    else:
        while int(toleranceText) > 100:
            toleranceText = toleranceText[:-1]

    toleranceField.setText(toleranceText)

    # update the window
    update(10)
