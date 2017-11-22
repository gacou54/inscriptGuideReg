#! usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
import clibPhase as clib

def correctionsArray(wavelength):
    """
        function for the application of the corrections on one image.
        IMPORTANT:
            Image must be in the correct format.
                - Display 792x600
                - Grayscale format (8-bit)

        The fonction save (if saveit=True) the image in a folder named img/.
        If there is no img/ folder the function creates one.

        arguments :
            wavelength : string/int/float/etc... : wavelength used in nm (e.g. 1064)
            saveit     : Booleen : True if you want to save the image, False if
                                    you do not want to save the image

        return : list : [array of the correction pattern, correction value(multipliate it to the final value)]

    """
    LENGHT_LA = 792
    LENGHT_HA = 600

    imgCorreciton = Image.open(
        "deformation_correction_pattern/CAL_LSH0701462_{}nm.bmp".format(wavelength))

    imgCorreciton = np.asarray(list(imgCorreciton.getdata()))
    imgCorrecitonNew = np.zeros(shape=(LENGHT_HA, LENGHT_LA))

    if len(imgCorreciton) > 600:
        for i in range(LENGHT_HA):
            for j in range(LENGHT_LA):
                imgCorrecitonNew[i, j] = imgCorreciton[i * LENGHT_LA + j]

    if len(imgCorreciton) == 600:
        imgCorrecitonNew = imgCorreciton

    if len(imgCorreciton) < 600:
        raise ValueError("The image/array do not have the good format")

    # the correction depend on what wavelength you use
    wavelength_correction_dict = {
        "1100": 223,
        "1090": 222,
        "1080": 220,
        "1070": 217,
        "1064": 216,
        "1060": 215,
        "1050": 213,
        "1040": 211,
        "1030": 209,
        "1020": 207,
        "1010": 205,
        "1000": 202,
    }
    correction_factor = 0
    for key, value in wavelength_correction_dict.items():
        if key == str(wavelength):
            correction_factor = value / 255

    return [imgCorrecitonNew, correction_factor]


def gen_zernike_list(n_max):
    """
        Function that generate a list of zernike polynomials
        :param n_max: int: Determine the number of zernike polynomial to
                           in the list. It will stop creating polynomial when
                           the zernike polynomials of index n=n_max will be created 
        :return: list: list of the zernike polynomials 
    """
    z_list = []
    for n in range(n_max):
        if n//2 == 0:
            for m in range(-n, n+1):
                pass


if __name__=='__main__':
    import matplotlib.pyplot as plt
    
    array = corrections(1030)#.astype(np.uint8)
    array2 = (8 * 255*clib.czernike(2, 2))#.astype(np.uint8)

    img = Image.fromarray((array + array2).astype(np.uint8))
    img.save('test.png')

    # plt.imshow(np.uint8(array + 6*array2*255), 'gray')
    # plt.show()

