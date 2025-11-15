"""Minimal comparison plot showing GDOP of the first tag in each scenario.

This file intentionally contains only the code required to draw a single
bar chart comparing the dilution-of-precision (GDOP) value for the first
tag in each provided scenario.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal
from presentation.plot_colors import TAG_TRUTH_GDOP


class ComparisonPlot(QObject):
    """Draw a simple bar chart where each bar is the GDOP of the first tag
    in a scenario.

    Expected usage:
      plot = ComparisonPlot(window, scenarios)
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
        # Initial setup - will be updated in update_data()

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute GDOP for the first tag of each scenario and update the bar chart.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        scenario_names = []
        gdop_values = []

        for s in self.scenarios:
            scenario_names.append(getattr(s, 'name', str(s)))
            tags = s.get_tag_list()
            if tags and len(tags) > 0:
                try:
                    gdop = tags[0].dilution_of_precision()
                except Exception:
                    gdop = 0.0
            else:
                gdop = 0.0
            gdop_values.append(float(gdop))

        # draw bars
        self.ax.clear()
        x = range(len(scenario_names))
        self.ax.bar(x, gdop_values, color=TAG_TRUTH_GDOP, 
                   edgecolor='black', linewidth=1.5)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(scenario_names, rotation=90, ha='center')
        self.ax.set_ylim(0, max(12, max(gdop_values) * 1.2 if gdop_values else 12))
        
        # Add title and labels
        self.ax.set_title('GDOP Comparison Across Scenarios')
        self.ax.set_xlabel('Scenario')
        self.ax.set_ylabel('GDOP')
        
        # Add grid
        self.ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add value labels on bars
        for i, v in enumerate(gdop_values):
            self.ax.text(i, v, f"{v:.2f}", ha='center', va='bottom')
        
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
