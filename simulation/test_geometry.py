import numpy as np
import pytest
from simulation.geometry import (
    euclidean_distance,
    euclidean_distances,
    trilateration,
    geometry_matrix,
    covariance_matrix,
    dilution_of_precision,
    angle_vectors,
    angle_anchors_tag,
    distance_between,
)


class TestEuclideanDistance:
    """Tests for the singular euclidean_distance function."""
    
    def test_basic_2d(self):
        p1 = np.array([0, 0])
        p2 = np.array([3, 4])
        dist = euclidean_distance(p1, p2)
        assert np.isclose(dist, 5.0)
    
    def test_basic_3d(self):
        p1 = np.array([0, 0, 0])
        p2 = np.array([1, 1, 1])
        dist = euclidean_distance(p1, p2)
        assert np.isclose(dist, np.sqrt(3))
    
    def test_same_point(self):
        p1 = np.array([1, 2, 3])
        p2 = np.array([1, 2, 3])
        dist = euclidean_distance(p1, p2)
        assert dist == 0.0
    
    def test_negative_coordinates(self):
        p1 = np.array([-1, -2])
        p2 = np.array([2, 2])
        dist = euclidean_distance(p1, p2)
        expected = np.sqrt(3**2 + 4**2)
        assert np.isclose(dist, expected)
    
    def test_1d(self):
        p1 = np.array([0])
        p2 = np.array([5])
        dist = euclidean_distance(p1, p2)
        assert dist == 5.0
    
    def test_list_input(self):
        """Test that function works with list inputs (converted to arrays)."""
        p1 = [0, 0]
        p2 = [3, 4]
        dist = euclidean_distance(p1, p2)
        assert np.isclose(dist, 5.0)
    
    def test_float_coordinates(self):
        p1 = np.array([1.5, 2.5])
        p2 = np.array([4.5, 6.5])
        dist = euclidean_distance(p1, p2)
        expected = np.sqrt(3**2 + 4**2)
        assert np.isclose(dist, expected)
    
    def test_large_dimension(self):
        """Test with higher dimensional space."""
        p1 = np.array([1, 2, 3, 4, 5])
        p2 = np.array([1, 2, 3, 4, 5])
        dist = euclidean_distance(p1, p2)
        assert dist == 0.0
    
    def test_large_distance(self):
        p1 = np.array([0, 0])
        p2 = np.array([1000, 1000])
        dist = euclidean_distance(p1, p2)
        expected = np.sqrt(1000**2 + 1000**2)
        assert np.isclose(dist, expected)


class TestEuclideanDistances:
    def test_basic_2d(self):
        anchors = np.array([[0, 0], [1, 0]])
        tag = np.array([0, 1])
        distances = euclidean_distances(anchors, tag)
        expected = np.array([1.0, np.sqrt(2)])
        np.testing.assert_array_almost_equal(distances, expected)

    def test_with_noise(self):
        anchors = np.array([[0, 0]])
        tag = np.array([1, 0])
        np.random.seed(42)  # For reproducibility
        distances = euclidean_distances(anchors, tag, sigma=0.1)
        assert len(distances) == 1
        assert distances[0] > 0.9  # Approximate, since noise is added

    def test_3d(self):
        anchors = np.array([[0, 0, 0]])
        tag = np.array([1, 1, 1])
        distances = euclidean_distances(anchors, tag)
        expected = np.sqrt(3)
        assert np.isclose(distances[0], expected)


class TestTrilateration:
    def test_one_anchor_2d(self):
        anchors = [[0, 0]]
        distances = [1.0]
        result = trilateration(anchors, distances)
        expected = np.array([1.0, 0.0])  # Along x-axis
        np.testing.assert_array_almost_equal(result, expected)

    def test_one_anchor_3d(self):
        anchors = [[0, 0, 0]]
        distances = [2.0]
        result = trilateration(anchors, distances)
        expected = np.array([2.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_two_anchors_intersecting_2d(self):
        anchors = [[0, 0], [2, 0]]
        distances = [1.0, 1.0]
        result = trilateration(anchors, distances)
        expected = np.array([1.0, 0.0])  # Midpoint
        np.testing.assert_array_almost_equal(result, expected)

    def test_two_anchors_non_intersecting_2d(self):
        anchors = [[0, 0], [1, 0]]
        distances = [0.5, 0.5]  # Too small to intersect
        result = trilateration(anchors, distances)
        # Should still return a position, even if warning is logged
        assert result.shape == (2,)

    def test_two_anchors_3d(self):
        anchors = [[0, 0, 0], [2, 0, 0]]
        distances = [1.0, 1.0]
        result = trilateration(anchors, distances)
        expected = np.array([1.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_three_anchors_exact_2d(self):
        anchors = [[0, 0], [2, 0], [1, 2]]
        tag = [1, 1]
        distances = euclidean_distances(np.array(anchors), np.array(tag))
        result = trilateration(anchors, distances)
        np.testing.assert_array_almost_equal(result, tag, decimal=5)

    def test_four_anchors_overdetermined_2d(self):
        anchors = [[0, 0], [2, 0], [0, 2], [2, 2]]
        tag = [1, 1]
        distances = euclidean_distances(np.array(anchors), np.array(tag))
        result = trilateration(anchors, distances)
        np.testing.assert_array_almost_equal(result, tag, decimal=3)  # Allow some tolerance

    def test_collinear_anchors_singular(self):
        anchors = [[0, 0], [1, 0], [2, 0]]  # Collinear
        distances = [1.0, 1.0, 1.0]
        result = trilateration(anchors, distances)
        # Should still return something, possibly least squares
        assert result.shape == (2,)

    def test_negative_distances(self):
        anchors = [[0, 0], [1, 0]]
        distances = [-1.0, 1.0]  # Invalid, but test robustness
        result = trilateration(anchors, distances)
        assert result.shape == (2,)


class TestGeometryMatrix:
    def test_basic_2d(self):
        anchors = np.array([[0, 0], [1, 0]])
        tag = np.array([0, 1])
        G = geometry_matrix(anchors, tag)
        expected = np.array([
            [0 / 1, 1 / 1],  # For anchor 0: (tag - anchor)/dist
            [-1 / np.sqrt(2), 1 / np.sqrt(2)]  # For anchor 1
        ])
        np.testing.assert_array_almost_equal(G, expected)

    def test_with_provided_distances(self):
        anchors = np.array([[0, 0]])
        tag = np.array([1, 0])
        distances = [1.0]
        G = geometry_matrix(anchors, tag, distances)
        expected = np.array([[1.0, 0.0]])
        np.testing.assert_array_almost_equal(G, expected)


class TestCovarianceMatrix:
    def test_basic(self):
        G = np.array([[1, 0], [0, 1]])
        cov = covariance_matrix(G)
        expected = np.eye(2)  # Inverse of G^T G = I
        np.testing.assert_array_almost_equal(cov, expected)

    def test_singular(self):
        G = np.array([[1, 0], [1, 0]])  # Rank deficient
        with pytest.raises(np.linalg.LinAlgError):
            covariance_matrix(G)


class TestDilutionOfPrecision:
    def test_normal_case_2d(self):
        anchors = np.array([[0, 0], [2, 0], [0, 2]])
        tag = np.array([1, 1])
        gdop = dilution_of_precision(anchors, tag)
        assert isinstance(gdop, float)
        assert gdop > 0

    def test_singular_geometry(self):
        anchors = np.array([[0, 0], [2, 0]])  # Collinear with tag on the line
        tag = np.array([1, 0])
        gdop = dilution_of_precision(anchors, tag)
        assert gdop == np.inf

    def test_with_distances(self):
        anchors = np.array([[0, 0], [1, 0]])
        tag = np.array([0, 1])
        distances = [1.0, np.sqrt(2)]
        gdop = dilution_of_precision(anchors, tag, distances)
        assert isinstance(gdop, float)


class TestAngleVectors:
    def test_perpendicular(self):
        u = np.array([1, 0])
        v = np.array([0, 1])
        angle = angle_vectors(u, v)
        assert np.isclose(angle, 90.0)

    def test_parallel(self):
        u = np.array([1, 0])
        v = np.array([1, 0])
        angle = angle_vectors(u, v)
        assert np.isclose(angle, 0.0)

    def test_opposite(self):
        u = np.array([1, 0])
        v = np.array([-1, 0])
        angle = angle_vectors(u, v)
        assert np.isclose(angle, 180.0)


class TestAngleAnchorsTag:
    def test_basic(self):
        anchors = np.array([[0, 0], [1, 0]])
        tag = np.array([0.5, 1])
        angle = angle_anchors_tag(anchors, tag)
        assert isinstance(angle, float)
        assert 0 <= angle <= 180


class TestDistanceBetween:
    def test_basic(self):
        p1 = np.array([0, 0])
        p2 = np.array([1, 1])
        dist = distance_between(p1, p2)
        expected = np.sqrt(2)
        assert np.isclose(dist, expected)

    def test_same_point(self):
        p1 = np.array([1, 1])
        p2 = np.array([1, 1])
        dist = distance_between(p1, p2)
        assert dist == 0.0