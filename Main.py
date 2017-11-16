'''
Exécution principale de la prise de données suivie de l'Extraction du score puis du fitting
    Trois étapes:
        1- Initialisation:
            -On initialise le point de plasma dans le montage expérimental (mean).
            -On trouve les intervalles utiles des polynomes de zernick (variances).
            -On génère la série de points à prendre en photo
            -On calibre la capture d'écran sur la fenêtre de la caméra.

        2- Prise de données:
            -On applique le polynome de zernick du premier point
            -On fait une capture d'écran du plasma
            -On répète cette étape pour tous les points

        3- Extraction du score:
            -On passe sur toutes les images générées et on en extrait le score de rondeur

        4- Fitting
            -On entraine un classifieur quelconque sur le set de données ainsi généré
'''

#Prise de données
from GenerateGaussianList import generate_sequence
from Screenshot import capture_box, calibrate_screenshot
from spotShapeDetec import round_score
import time
import numpy as np

def set_box_inputs(JustScreenshot = False):
    if JustScreenshot:
        calibrate_screenshot(0,0,0,0,"ScreenCaps/1Calibration")
        x1 = int(input("x coin sup gauche [px]:"))
        y1 = int(input("y coin sup gauche [px]:"))
        x2 = int(input("x coin inf droit [px]:"))
        y2 = int(input("y coin inf droit [px]:"))
        return x1,y1,x2,y2
    condition = True
    while condition:
        x1 = int(input("x coin sup gauche [px]:"))
        y1 = int(input("y coin sup gauche [px]:"))
        x2 = int(input("x coin inf droit [px]:"))
        y2 = int(input("y coin inf droit [px]:"))

        calibrate_screenshot(x1,y1,x2,y2)

        if bool(int(input("Accept coordinates? : (1 = yes, 0 = no)"))):
            condition = False

    return x1,y1,x2,y2

def set_zernik_polynomial(weights):
    '''
    Arranges le slm selon le polynome de zernick associé au point
    :param weights: matrice D x 1 des poids associés aux polynomes dans un certain ordre
    :return: None
    '''
    pass


if __name__ == "__main__":
    #initialisation
    mean = [1,1,1,1,1,1,1,1,1,1]
    variances = [4,5,4,5,4,5,4,5,4,5]
    dimension = len(mean)
    number = 5

    #x1, y1, x2, y2 = 200,200,1000,700
    x1, y1, x2, y2 = set_box_inputs(JustScreenshot=True)


    test_points = generate_sequence(mean,variances, dimension, number)

    #Prise de données
    for point in range(test_points.shape[1]):

        set_zernik_polynomial(test_points[point])

        time.sleep(1) #pour que le slm change de forme
        capture_box(x1, y1, x2, y2,"image{}".format(point))
        time.sleep(0.2)

    #extraction du score
    score_list = []
    for point in range(test_points.shape[1]):
        score_list.append(round_score("ScreenCaps/image{}.jpg".format(point),"ScreenCaps_contour/image{}contour.jpg".format(point),save_calibration= True))
    np.savetxt("Score_list", score_list)
    #Fitting