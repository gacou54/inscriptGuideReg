import numpy as np

def generate_sequence(mean, variances, dimensions, number):
    '''
    On génère une gaussienne centrée sur un point en D dimensions contenant
    N points avec une variance prédéterminée pour chaque dimension
    :param mean: Matrice D x 1 contenant les coordonés du centre de la gaussienne
    :param variances: Matrice D x 1 contenant les variances de chaque dimension
    :param dimensions: Int : nombre de dimensions (D)
    :param number: Int : nombre de points dans la gaussienne (N)
    :return: initial_values : matrice D x N contenant une gaussienne centrée sur mean
    '''

    initial_values = np.zeros((dimensions, number))
    for x in range(dimensions):
        initial_values[x] = np.random.normal(mean[x],variances[x],number)

    return initial_values.transpose()

if __name__ == "__main__":
    variances = range(0,100)
    test_sequence = generate_sequence(100,variances,100,1000)
    import matplotlib.pyplot as plt
    plt.plot(test_sequence[6],test_sequence[5],'.')
    plt.plot(test_sequence[60],test_sequence[50],'.')
    plt.plot(test_sequence[90],test_sequence[91],'.')
    plt.show()

