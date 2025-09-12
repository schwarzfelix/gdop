import numpy as np
import logging

_LOG = logging.getLogger(__name__)

def euclidean_distances(anchor_positions, tag_position, sigma=0.0):
    distances = np.linalg.norm(anchor_positions - tag_position, axis=1)
    if sigma > 0:
        distances += np.random.normal(0, sigma, len(anchor_positions))
    return distances

def trilateration(anchor_positions, distances):
    anchor_positions = np.array(anchor_positions)
    distances = np.array(distances)
    num_anchors, dimensions = anchor_positions.shape

    if num_anchors == 1:
        direction = np.zeros(dimensions)
        direction[0] = 1  # Fixed direction
        return anchor_positions[0] + distances[0] * direction

    if num_anchors == 2 and dimensions >= 2:
        p1, p2 = anchor_positions
        r1, r2 = distances
        d = np.linalg.norm(p2 - p1)

        if d > r1 + r2 or d < abs(r1 - r2):
            _LOG.warning("The hyper-spheres do not intersect.")

        a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
        base = p1 + a * (p2 - p1) / d
        h = np.sqrt(max(r1 ** 2 - a ** 2, 0))

        # orthogonal vector
        v = (p2 - p1) / d
        if dimensions == 2:
            orth = np.array([-v[1], v[0]])
        else:
            # Gram-Schmidt with fixed vector
            fixed = np.zeros(dimensions)
            fixed[1] = 1
            orth = fixed - np.dot(fixed, v) * v
            orth /= np.linalg.norm(orth)
        return base + h * orth

    A = -2 * (anchor_positions[1:] - anchor_positions[0])
    b = distances[1:] ** 2 - distances[0] ** 2 - np.sum(anchor_positions[1:] ** 2, axis=1) + np.sum(anchor_positions[0] ** 2)

    try:
        solution = np.linalg.solve(A, b)
        return solution
    except np.linalg.LinAlgError:
        pass

    base_solution, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return base_solution

def geometry_matrix(anchor_positions, tag_position, distances=None):
    if distances is None:
        distances = euclidean_distances(anchor_positions, tag_position)
    return np.column_stack([(tag_position[i] - anchor_positions[:, i]) / distances for i in range(anchor_positions.shape[1])])

def covariance_matrix(geometry):
    return np.linalg.inv(geometry.T @ geometry)

def dilution_of_precision(anchor_positions, tag_position, distances=None):
    try:
        covariance = covariance_matrix(geometry_matrix(anchor_positions, tag_position, distances))
        return np.sqrt(np.trace(covariance))
    except np.linalg.LinAlgError:
        return np.inf

def angle_vectors(vec_u, vec_v):
    dot_product = np.dot(vec_u, vec_v)
    norm_a = np.linalg.norm(vec_u)
    norm_b = np.linalg.norm(vec_v)
    angle_rad = np.arccos(dot_product / (norm_a * norm_b))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def angle_anchors_tag(anchor_positions, tag_position):
    vec_u = anchor_positions[0] - tag_position
    vec_v = anchor_positions[1] - tag_position
    return angle_vectors(vec_u, vec_v)

def distance_between(point1, point2):
    return np.linalg.norm(point1 - point2)