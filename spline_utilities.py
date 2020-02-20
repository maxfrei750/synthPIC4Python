import warnings

import numpy as np
import pandas as pd
from scipy import integrate, interpolate
from scipy.integrate.quadrature import AccuracyWarning


def _remove_duplicate_vertices(vertices):
    return pd.DataFrame(data=vertices).drop_duplicates().to_numpy()


def _prepare_spline_interpolation(vertices):
    vertices = _remove_duplicate_vertices(vertices)

    num_vertices = len(vertices)

    if num_vertices < 2:
        return None

    if num_vertices < 4:
        spline_degree = 1
    else:
        spline_degree = 3

    tck, _ = interpolate.splprep(vertices.T, s=0, k=spline_degree)

    return tck


def calculate_spline_length(vertices):
    tck = _prepare_spline_interpolation(vertices)

    if tck is None:
        return 0

    def length_function(u):
        derivatives = interpolate.splev(u, tck, der=1)
        derivatives = np.array(derivatives)
        return np.sqrt(np.sum(derivatives ** 2))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", AccuracyWarning)
        length = integrate.romberg(length_function, 0, 1)

    return length
