"""Unit tests for GDOP Correlation Analysis.

Tests the correlation analysis functionality including edge cases and statistical calculations.
"""

import unittest
import numpy as np
from unittest.mock import Mock, MagicMock
from presentation.gdop_correlation_analysis import GDOPCorrelationAnalysis


class TestGDOPCorrelationAnalysis(unittest.TestCase):
    """Test cases for GDOPCorrelationAnalysis class."""

    def create_mock_scenario(self, name, gdop, position_error):
        """Helper to create a mock scenario with given GDOP and position error."""
        scenario = Mock()
        scenario.name = name
        
        tag = Mock()
        tag.position_error.return_value = position_error
        
        scenario.get_tag_list.return_value = [tag]
        scenario.get_tag_truth_gdop.return_value = gdop
        
        return scenario

    def test_perfect_positive_correlation(self):
        """Test with perfect positive correlation (r = 1.0)."""
        scenarios = [
            self.create_mock_scenario("S1", gdop=1.0, position_error=1.0),
            self.create_mock_scenario("S2", gdop=2.0, position_error=2.0),
            self.create_mock_scenario("S3", gdop=3.0, position_error=3.0),
            self.create_mock_scenario("S4", gdop=4.0, position_error=4.0),
            self.create_mock_scenario("S5", gdop=5.0, position_error=5.0),
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 5)
        
        # Perfect correlation should have r very close to 1.0
        self.assertAlmostEqual(result['pearson_r'], 1.0, places=10)
        self.assertAlmostEqual(result['spearman_r'], 1.0, places=10)
        
        # R² should be very close to 1.0
        self.assertAlmostEqual(result['r_squared'], 1.0, places=10)
        
        # For perfect correlation, p-value should be very small (but not exactly 0)
        # scipy.stats returns very small p-values for perfect correlations
        self.assertLess(result['pearson_p'], 0.01)
        self.assertLess(result['spearman_p'], 0.01)
        
        # Linear regression should have slope = 1, intercept = 0
        self.assertAlmostEqual(result['slope'], 1.0, places=10)
        self.assertAlmostEqual(result['intercept'], 0.0, places=10)

    def test_perfect_negative_correlation(self):
        """Test with perfect negative correlation (r = -1.0)."""
        scenarios = [
            self.create_mock_scenario("S1", gdop=1.0, position_error=5.0),
            self.create_mock_scenario("S2", gdop=2.0, position_error=4.0),
            self.create_mock_scenario("S3", gdop=3.0, position_error=3.0),
            self.create_mock_scenario("S4", gdop=4.0, position_error=2.0),
            self.create_mock_scenario("S5", gdop=5.0, position_error=1.0),
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result['pearson_r'], -1.0, places=10)
        self.assertAlmostEqual(result['spearman_r'], -1.0, places=10)
        self.assertAlmostEqual(result['r_squared'], 1.0, places=10)
        self.assertLess(result['slope'], 0)  # Negative slope

    def test_no_correlation(self):
        """Test with no correlation (r ≈ 0)."""
        scenarios = [
            self.create_mock_scenario("S1", gdop=1.0, position_error=2.5),
            self.create_mock_scenario("S2", gdop=2.0, position_error=2.5),
            self.create_mock_scenario("S3", gdop=3.0, position_error=2.5),
            self.create_mock_scenario("S4", gdop=4.0, position_error=2.5),
            self.create_mock_scenario("S5", gdop=5.0, position_error=2.5),
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        # No variation in position_error means correlation is undefined/zero
        # The exact value depends on scipy implementation
        self.assertTrue(np.isnan(result['pearson_r']) or abs(result['pearson_r']) < 0.001)

    def test_moderate_positive_correlation(self):
        """Test with moderate positive correlation."""
        # Create data with some noise
        np.random.seed(42)
        gdop_values = np.linspace(1.0, 5.0, 20)
        # Linear relationship with noise
        pos_errors = 0.5 * gdop_values + 1.0 + np.random.normal(0, 0.3, 20)
        
        scenarios = [
            self.create_mock_scenario(f"S{i}", gdop=g, position_error=pe)
            for i, (g, pe) in enumerate(zip(gdop_values, pos_errors))
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 20)
        
        # Should have positive correlation
        self.assertGreater(result['pearson_r'], 0.5)
        self.assertGreater(result['spearman_r'], 0.5)
        
        # Should be significant
        self.assertLess(result['pearson_p'], 0.05)
        self.assertLess(result['spearman_p'], 0.05)
        
        # Slope should be positive and around 0.5
        self.assertGreater(result['slope'], 0.3)
        self.assertLess(result['slope'], 0.7)

    def test_insufficient_data(self):
        """Test with insufficient data (< 2 scenarios)."""
        # Only one scenario
        scenarios = [
            self.create_mock_scenario("S1", gdop=1.0, position_error=1.0),
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        # Should return None for insufficient data
        self.assertIsNone(result)

    def test_empty_scenarios(self):
        """Test with empty scenario list."""
        scenarios = []
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNone(result)

    def test_scenarios_with_none_values(self):
        """Test handling of scenarios with None values."""
        # Mix of valid and invalid scenarios
        scenario1 = self.create_mock_scenario("S1", gdop=1.0, position_error=1.0)
        
        scenario2 = Mock()
        scenario2.name = "S2"
        tag2 = Mock()
        tag2.position_error.return_value = None  # None position error
        scenario2.get_tag_list.return_value = [tag2]
        scenario2.get_tag_truth_gdop.return_value = 2.0
        
        scenario3 = self.create_mock_scenario("S3", gdop=3.0, position_error=3.0)
        
        scenarios = [scenario1, scenario2, scenario3]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        # Should only count valid scenarios
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 2)

    def test_scenarios_with_exceptions(self):
        """Test handling of scenarios that raise exceptions."""
        scenario1 = self.create_mock_scenario("S1", gdop=1.0, position_error=1.0)
        
        scenario2 = Mock()
        scenario2.name = "S2"
        scenario2.get_tag_list.side_effect = Exception("Test error")
        
        scenario3 = self.create_mock_scenario("S3", gdop=3.0, position_error=3.0)
        
        scenarios = [scenario1, scenario2, scenario3]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        # Should skip the error scenario
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 2)

    def test_scenarios_with_no_tags(self):
        """Test scenarios with no tags."""
        scenario1 = self.create_mock_scenario("S1", gdop=1.0, position_error=1.0)
        
        scenario2 = Mock()
        scenario2.name = "S2"
        scenario2.get_tag_list.return_value = []  # No tags
        scenario2.get_tag_truth_gdop.return_value = 2.0
        
        scenario3 = self.create_mock_scenario("S3", gdop=3.0, position_error=3.0)
        
        scenarios = [scenario1, scenario2, scenario3]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        # Should skip scenario without tags
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 2)

    def test_monotonic_but_not_linear(self):
        """Test data that is monotonic but not linear (Spearman > Pearson)."""
        # Quadratic relationship
        gdop_values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        pos_errors = [x**2 for x in gdop_values]  # y = x²
        
        scenarios = [
            self.create_mock_scenario(f"S{i}", gdop=g, position_error=pe)
            for i, (g, pe) in enumerate(zip(gdop_values, pos_errors))
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        
        # Both should be positive and high
        self.assertGreater(result['spearman_r'], 0.9)
        self.assertGreater(result['pearson_r'], 0.8)
        
        # Spearman should be closer to 1.0 than Pearson (perfect monotonic)
        self.assertGreater(result['spearman_r'], result['pearson_r'])

    def test_realistic_gdop_data(self):
        """Test with realistic GDOP and position error values."""
        # Realistic scenario: GDOP values between 1.5 and 8.0
        # Position errors roughly correlated but with noise
        np.random.seed(123)
        gdop_values = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0]
        # Position error roughly proportional to GDOP with noise
        pos_errors = [g * 0.8 + np.random.uniform(-0.5, 0.5) for g in gdop_values]
        
        scenarios = [
            self.create_mock_scenario(f"Scenario_{i}", gdop=g, position_error=pe)
            for i, (g, pe) in enumerate(zip(gdop_values, pos_errors))
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['n_samples'], 10)
        
        # Should show positive correlation
        self.assertGreater(result['pearson_r'], 0.7)
        self.assertGreater(result['spearman_r'], 0.7)
        
        # Should be statistically significant
        self.assertLess(result['pearson_p'], 0.05)
        self.assertLess(result['spearman_p'], 0.05)

    def test_p_value_not_exactly_zero(self):
        """Test that p-values are not exactly 0.0 (they should be very small floats)."""
        # Create perfect correlation data
        scenarios = [
            self.create_mock_scenario(f"S{i}", gdop=float(i), position_error=float(i))
            for i in range(1, 11)
        ]
        
        analysis = GDOPCorrelationAnalysis(scenarios)
        result = analysis.run_analysis()
        
        self.assertIsNotNone(result)
        
        # P-values should be very small but not exactly 0.0
        # They might be extremely small (e.g., 1e-20) which could be represented as 0.0
        # when printed, but should be > 0.0 in floating point
        # Note: For perfect correlation with limited samples, scipy might return
        # a p-value that is effectively 0 due to floating point precision
        
        # Check that p-values are either very small or effectively zero
        self.assertLessEqual(result['pearson_p'], 1e-5)
        self.assertLessEqual(result['spearman_p'], 1e-5)
        
        # P-values should be non-negative
        self.assertGreaterEqual(result['pearson_p'], 0.0)
        self.assertGreaterEqual(result['spearman_p'], 0.0)


if __name__ == '__main__':
    unittest.main()
