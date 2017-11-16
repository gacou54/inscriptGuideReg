# -*- coding:utf-8 -*-
import numpy as np
cimport numpy as np
from cython cimport floating
from libcpp cimport bool
from libc.math cimport sqrt, pow, atan, M_PI, sin, cos, abs

"""
    Authors : Gabriel Couture
              Charles Fortier
    Date    : 2017-11-15

    Library of functions for the generation of images for the LCOS-SLM device.
    The applied images on the SLM screen changes the shape of the wavefront by
    changin the phase on each pixel.

    The value on the Grayscale image (8-bit encoding) goes to 0 to 255.
    A value of 0 on a pixel means that this one will changes the phase of the
    beam by 0*pi
    A value of 255 on a pixel means that this one will changes the phase of the
    beam by 2*pi
        (e.g. If you want to change de phase by pi/2 you must enter
            a value of int(255/4))

"""

DTYPE = np.float
ctypedef np.float_t DTYPE_t
    
cdef int LENGTH_LA = 792
cdef int LENGTH_HA = 600
 

cdef int cfactorial(int n):
    if (n == 0):
        return 1
    return n * cfactorial(n-1)


cdef double czernike_xy(int n, int m, int x, int y):
    # Function to generate a value form a Zernike polynom at a (x.y) position
    cdef int LENGTH_LA = 792
    cdef int LENGTH_HA = 600
    cdef int xo = 396
    cdef int yo = 300
    cdef int R_MAX = 300
    cdef double rho = sqrt( (x-xo)**2 + (y-yo)**2  )  / R_MAX
    cdef double phi
    cdef double num = 0
    cdef double deno = 0
    cdef double R = 0
    cdef int m_neg = 0
    if x == xo and y - yo < 0:
        phi = M_PI * 3.0 / 2.0
    elif x == xo and y - yo > 0:
        phi = M_PI * 1.0 / 2.0
    elif x == xo and y == yo:
        phi = 0.0
    elif (x - xo < 0):  # Quadrant 2 et 3
        phi = np.arctan(float(y - yo) / float(x - xo)) + M_PI
    else:
        phi = np.arctan(float(y - yo) / (x - xo))
    if m < 0:
        m_neg =  1
        m = -m
    for k in range( int( (n-m)/2 + 1 ) ):
        num = (-1)**k * cfactorial(n - k) * rho**(n - 2 * k)
        deno = cfactorial(k) * cfactorial((n + m) / 2 - k) * cfactorial((n - m) / 2 - k)
        R += (num / deno)
    cdef double val = 0
    if m == 0:
        val = -R  # Le - est pour qu'à la valeur nulle le déphasage soit de 0 pi
    elif n % 2 == 0:
        if m_neg == 1:
            # Le - est pour qu'à la valeur nulle le déphasage soit de 0 pi
            val = -R * sin(m * phi)
        else:
            # Le - est pour qu'à la valeur nulle le déphasage soit de 0 pi
            val = -R * cos(m * phi)
    elif n % 2 == 1:
        if m_neg == 1:
            # Le - est pour qu'à la valeur nulle le déphasage soit de 0
            val = -R * sin(m * phi)
        else:
            # Le - est pour qu'à la valeur nulle le déphasage soit de 0 pi
            val = R * cos(m * phi)
    return ( val + 1 ) / 2



def czernike(int n, int m):
    cdef np.ndarray[DTYPE_t, ndim=2] array = np.zeros(shape=(LENGTH_HA, LENGTH_LA))
    cdef int i
    cdef int j
    for i in range(LENGTH_HA):
        for j in range(LENGTH_LA):
            array[i, j] = czernike_xy(n , m, j, i)

    return array



