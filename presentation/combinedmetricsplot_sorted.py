"""Combined metrics plot showing position error and tag truth GDOP for each scenario, sorted by tag truth GDOP.

This file contains code to draw a grouped bar chart comparing position error and tag truth GDOP
for scenarios sorted by their tag truth GDOP values.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal


class CombinedMetricsPlotSorted(QObject):
    """Draw a grouped bar chart where each scenario has two bars:
    - Position error of the first tag
    - GDOP at tag_truth position

    Scenarios are sorted by tag truth GDOP ascending.

    Expected usage:
      plot = CombinedMetricsPlotSorted(window, scenarios)
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
        self.ax.set_title('Scenario Metrics (Sorted by Tag Truth GDOP): Position Error and Tag Truth GDOP')
        self.ax.set_ylabel('Value')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute metrics for the first tag of each scenario, sort by tag truth GDOP, and update the grouped bar chart.

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

        # Sort by tag truth GDOP ascending
        scenario_data.sort(key=lambda x: x['tag_truth_gdop'])

        # Extract sorted data
        scenario_names = [d['name'] for d in scenario_data]
        position_errors = [d['position_error'] for d in scenario_data]
        tag_truth_gdops = [d['tag_truth_gdop'] for d in scenario_data]

        # Prepare data for grouped bars
        x = range(len(scenario_names))  # the label locations
        width = 0.3  # the width of the bars

        # draw bars
        self.ax.clear()
        rects1 = self.ax.bar(x, position_errors, width, label='Position Error (m)', color='blue')
        rects2 = self.ax.bar([i + width for i in x], tag_truth_gdops, width, label='Tag Truth GDOP', color='orange')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        self.ax.set_xticks([i + width/2 for i in x])
        self.ax.set_xticklabels(scenario_names, rotation=45, ha='right')
        self.ax.legend()

        # Add value labels on bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                self.ax.annotate(f'{height:.2f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)

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