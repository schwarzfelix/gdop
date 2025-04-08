import numpy as np

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
        direction = np.random.randn(dimensions)
        direction /= np.linalg.norm(direction)
        return anchor_positions[0] + distances[0] * direction

    if num_anchors == 2 and dimensions >= 2:
        p1, p2 = anchor_positions
        r1, r2 = distances
        d = np.linalg.norm(p2 - p1)

        if d > r1 + r2 or d < abs(r1 - r2):
            raise ValueError("The hyper-spheres do not intersect.")

        a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
        base = p1 + a * (p2 - p1) / d
        h = np.sqrt(max(r1 ** 2 - a ** 2, 0))

        random_vec = np.random.randn(dimensions)
        random_vec -= np.dot(random_vec, (p2 - p1)) * (p2 - p1) / d ** 2
        random_vec /= np.linalg.norm(random_vec)
        return base + h * random_vec

    A = -2 * (anchor_positions[1:] - anchor_positions[0])
    b = distances[1:] ** 2 - distances[0] ** 2 - np.sum(anchor_positions[1:] ** 2, axis=1) + np.sum(
        anchor_positions[0] ** 2)

    try:
        solution = np.linalg.solve(A, b)
        return solution
    except np.linalg.LinAlgError:
        pass

    base_solution, _, _, singular_vectors = np.linalg.lstsq(A, b, rcond=None)
    null_space_basis = singular_vectors[A.shape[0]:]

    if null_space_basis.size == 0:
        return base_solution

    random_combination = np.random.randn(null_space_basis.shape[0])
    random_solution = base_solution + null_space_basis.T @ random_combination
    return random_solution

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