"""Combined metrics plot showing position error, tag_truth GDOP, and tag GDOP for each scenario.

This file contains code to draw a grouped bar chart comparing three metrics
for the first tag in each provided scenario.
"""

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal


class CombinedMetricsPlot(QObject):
    """Draw a grouped bar chart where each scenario has two bars:
    - Position error of the first tag
    - GDOP at tag_truth position

    Expected usage:
      plot = CombinedMetricsPlot(window, scenarios)
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

        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.ax.set_title('Scenario Metrics: Position Error and Tag Truth GDOP')
        self.ax.set_ylabel('Value')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute metrics for the first tag of each scenario and update the grouped bar chart.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        scenario_names = []
        position_errors = []
        tag_truth_gdops = []

        for s in self.scenarios:
            scenario_names.append(getattr(s, 'name', str(s)))
            tags = s.get_tag_list()
            if tags and len(tags) > 0:
                tag = tags[0]
                try:
                    pos_error = tag.position_error()
                    if pos_error is None:
                        pos_error = 0.0
                except Exception:
                    pos_error = 0.0
                position_errors.append(float(pos_error))

                try:
                    tag_truth_gdop = s.get_tag_truth_gdop()
                except Exception:
                    tag_truth_gdop = 0.0
                tag_truth_gdops.append(float(tag_truth_gdop))
            else:
                position_errors.append(0.0)
                tag_truth_gdops.append(0.0)

        # Prepare data for grouped bars
        x = np.arange(len(scenario_names))  # the label locations
        width = 0.3  # the width of the bars (adjusted for 2 bars)

        # draw bars
        self.ax.clear()
        rects1 = self.ax.bar(x - width/2, position_errors, width, label='Position Error (m)', color='blue')
        rects2 = self.ax.bar(x + width/2, tag_truth_gdops, width, label='Tag Truth GDOP', color='orange')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(scenario_names, rotation=90)
        self.ax.legend()

        # Add value labels on bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                self.ax.annotate(f'{height:.2f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        # Set y-limits
        all_values = position_errors + tag_truth_gdops
        if all_values:
            max_val = max(all_values)
            self.ax.set_ylim(0, max(5, max_val * 1.2))

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