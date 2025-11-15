"""Combined metrics line plot showing position error and tag truth GDOP as lines over scenarios, sorted by tag truth GDOP.

This file contains code to draw a line plot comparing position error and tag truth GDOP
across scenarios sorted by their tag truth GDOP values.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal
from presentation.plot_colors import POSITION_ERROR, TAG_TRUTH_GDOP


class CombinedMetricsLinePlotSorted(QObject):
    """Draw a line plot where each metric is shown as a line across scenarios:
    - Position error of the first tag
    - GDOP at tag_truth position

    Scenarios are sorted by tag truth GDOP ascending.

    Expected usage:
      plot = CombinedMetricsLinePlotSorted(window, scenarios)
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

        self.fig, self.ax1 = plt.subplots(figsize=(10, 6))
        self.ax2 = self.ax1.twinx()  # Create second y-axis for GDOP
        # Title and labels will be set in update_data()

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute metrics for the first tag of each scenario, sort by tag truth GDOP, and update the line plot.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        scenario_data = []

        for s in self.scenarios:
            scenario_name = getattr(s, 'name', str(s))
            tags = s.get_tag_list()
            if tags and len(tags) > 0:
                tag = tags[0]
                try:
                    pos_error = tag.position_error()
                    if pos_error is None:
                        pos_error = 0.0
                except Exception:
                    pos_error = 0.0

                try:
                    tag_truth_gdop = s.get_tag_truth_gdop()
                except Exception:
                    tag_truth_gdop = 0.0

                scenario_data.append({
                    'name': scenario_name,
                    'position_error': float(pos_error),
                    'tag_truth_gdop': float(tag_truth_gdop)
                })
            else:
                scenario_data.append({
                    'name': scenario_name,
                    'position_error': 0.0,
                    'tag_truth_gdop': 0.0
                })

        # Sort by tag truth GDOP (rounded to 2 decimals) ascending, then by position error ascending
        # This ensures that scenarios with visually identical GDOP are sorted by position error
        scenario_data.sort(key=lambda x: (round(float(x['tag_truth_gdop']), 2), float(x['position_error'])))

        # Extract sorted data
        scenario_names = [d['name'] for d in scenario_data]
        position_errors = [d['position_error'] for d in scenario_data]
        tag_truth_gdops = [d['tag_truth_gdop'] for d in scenario_data]

        # Clear both axes
        self.ax1.clear()
        self.ax2.clear()
        x = range(len(scenario_names))

        # Set zorder for axes to control layering
        self.ax1.set_zorder(2)  # Position Error axis in front
        self.ax2.set_zorder(1)  # GDOP axis in back
        
        # Make ax1 background transparent so ax2 is visible
        self.ax1.patch.set_visible(False)

        # Plot tag truth GDOP line on right axis
        line2 = self.ax2.plot(x, tag_truth_gdops, 's-', label='Tag Truth GDOP', 
                             color=TAG_TRUTH_GDOP, linewidth=3, markersize=8)

        # Plot position error line on left axis (will be in front due to ax1 zorder)
        line1 = self.ax1.plot(x, position_errors, 'o-', label='Position Error', 
                             color=POSITION_ERROR, linewidth=3, markersize=8)

        # Set title and labels
        self.ax1.set_title('Scenario Metrics Trends (Sorted by Tag Truth GDOP)')
        self.ax1.set_xlabel('Scenario (sorted by Tag Truth GDOP)')
        self.ax1.set_ylabel('Position Error (m)')
        self.ax2.set_ylabel('GDOP')
        self.ax2.yaxis.set_label_position('right')
        
        # Set ticks and formatting
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(scenario_names, rotation=90, ha='center')
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        self.ax1.legend(lines, labels, loc='upper left', fontsize=display_config.fontSize_legend)
        
        self.ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

        # Set y-limits with some padding for each axis independently
        if position_errors:
            min_pe = min(position_errors)
            max_pe = max(position_errors)
            padding_pe = (max_pe - min_pe) * 0.15 if max_pe != min_pe else 1.0
            self.ax1.set_ylim(max(0, min_pe - padding_pe), max_pe + padding_pe)
        
        if tag_truth_gdops:
            min_gdop = min(tag_truth_gdops)
            max_gdop = max(tag_truth_gdops)
            padding_gdop = (max_gdop - min_gdop) * 0.15 if max_gdop != min_gdop else 1.0
            self.ax2.set_ylim(max(0, min_gdop - padding_gdop), max_gdop + padding_gdop)
        
        # Apply font sizes to axes
        from presentation.displayconfig import DisplayConfig
        display_config = DisplayConfig()
        display_config.apply_font_sizes(self.ax1, self.fig)
        self.ax2.yaxis.label.set_fontsize(display_config.fontSize_axisLabel)
        self.ax2.tick_params(axis='y', labelsize=display_config.fontSize_tickLabel)
        
        # Add sample count info
        n_scenarios = len(scenario_names)
        self.fig.text(0.5, 0.02, f'Number of scenarios: {n_scenarios}', ha='center',
                     fontsize=display_config.fontSize_info)
        
        self.fig.tight_layout(rect=[0, 0.05, 1, 1])  # Leave space for info text

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