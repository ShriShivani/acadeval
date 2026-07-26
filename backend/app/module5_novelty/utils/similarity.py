import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(vec_a: list[float] | np.ndarray, vec_b: list[float] | np.ndarray) -> float:
    a = np.array(vec_a).reshape(1, -1)
    b = np.array(vec_b).reshape(1, -1)
    return float(cosine_similarity(a, b)[0][0])

def calculate_cosine_similarity_matrix(vec: list[float] | np.ndarray, matrix: list[list[float]] | np.ndarray) -> np.ndarray:
    v = np.array(vec).reshape(1, -1)
    m = np.array(matrix)
    if m.ndim == 1:
        m = m.reshape(1, -1)
    return cosine_similarity(v, m)[0]
