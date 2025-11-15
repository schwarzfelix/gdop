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

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
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

        # Clear and plot lines
        self.ax.clear()
        x = range(len(scenario_names))

        # Plot position error line
        self.ax.plot(x, position_errors, 'o-', label='Position Error (m)', color=POSITION_ERROR, linewidth=2, markersize=6)

        # Plot tag truth GDOP line
        self.ax.plot(x, tag_truth_gdops, 's-', label='Tag Truth GDOP', color=TAG_TRUTH_GDOP, linewidth=2, markersize=6)

        # Set title and labels
        self.ax.set_title('Scenario Metrics Trends (Sorted by Tag Truth GDOP)')
        self.ax.set_xlabel('Scenario (sorted by Tag Truth GDOP)')
        self.ax.set_ylabel('Value')
        
        # Set ticks and formatting
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(scenario_names, rotation=45, ha='right')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        # Add value labels at each point
        for i, (pe, gdop) in enumerate(zip(position_errors, tag_truth_gdops)):
            self.ax.annotate(f'{pe:.2f}', (x[i], pe), textcoords="offset points", xytext=(0,10), ha='center')
            self.ax.annotate(f'{gdop:.2f}', (x[i], gdop), textcoords="offset points", xytext=(0,-15), ha='center')

        # Set y-limits with some padding
        all_values = position_errors + tag_truth_gdops
        if all_values:
            min_val = min(all_values)
            max_val = max(all_values)
            padding = (max_val - min_val) * 0.1 if max_val != min_val else 1.0
            self.ax.set_ylim(max(0, min_val - padding), max_val + padding)
        
        # Add sample count info
        n_scenarios = len(scenario_names)
        self.fig.text(0.5, 0.02, f'Number of scenarios: {n_scenarios}', ha='center')
        
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