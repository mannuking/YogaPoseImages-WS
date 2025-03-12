import numpy as np

def rx_detector(hsi_cube):
    # Reshape the HSI cube into a 2D matrix (pixels x bands)
    rows, cols, bands = hsi_cube.shape
    X = hsi_cube.reshape(rows * cols, bands)

    # Calculate mean vector and covariance matrix
    mean_vector = np.mean(X, axis=0)
    cov_matrix = np.cov(X, rowvar=False)

    # Calculate the inverse of the covariance matrix
    cov_inv = np.linalg.inv(cov_matrix)

    # Initialize the RX score matrix
    rx_scores = np.zeros(rows * cols)

    # Calculate the Mahalanobis distance for each pixel
    for i in range(rows * cols):
        diff = X[i] - mean_vector
        rx_scores[i] = np.dot(np.dot(diff, cov_inv), diff.T)

    # Reshape the result back to the original image dimensions
    rx_scores = rx_scores.reshape(rows, cols)
    return rx_scores
