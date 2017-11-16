import pyscreenshot as ImageGrab
import PIL.Image as Image
import numpy as np

def capture_box(x1,y1,x2,y2,filename = "default",directory = "ScreenCaps"):
    '''
    Capture d'écran d'une boîte entre (x1,y1), (x2,y2) et sauvegarde
    :param x1: Int: Coordonnée x du coin supérieur gauche de la boîte à capturer [pixels]
    :param y1: Int: Coordonnée y du coin supérieur gauche de la boîte à capturer [pixels]
    :param x2: Int: Coordonnée x du coin inférieur droit de la boîte à capturer [pixels]
    :param y2: Int: Coordonnée y du coin inférieur droit de la boîte à capturer [pixels]
    :param filename: String: Nom donné au fichier de sauvegarde
    :param directory: String: Dossier ou séquence de dossiers dans lequel on sauvegarde la capture
    :return: None
    '''
    im=ImageGrab.grab(bbox=(x1,y1,x2,y2))
    im.save("{}/{}.jpg".format(directory,filename))
    return None

def calibrate_screenshot(x1,y1,x2,y2):
    '''
    Affiches l'écran avec en pointillé l'encadré contenant la boîte entre (x1,y1), (x2,y2)
    :param x1: Int: Coordonnée x du coin supérieur gauche de la boîte à capturer [pixels]
    :param y1: Int: Coordonnée y du coin supérieur gauche de la boîte à capturer [pixels]
    :param x2: Int: Coordonnée x du coin inférieur droit de la boîte à capturer [pixels]
    :param y2: Int: Coordonnée y du coin inférieur droit de la boîte à capturer [pixels]
    :return: None
    '''
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
    return None

if __name__ == "__main__":
    #test des fonctions
    x1,y1,x2,y2 = 50,50,500,500
    calibrate_screenshot(x1,y1,x2,y2)
    capture_box(x1,y1,x2,y2)