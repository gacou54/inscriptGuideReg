#! usr/bin/python3
# -*- coding: utf-8 -*-
# author : Gabriel Couture
"""
    Automatisation of the shape detection of
    the generated plasma
"""

import numpy as np
from PIL import Image
from skimage import filters
from skimage.segmentation import active_contour
from scipy import signal as sig



# kernel_test = np.array([[0, 1, 0], [1, -4, 1], [0, -1, 0]])

kernel_test = np.array([[1, 2, 1], [1, -4, 1], [1, -2, 1]])


def round_score(file_name, target_file_name, save_calibration = False):
    """
        the function takes an images and try to
        quantify the roundness of the photo generated
        plasma

        arguments:
            file_name        : string | name of the file
            target_file_name : string | result file's name

        return:
            float | roundness score of the generated plasma
    """
    try:
        img = Image.open(file_name).convert('L')
    except:
        raise NameError("The script failed to open the image")

    # (width, height) = img.size
    img_arr = np.asarray(img).copy()  # copy to avoid working on the original data
    img_arrN = img_arr/255

    # finding the maximum value of the array
    max_value_of_array = 0
    for i in img_arrN:
        if max(i) > max_value_of_array:
            max_value_of_array = max(i)


    # renormalization with the maximum value
    for i in range(len(img_arrN)):
        for j in range(len(img_arrN[0])):
            img_arrN[i, j] = img_arrN[i, j] / max_value_of_array


    # we applied some filters
    img_arrN = filters.gaussian(img_arrN, 2)
    img_arrN = abs(sig.convolve(img_arrN, kernel_test))


    # contrast
    img_arrN = np.int8(img_arrN)


    # countour detecting
    crit = 0.02
    ct = np.zeros(shape=img_arrN.shape)
    for i in range(len(img_arrN) - 1):
        for j in range(len(img_arrN[0]) - 1):
            if abs(img_arrN[i+1, j] - img_arrN[i, j]) > crit:
                ct[i, j] = 1
            if abs(img_arrN[i, j+1] - img_arrN[i, j]) > crit:
                ct[i, j] = 1

    #find the true center
    idx_h = np.sum(ct,axis=0)
    idx_v = np.sum(ct,axis=1)
    count = 0
    total_h = 0
    for x in idx_h:
        count += 1
        if x != 0:
            total_h += count
    center_x = total_h/np.count_nonzero(idx_h)
    total_v = 0
    count = 0
    for x in idx_v:
        count += 1
        if x != 0:
            total_v += count
    center_y = total_v/np.count_nonzero(idx_v)
    center = [center_y,center_x]

    # calculate the mean radius and the score
    radius = []
    for i in range(len(ct)):
        for j in range(len(ct[0])):
            if ct[i, j] == 1:
                radius.append(np.sqrt((i - center[0])**2 + (j - center[1])**2))

    radius_mean = np.mean(radius)
    # radius /= radius_mean
    score = 0
    for i in radius:
        score += abs(i - radius_mean)/radius_mean

    #print(score/len(radius))

    # getting the cercle with the radius_mean as the radius
    # for i in range(len(ct)):
    #     for j in range(len(ct[0])):
    #         if ct[i, j] != 1:
    #             if np.sqrt((i-center[0])**2 + (j-center[1])**2) <= radius_mean:
    #                 ct[i, j] = 1
      

    img_gs = Image.fromarray(np.uint8(ct)*255)
    img_gs.save(target_file_name)

    if save_calibration:
        calibration_visualisation(radius_mean,center,img_arrN.shape,ct,target_file_name)

    return score

def calibration_visualisation(radius, center, image_shape, contour, filename):
    '''
    Affiches la figure de contour ainsi que le centre et le cercle sur lequel les
    calculs de score sont effectués.
    :param radius: Rayon du cercle du calcul de score
    :param center: Centre du cercle du calcul de score
    :param image_shape: Hauteur et largeur de l'image
    :param contour: Contour trouvé précédemment
    :return: None
    '''

    ct = np.zeros(shape=image_shape)

    for x in range(image_shape[0]):
        for y in range(image_shape[1]):
            #dessine la croix du centre
            if (x < center[0] + radius//4 and x > center[0] - radius//4 and y < int(center[1]) + 2 and y > int(center[1]) - 2) \
                or (y < center[1] + radius//4 and y > center[1] - radius//4 and x < int(center[0])+ 2 and x > int(center[0]) - 2):
                ct[x][y] = 1
            #dessine le cercle de calibration
            if (x-center[0])**2 + (y-center[1])**2 < (radius + 1)**2 and (x-center[0])**2 + (y-center[1])**2 > (radius-1)**2:
                ct[x][y] = 1

    #superpose la bitmap et montre
    total = ct+contour
    for x in range(total.shape[0]):
        for y in range(total.shape[1]):
            if total[x][y] != 0:
                total[x][y] = 255
    #Image.fromarray(total).save("ScreenCaps_contour/Calibration/")
    return None

if __name__ == "__main__":
    names_list = [["imgTest/spot_silice_1.jpg", "imgTest/img_test_silice_1.png"],
                   # ["imgTest/spot_BGG_1.png", "imgTest/img_test_BGG_1.png"],
                   # ["imgTest/spot_BGG_2.png", "imgTest/img_test_BGG_2.png"], 
                   ["imgTest/spot_BGG_3.png", "imgTest/img_test_BGG_3.png"], 
                   # ["imgTest/spot_BGG_4.png", "imgTest/img_test_BGG_4.png"], 
                   ["imgTest/spot_BGG_5.png", "imgTest/img_test_BGG_5.png"]]
        
    for name in names_list:
        round_score(name[0], name[1])

