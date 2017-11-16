import numpy as np

def generate_sequence(mean, variances, dimensions, number):

    initial_values = np.zeros((dimensions, number))
    for x in range(dimensions):
        initial_values[x] = np.random.normal(mean,variances[x],number)

    return initial_values

if __name__ == "__main__":
    variances = range(0,100)
    test_sequence = generate_sequence(100,variances,100,1000)
    import matplotlib.pyplot as plt
    plt.plot(test_sequence[6],test_sequence[5],'.')
    plt.plot(test_sequence[60],test_sequence[50],'.')
    plt.plot(test_sequence[90],test_sequence[91],'.')
    plt.show()

