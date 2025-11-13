import numpy as np
import logging
from typing import Optional, Union

_LOG = logging.getLogger(__name__)

def euclidean_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        point1: First point (array-like).
        point2: Second point (array-like).

    Returns:
        Distance as a float.
    """
    return np.linalg.norm(np.array(point1) - np.array(point2))

def euclidean_distances(anchor_positions: np.ndarray, tag_position: np.ndarray, sigma: float = 0.0) -> np.ndarray:
    """
    Calculate Euclidean distances from anchors to tag position, optionally with noise.

    Args:
        anchor_positions: Array of anchor positions (shape: num_anchors x dimensions).
        tag_position: Tag position (shape: dimensions).
        sigma: Standard deviation for Gaussian noise (default: 0.0).

    Returns:
        Array of distances (shape: num_anchors).
    """
    distances = np.linalg.norm(anchor_positions - tag_position, axis=1)
    if sigma > 0:
        distances += np.random.normal(0, sigma, len(anchor_positions))
    return distances

def trilateration(anchor_positions: Union[list, np.ndarray], distances: Union[list, np.ndarray]) -> np.ndarray:
    """
    Estimate tag position using trilateration.

    Args:
        anchor_positions: List or array of anchor positions.
        distances: Measured distances to anchors.

    Returns:
        Estimated tag position.
    """
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
        d = euclidean_distance(p2, p1)

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
            norm_orth = np.linalg.norm(orth)
            if norm_orth > 0:
                orth /= norm_orth
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

def geometry_matrix(anchor_positions: np.ndarray, tag_position: np.ndarray, distances: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Compute the geometry matrix (Jacobian of distance functions).

    Args:
        anchor_positions: Anchor positions.
        tag_position: Tag position.
        distances: Precomputed distances (optional).

    Returns:
        Geometry matrix G.
    """
    if distances is None:
        distances = euclidean_distances(anchor_positions, tag_position)
    # Avoid division by zero by replacing 0 with 1 (safe fallback)
    safe_distances = np.where(distances == 0, 1, distances)
    return np.column_stack([(tag_position[i] - anchor_positions[:, i]) / safe_distances for i in range(anchor_positions.shape[1])])

def covariance_matrix(geometry: np.ndarray) -> np.ndarray:
    """
    Compute the covariance matrix from geometry matrix.

    Args:
        geometry: Geometry matrix G.

    Returns:
        Covariance matrix.
    """
    return np.linalg.inv(geometry.T @ geometry)

def dilution_of_precision(anchor_positions: np.ndarray, tag_position: np.ndarray, distances: Optional[np.ndarray] = None) -> float:
    """
    Calculate Geometric Dilution of Precision (GDOP).

    Args:
        anchor_positions: Anchor positions.
        tag_position: Tag position.
        distances: Precomputed distances (optional).

    Returns:
        GDOP value (inf if singular).
    """
    try:
        covariance = covariance_matrix(geometry_matrix(anchor_positions, tag_position, distances))
        return np.sqrt(np.trace(covariance))
    except np.linalg.LinAlgError:
        return np.inf

def angle_vectors(vec_u: np.ndarray, vec_v: np.ndarray) -> float:
    """
    Calculate angle between two vectors in degrees.

    Args:
        vec_u, vec_v: Input vectors.

    Returns:
        Angle in degrees.
    """
    dot_product = np.dot(vec_u, vec_v)
    norm_a = euclidean_distance(vec_u, np.zeros_like(vec_u))
    norm_b = euclidean_distance(vec_v, np.zeros_like(vec_v))
    angle_rad = np.arccos(dot_product / (norm_a * norm_b))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def angle_anchors_tag(anchor_positions: np.ndarray, tag_position: np.ndarray) -> float:
    """
    Calculate angle at tag between first two anchors.

    Args:
        anchor_positions: Anchor positions.
        tag_position: Tag position.

    Returns:
        Angle in degrees.
    """
    vec_u = anchor_positions[0] - tag_position
    vec_v = anchor_positions[1] - tag_position
    return angle_vectors(vec_u, vec_v)

def distance_between(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        point1, point2: Points.

    Returns:
        Distance.
    """
    return euclidean_distance(point1, point2)