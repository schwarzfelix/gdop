import numpy as np
import logging
from typing import Optional, Union, Tuple
from itertools import combinations

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


def trilateration_robust(
    anchor_positions: Union[list, np.ndarray], 
    distances: Union[list, np.ndarray],
    method: str = "best_subset",
    condition_threshold: float = 100.0
) -> Tuple[np.ndarray, dict]:
    """
    Robust trilateration that handles poor anchor geometry.
    
    This method addresses the problem where classical least-squares trilateration
    can produce physically impossible results (e.g., positions hundreds of meters
    away when all measurements are < 20m) when anchors have poor geometry
    (e.g., 3+ anchors collinear).
    
    Strategy:
    - "best_subset": Find the best 3-anchor subset by condition number (recommended)
    - "nonlinear": Use nonlinear least-squares with centroid start (requires scipy)
    - "classical": Fall back to classical method (may fail on poor geometry)
    
    Args:
        anchor_positions: Array of anchor positions (Nx2 or Nx3)
        distances: Measured distances to anchors
        method: Strategy to use ("best_subset", "nonlinear", or "classical")
        condition_threshold: Maximum acceptable condition number (default: 100)
    
    Returns:
        Tuple of (estimated_position, metadata_dict)
        metadata contains: method_used, condition_number, residual, anchor_subset, warnings
    """
    anchor_positions = np.array(anchor_positions)
    distances = np.array(distances)
    num_anchors, dimensions = anchor_positions.shape
    
    metadata = {
        'method_used': method,
        'condition_number': None,
        'residual': None,
        'anchor_subset': None,
        'warnings': []
    }
    
    # For 3 or fewer anchors, use classical method
    if num_anchors <= 3:
        solution = trilateration(anchor_positions, distances)
        metadata['method_used'] = 'classical_3_or_less'
        return solution, metadata
    
    # Method 1: Find best 3-anchor subset
    if method == "best_subset":
        best_solution = None
        best_condition = float('inf')
        best_combo = None
        best_residual = float('inf')
        
        for combo in combinations(range(num_anchors), 3):
            anchors_subset = anchor_positions[list(combo)]
            distances_subset = distances[list(combo)]
            
            # Compute condition number
            A = -2 * (anchors_subset[1:] - anchors_subset[0])
            
            try:
                cond = np.linalg.cond(A)
                
                # Skip if poorly conditioned
                if cond > condition_threshold:
                    continue
                
                # Solve trilateration
                b = (distances_subset[1:]**2 - distances_subset[0]**2 - 
                     np.sum(anchors_subset[1:]**2, axis=1) + np.sum(anchors_subset[0]**2))
                sol = np.linalg.solve(A, b)
                
                # Compute residual: how well does this solution fit ALL measurements?
                reconstructed_distances = np.linalg.norm(anchor_positions - sol, axis=1)
                residual = np.sqrt(np.sum((distances - reconstructed_distances)**2))
                
                # Update best if this is better
                if residual < best_residual:
                    best_solution = sol
                    best_condition = cond
                    best_combo = combo
                    best_residual = residual
                    
            except np.linalg.LinAlgError:
                # Singular matrix, skip this combination
                continue
        
        if best_solution is not None:
            metadata['condition_number'] = best_condition
            metadata['residual'] = best_residual
            metadata['anchor_subset'] = best_combo
            
            if best_condition > 50:
                metadata['warnings'].append(
                    f"High condition number ({best_condition:.1f}) indicates poor geometry"
                )
            
            _LOG.debug(f"Best 3-anchor subset: {best_combo}, condition={best_condition:.1f}, "
                      f"residual={best_residual:.2f}m")
            return best_solution, metadata
        else:
            metadata['warnings'].append("No well-conditioned 3-anchor subset found")
            _LOG.warning("All 3-anchor combinations are poorly conditioned or singular")
            # Fall through to nonlinear method
            method = "nonlinear"
    
    # Method 2: Nonlinear least-squares
    if method == "nonlinear":
        try:
            from scipy.optimize import least_squares
            
            def residuals_function(pos, anchors, measured_dist):
                """Compute residuals: measured - calculated distances"""
                calculated = np.linalg.norm(anchors - pos, axis=1)
                return measured_dist - calculated
            
            # Start from centroid of anchors
            x0 = np.mean(anchor_positions, axis=0)
            
            result = least_squares(
                residuals_function, 
                x0, 
                args=(anchor_positions, distances),
                loss='soft_l1'  # Robust to outliers
            )
            
            solution = result.x
            metadata['method_used'] = 'nonlinear_lstsq'
            metadata['residual'] = np.linalg.norm(result.fun)
            
            _LOG.debug(f"Nonlinear least-squares: residual={metadata['residual']:.2f}m")
            return solution, metadata
            
        except ImportError:
            _LOG.warning("scipy not available, falling back to classical method")
            method = "classical"
    
    # Method 3: Classical (may fail on poor geometry)
    if method == "classical":
        solution = trilateration(anchor_positions, distances)
        
        # Check if solution is plausible
        reconstructed = np.linalg.norm(anchor_positions - solution, axis=1)
        max_error = np.max(np.abs(reconstructed - distances))
        
        if max_error > 2 * np.max(distances):
            metadata['warnings'].append(
                f"Classical solution may be unreliable (max error {max_error:.1f}m)"
            )
        
        metadata['method_used'] = 'classical'
        metadata['residual'] = np.sqrt(np.sum((distances - reconstructed)**2))
        
        return solution, metadata
    
    # Should not reach here
    raise ValueError(f"Unknown method: {method}")


def check_anchor_geometry(anchor_positions: np.ndarray, collinearity_threshold: float = 1.0) -> dict:
    """
    Analyze anchor geometry to identify potential trilateration issues.
    
    Args:
        anchor_positions: Nx2 or Nx3 array of anchor positions
        collinearity_threshold: Area threshold below which anchors are considered collinear (default: 1.0)
    
    Returns:
        Dictionary with geometry metrics:
        - is_collinear: bool, if 3+ anchors are nearly collinear
        - min_triangle_area: smallest triangle area (for 2D)
        - condition_numbers: condition numbers for all 3-anchor subsets
        - recommendations: list of warning strings
    """
    num_anchors = len(anchor_positions)
    
    result = {
        'is_collinear': False,
        'min_triangle_area': None,
        'condition_numbers': [],
        'recommendations': []
    }
    
    if num_anchors < 3:
        result['recommendations'].append("Need at least 3 anchors for trilateration")
        return result
    
    # Check triangle areas (for 2D)
    if anchor_positions.shape[1] == 2:
        min_area = float('inf')
        
        for combo in combinations(range(num_anchors), 3):
            p1, p2, p3 = [anchor_positions[i] for i in combo]
            v1 = p2 - p1
            v2 = p3 - p1
            area = 0.5 * abs(v1[0] * v2[1] - v1[1] * v2[0])
            
            if area < min_area:
                min_area = area
            
            if area < collinearity_threshold:
                result['is_collinear'] = True
                result['recommendations'].append(
                    f"Anchors {combo} are nearly collinear (area={area:.2f})"
                )
        
        result['min_triangle_area'] = min_area
        
        if min_area < 5.0:
            result['recommendations'].append(
                "Consider repositioning anchors to form larger triangles"
            )
    
    # Check condition numbers
    for combo in combinations(range(num_anchors), 3):
        anchors_subset = anchor_positions[list(combo)]
        A = -2 * (anchors_subset[1:] - anchors_subset[0])
        
        try:
            cond = np.linalg.cond(A)
            result['condition_numbers'].append({
                'subset': combo,
                'condition': cond
            })
            
            if cond > 100:
                result['recommendations'].append(
                    f"Subset {combo} has high condition number ({cond:.1f})"
                )
        except:
            result['recommendations'].append(f"Subset {combo} is singular")
    
    return result
