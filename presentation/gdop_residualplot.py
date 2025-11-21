"""Residual plot for GDOP vs Position Error linear regression.

This plot shows the residuals (differences between actual and predicted values)
to help identify non-linear patterns or heteroscedasticity in the relationship.
"""

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from scipy import stats
from presentation.displayconfig import DisplayConfig


class GDOPResidualPlot(QObject):
    """Draw a residual plot for GDOP vs Position Error regression.
    
    Shows:
    - Residuals (actual - predicted) on y-axis
    - GDOP values on x-axis
    - Zero line (ideal fit)
    - Helps identify non-linear patterns or outliers
    
    Expected usage:
      plot = GDOPResidualPlot(window, scenarios)
      plot.update_data()
      plot.redraw()
    """
    # class-level signals so external code can connect to them
    anchors_changed = pyqtSignal()
    tags_changed = pyqtSignal()
    measurements_changed = pyqtSignal()

    def __init__(self, window, app_scenarios):
        super().__init__()
        self.window = window
        self.scenarios = app_scenarios

        self.fig, self.ax = plt.subplots(figsize=(10, 8))

    @property
    def display_config(self):
        """Access display_config from window if available, otherwise create a default one."""
        if hasattr(self.window, 'display_config'):
            return self.window.display_config
        else:
            # Fallback for cases where window doesn't have display_config yet
            if not hasattr(self, '_display_config'):
                self._display_config = DisplayConfig()
            return self._display_config

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Collect data from scenarios and create residual plot.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        gdop_values = []
        pos_errors = []
        scenario_names = []

        for s in self.scenarios:
            scenario_name = getattr(s, 'name', str(s))
            tags = s.get_tag_list()
            if tags and len(tags) > 0:
                tag = tags[0]
                try:
                    pos_error = tag.position_error()
                    if pos_error is None:
                        continue
                except Exception:
                    continue

                try:
                    tag_truth_gdop = s.get_tag_truth_gdop()
                except Exception:
                    continue

                gdop_values.append(float(tag_truth_gdop))
                pos_errors.append(float(pos_error))
                scenario_names.append(scenario_name)

        # Clear axes
        self.ax.clear()

        if len(gdop_values) < 2:
            self.ax.text(0.5, 0.5, 'Not enough data points (need at least 2 scenarios)',
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=self.display_config.fontSize_info)
            self.fig.tight_layout()
            return

        # Convert to numpy arrays
        gdop_arr = np.array(gdop_values)
        pos_err_arr = np.array(pos_errors)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(gdop_arr, pos_err_arr)
        
        # Calculate predicted values and residuals
        predicted = slope * gdop_arr + intercept
        residuals = pos_err_arr - predicted

        # Calculate residual statistics
        residual_mean = np.mean(residuals)
        residual_std = np.std(residuals)
        
        # Scatter plot of residuals
        self.ax.scatter(gdop_values, residuals, alpha=0.6, s=120, 
                       color='steelblue', edgecolors='black', linewidth=1.5,
                       zorder=3)

        # Zero line (perfect fit)
        self.ax.axhline(y=0, color='red', linestyle='--', linewidth=2.5, 
                       label='Zero residual (perfect fit)', zorder=2)

        # Mean residual line (should be close to zero)
        if abs(residual_mean) > 0.01:  # Only show if noticeably different from zero
            self.ax.axhline(y=residual_mean, color='orange', linestyle=':', linewidth=2,
                           label=f'Mean residual: {residual_mean:.3f}', zorder=2)

        # Optional: add ±2 standard deviation lines
        self.ax.axhline(y=2*residual_std, color='gray', linestyle=':', linewidth=1.5,
                       alpha=0.5, label=f'±2σ ({2*residual_std:.3f})', zorder=1)
        self.ax.axhline(y=-2*residual_std, color='gray', linestyle=':', linewidth=1.5,
                       alpha=0.5, zorder=1)

        # Labels and title
        self.ax.set_xlabel('Tag Truth GDOP', fontsize=self.display_config.fontSize_axisLabel)
        self.ax.set_ylabel('Residuals (Actual - Predicted) [m]', fontsize=self.display_config.fontSize_axisLabel)
        self.ax.set_title('Residual Plot for GDOP vs Position Error', 
                         fontsize=self.display_config.fontSize_title)
        
        # Grid
        self.ax.grid(True, alpha=0.3, linestyle='--', zorder=0)

        # Legend
        self.ax.legend(fontsize=self.display_config.fontSize_legend, loc='best')

        # Add statistics as text box
        stats_text = f'Residual Statistics:\n'
        stats_text += f'Mean: {residual_mean:.4f} m\n'
        stats_text += f'Std Dev: {residual_std:.4f} m\n'
        stats_text += f'Min: {np.min(residuals):.4f} m\n'
        stats_text += f'Max: {np.max(residuals):.4f} m\n'
        stats_text += f'n = {len(gdop_values)} scenarios'

        # Check for patterns
        interpretation = '\n\nInterpretation:\n'
        if abs(residual_mean) < 0.1:
            interpretation += '✓ Mean ≈ 0 (unbiased)\n'
        else:
            interpretation += '⚠ Mean ≠ 0 (biased fit)\n'
        
        # Simple check for heteroscedasticity (increasing/decreasing variance)
        mid_point = len(gdop_arr) // 2
        sorted_indices = np.argsort(gdop_arr)
        first_half_var = np.var(residuals[sorted_indices[:mid_point]])
        second_half_var = np.var(residuals[sorted_indices[mid_point:]])
        
        if max(first_half_var, second_half_var) / min(first_half_var, second_half_var) > 2:
            interpretation += '⚠ Variance may increase with GDOP\n'
        else:
            interpretation += '✓ Variance appears constant\n'

        stats_text += interpretation

        self.ax.text(0.05, 0.95, stats_text, transform=self.ax.transAxes,
                    fontsize=self.display_config.fontSize_info - 1,
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

        # Apply font sizes
        self.display_config.apply_font_sizes(self.ax, self.fig)
        
        self.fig.tight_layout()

    def redraw(self):
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            pass

    def request_refresh(self, anchors=False, tags=False, measurements=False):
        """Minimal request_refresh compatible with MainWindow connect calls.

        This implementation simply emits the corresponding signal immediately.
        """
        if anchors:
            try:
                self.anchors_changed.emit()
            except Exception:
                pass
        if tags:
            try:
                self.tags_changed.emit()
            except Exception:
                pass
        if measurements:
            try:
                self.measurements_changed.emit()
            except Exception:
                pass
