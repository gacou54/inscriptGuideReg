import pyscreenshot as ImageGrab
import PIL.Image as Image
import numpy as np

def capture_box(x1,y1,x2,y2,filename = "default"):
    box = (x1, y1, x2, y2)
    # fullscreen
    im=ImageGrab.grab(bbox=(x1,y1,x2,y2))
    im.save("ScreenCaps/{}.jpg".format(filename))

def calibrate_screenshot(x1,y1,x2,y2):
    im = ImageGrab.grab()
    im = np.asarray(im).copy()
    count = 0
    for x in range(im.shape[0]):
        count += 1
        for y in range(im.shape[1]):
            count += 1
            if (x == x1 - 1 or x == x1 + 1 or x == x2 - 1 or x == x2 + 1) and y > y1 and y < y2:
                im[x][y] = (count%2)*255
            if (y == y1 - 1 or y == y1 + 1 or y == y2 - 1 or y == y2 + 1) and x > x1 and x < x2:
                im[x][y] = (count%2)*255
    Image.fromarray(im).show()

if __name__ == "__main__":
    x1,y1,x2,y2 = 50,50,500,500
    #calibrate_screenshot(x1,y1,x2,y2)
    capture_box(x1,y1,x2,y2)