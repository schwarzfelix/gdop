"""Scatter plot showing GDOP vs Position Error with linear regression line and correlation statistics.

This plot helps visualize the relationship between GDOP values and actual position errors
to determine if GDOP is a good predictor of positioning accuracy.
"""

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from scipy import stats
from presentation.plot_colors import POSITION_ERROR, TAG_TRUTH_GDOP
from presentation.displayconfig import DisplayConfig


class GDOPPositionErrorScatterPlot(QObject):
    """Draw a scatter plot of GDOP vs Position Error with regression line.
    
    Shows:
    - Each scenario as a point (GDOP on x-axis, Position Error on y-axis)
    - Linear regression line
    - Correlation statistics (Pearson r, Spearman ρ, R², p-values)
    
    Expected usage:
      plot = GDOPPositionErrorScatterPlot(window, scenarios)
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
        """Collect data from scenarios and create scatter plot with regression line.

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

        # Calculate correlation statistics
        pearson_r, pearson_p = stats.pearsonr(gdop_arr, pos_err_arr)
        spearman_r, spearman_p = stats.spearmanr(gdop_arr, pos_err_arr)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(gdop_arr, pos_err_arr)
        
        # Scatter plot
        self.ax.scatter(gdop_values, pos_errors, alpha=0.6, s=120, 
                       color=TAG_TRUTH_GDOP, edgecolors='black', linewidth=1.5,
                       zorder=3)

        # Regression line
        line_x = np.array([min(gdop_values), max(gdop_values)])
        line_y = slope * line_x + intercept
        self.ax.plot(line_x, line_y, 'r--', linewidth=2.5, 
                    label=f'Linear fit: y = {slope:.3f}x + {intercept:.3f}',
                    zorder=2)

        # Labels and title
        self.ax.set_xlabel('Tag Truth GDOP', fontsize=self.display_config.fontSize_axisLabel)
        self.ax.set_ylabel('Position Error (m)', fontsize=self.display_config.fontSize_axisLabel)
        self.ax.set_title('GDOP vs Position Error Correlation Analysis', 
                         fontsize=self.display_config.fontSize_title)
        
        # Grid
        self.ax.grid(True, alpha=0.3, linestyle='--', zorder=1)

        # Legend for regression line
        self.ax.legend(fontsize=self.display_config.fontSize_legend, loc='upper left')

        # Add correlation statistics as text box
        stats_text = f'Pearson r = {pearson_r:.4f} (p = {pearson_p:.4f})\n'
        stats_text += f'Spearman ρ = {spearman_r:.4f} (p = {spearman_p:.4f})\n'
        stats_text += f'R² = {r_value**2:.4f}\n'
        stats_text += f'n = {len(gdop_values)} scenarios'
        
        # Interpretation helper
        if abs(pearson_r) < 0.3:
            interpretation = 'weak correlation'
        elif abs(pearson_r) < 0.7:
            interpretation = 'moderate correlation'
        else:
            interpretation = 'strong correlation'
        
        stats_text += f'\n({interpretation})'

        self.ax.text(0.05, 0.95, stats_text, transform=self.ax.transAxes,
                    fontsize=self.display_config.fontSize_info,
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

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
