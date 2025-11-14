"""
Test cases for robust trilateration methods.
"""

import pytest
import numpy as np
from simulation.geometry import trilateration_robust, check_anchor_geometry


def test_trilateration_robust_with_good_geometry():
    """Test robust trilateration with well-positioned anchors."""
    # Good geometry: anchors form a large triangle
    anchors = np.array([
        [0, 0],
        [10, 0],
        [5, 10]
    ])
    
    # True position in center
    true_pos = np.array([5, 5])
    
    # Calculate distances
    distances = np.linalg.norm(anchors - true_pos, axis=1)
    
    # All methods should work well
    for method in ["classical", "best_subset", "nonlinear"]:
        pos, metadata = trilateration_robust(anchors, distances, method=method)
        error = np.linalg.norm(pos - true_pos)
        assert error < 0.1, f"Method {method} failed with good geometry: error={error}"


def test_trilateration_robust_with_collinear_anchors():
    """Test robust trilateration with collinear anchors (pathological case)."""
    # Bad geometry: 3 anchors on a line (scenario 4-4A-PD-V3)
    anchors = np.array([
        [3.50, 8.50],   # FTM_PINK
        [0.00, 11.00],  # FTM_BLUE
        [16.00, 0.00],  # FTM_GREEN
        [8.00, 5.50]    # FTM_ORANGE (on line BLUE-GREEN)
    ])
    
    true_pos = np.array([16.00, 11.00])
    
    # Measured distances (from real scenario)
    distances = np.array([12.75, 16.0, 15.0, 9.71])
    
    # Classical should fail badly
    pos_classical, metadata_classical = trilateration_robust(anchors, distances, method="classical")
    error_classical = np.linalg.norm(pos_classical - true_pos)
    assert error_classical > 30, f"Classical should fail with collinear anchors, but error={error_classical}"
    
    # Best_subset should work much better
    pos_best, metadata_best = trilateration_robust(anchors, distances, method="best_subset")
    error_best = np.linalg.norm(pos_best - true_pos)
    assert error_best < 1.0, f"Best_subset should succeed with collinear anchors, but error={error_best}"
    assert metadata_best['anchor_subset'] is not None, "Best_subset should return anchor subset"
    assert metadata_best['condition_number'] is not None, "Best_subset should return condition number"


def test_check_anchor_geometry_collinear():
    """Test geometry check detects collinear anchors."""
    # Collinear anchors
    anchors = np.array([
        [0, 0],
        [5, 5],
        [10, 10]
    ])
    
    result = check_anchor_geometry(anchors)
    assert result['is_collinear'] == True, "Should detect collinear anchors"
    assert result['min_triangle_area'] is not None
    assert result['min_triangle_area'] < 1.0, "Triangle area should be near zero"


def test_check_anchor_geometry_good():
    """Test geometry check with good anchor configuration."""
    # Good geometry
    anchors = np.array([
        [0, 0],
        [10, 0],
        [5, 10]
    ])
    
    result = check_anchor_geometry(anchors)
    assert result['min_triangle_area'] > 10.0, "Triangle area should be large"
    # May still flag as collinear if only 3 anchors, but area should be good


def test_trilateration_robust_metadata():
    """Test that metadata is returned correctly."""
    anchors = np.array([
        [0, 0],
        [10, 0],
        [5, 10],
        [5, 0]
    ])
    
    distances = np.array([5.0, 5.0, 5.0, 5.0])
    
    pos, metadata = trilateration_robust(anchors, distances, method="best_subset")
    
    assert 'method_used' in metadata
    assert 'condition_number' in metadata
    assert 'residual' in metadata
    assert 'anchor_subset' in metadata
    assert 'warnings' in metadata
    assert isinstance(metadata['warnings'], list)


if __name__ == "__main__":
    # Run tests
    test_trilateration_robust_with_good_geometry()
    print("✓ test_trilateration_robust_with_good_geometry")
    
    test_trilateration_robust_with_collinear_anchors()
    print("✓ test_trilateration_robust_with_collinear_anchors")
    
    test_check_anchor_geometry_collinear()
    print("✓ test_check_anchor_geometry_collinear")
    
    test_check_anchor_geometry_good()
    print("✓ test_check_anchor_geometry_good")
    
    test_trilateration_robust_metadata()
    print("✓ test_trilateration_robust_metadata")
    
    print("\n✅ All tests passed!")
