'''
Exécution principale de la prise de données suivie de l'Extraction du score puis du fitting
    Trois étapes:
        1- Initialisation:
            -On initialise le point de plasma dans le montage expérimental (mean).
            -On trouve les intervalles utiles des polynomes de zernike (variances).
            -On génère la série de points à prendre en photo
            -On calibre la capture d'écran sur la fenêtre de la caméra.

        2- Prise de données:
            -On applique le polynome de zernike du premier point
            -On fait une capture d'écran du plasma
            -On répète cette étape pour tous les points

        3- Extraction du score:
            -On passe sur toutes les images générées et on en extrait le score de rondeur

        4- Fitting
            -On entraine un classifieur quelconque sur le set de données ainsi généré
'''

#Prise de données
#pip install git+https://github.com/AIworx-Labs/chocolate@master
from GenerateGaussianList import generate_sequence
from Screenshot import capture_box, calibrate_screenshot
from spotShapeDetec import round_score
import time
import numpy as np
import cliPhase as clib
import libPhase as lib

import chocolate as choco

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


def set_zernike_polynomial(weights):
    """
        Arrange le slm selon le polynome de zernike associé au point

        :param weights: ndarray: matrice D x 1 des poids associés
                        aux polynomes dans un certain ordre
        :return: None
    """
    pass


if __name__ == "__main__":
    # initialisation
    mean = [1,1,1,1,1,1,1,1,1,1]
    variances = [4,5,4,5,4,5,4,5,4,5]
    dimension = len(mean)
    number = 5

    # x1, y1, x2, y2 = 200,200,1000,700
    x1, y1, x2, y2 = set_box_inputs(JustScreenshot=True)


    test_points = generate_sequence(mean,variances, dimension, number)

    # Prise de données
    for point in range(test_points.shape[1]):

        set_zernike_polynomial(test_points[point])

        time.sleep(1) # pour que le slm change de forme
        capture_box(x1, y1, x2, y2,"image{}".format(point))


def example_run_hadoc():
    # initialisation
    mean = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    variances = [4, 5, 4, 5, 4, 5, 4, 5, 4, 5]
    dimension = len(mean)
    number = 20

    x1, y1, x2, y2 = 60, 342, 726, 725
    # x1, y1, x2, y2 = set_box_inputs(JustScreenshot=True)

    print("generating test data")
    test_points = generate_sequence(mean, variances, dimension, number)
    print("gathering data")
    # Prise de données
    print(test_points.shape)
    for point in range(test_points.shape[0]):
        set_zernike_polynomial(test_points[point])

        time.sleep(1)  # pour que le slm change de forme
        capture_box(x1, y1, x2, y2, "image{}".format(point), directory="ScreenCaps")
        time.sleep(0.2)
        print("\rprogress : {}%".format(100 * point / test_points.shape[0]), end="")

    # extraction du score
    score_list = []
    for point in range(test_points.shape[1]):
        score_list.append(round_score("ScreenCaps/image{}.jpg".format(point),"ScreenCaps_contour/image{}contour.jpg".format(point),save_calibration= True))

    print("\rextracting score")
    score_list = []
    for point in range(test_points.shape[0]):
        print("\rprogress : {}%".format(100 * point / test_points.shape[0]), end="")
        score_list.append(round_score("ScreenCaps/image{}.png".format(point), "image{}contour.png".format(point),
                                      save_calibration=True))
    np.savetxt("Score_list", score_list)
    # Fitting

def example_run_bayesian():
    # initialisation
    mean = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    variances = [4, 5, 4, 5, 4, 5, 4, 5, 4, 5]
    x1, y1, x2, y2 = 60, 342, 726, 725
    dimension = len(mean)
    number = 20
    space = {}
    for x in range(dimension):
        space["{}".format(x)] = choco.uniform(mean[x] - variances[x],mean[x] + variances[x])

    #pip install sclite3
    #sclite3 TEST.db
    conn = choco.SQLiteConnection("sqlite:///TEST.db")
    conn.lock()
    bay = choco.Bayes(conn,space, clear_db= True)
    (token,point_next) = bay.next()
    point = format_next(point_next)

    all_pos = []
    all_score = []
    for x in range(number):
        loss = extract_score(x, x1, y1, x2, y2, point)
        bay.update(token, loss)
        (token, point_next) = bay.next()
        point = format_next(point_next)
        print("\rProgress : {}%".format(100*x//number),end= "")
        all_pos.append(point)
        all_score.append(1-loss)

    np.savetxt("Score_list",all_score)
    np.savetxt("Point_list",all_pos)

    return True


def format_next(dictio):
    position_list = []

    for key in range(len(dictio.keys())) :
        position_list.append(dictio[str(key)])

    return position_list

def extract_score(number,x1,y1,x2,y2,test_point):
    '''
    Measures the score of a given point
    :param number: number of the point (for filename)
    :param x1: Int: Coordonnée x du coin supérieur gauche de la boîte à capturer [pixels]
    :param y1: Int: Coordonnée y du coin supérieur gauche de la boîte à capturer [pixels]
    :param x2: Int: Coordonnée x du coin inférieur droit de la boîte à capturer [pixels]
    :param y2: Int: Coordonnée y du coin inférieur droit de la boîte à capturer [pixels]
    :param test_point: Poids des polynomes de zernick à tester
    :return:
    '''
    set_zernike_polynomial(test_point)

    time.sleep(1)  # pour que le slm change de forme
    capture_box(x1, y1, x2, y2, "image{}".format(number), directory="ScreenCaps")
    time.sleep(0.2)
    score = round_score("ScreenCaps/image{}.png".format(number), "image{}contour.png".format(number),
                                  save_calibration=True)
    return score


if __name__ == "__main__":
    #example_run_hadoc()
    example_run_bayesian()

