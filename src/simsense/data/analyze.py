import matplotlib.pyplot as plt
import numpy as np


def calculate_mr(data):
    avk = data.avk[0:41, 0:41]
    return np.array([np.sum(row) for row in avk])


def calculate_residual(data):
    y = data.y
    yf = data.yf
    return np.array(y - yf)
