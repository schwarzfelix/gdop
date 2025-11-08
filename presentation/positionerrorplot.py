"""Minimal position error plot showing position error of the first tag in each scenario.

This file intentionally contains only the code required to draw a single
bar chart comparing the position error value for the first
tag in each provided scenario.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal


class PositionErrorPlot(QObject):
    """Draw a simple bar chart where each bar is the position error of the first tag
    in a scenario.

    Expected usage:
      plot = PositionErrorPlot(window, scenarios)
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

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title('First-tag Position Error per scenario')
        self.ax.set_ylabel('Position Error (m)')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute position error for the first tag of each scenario and update the bar chart.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        scenario_names = []
        error_values = []

        for s in self.scenarios:
            scenario_names.append(getattr(s, 'name', str(s)))
            tags = s.get_tag_list()
            if tags and len(tags) > 0:
                try:
                    error = tags[0].position_error()
                    if error is None:
                        error = 0.0
                except Exception:
                    error = 0.0
            else:
                error = 0.0
            error_values.append(float(error))

        # draw bars
        self.ax.clear()
        x = range(len(scenario_names))
        self.ax.bar(x, error_values, color='blue')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(scenario_names, rotation=90)
        self.ax.set_ylim(0, max(5, max(error_values) * 1.2 if error_values else 5))
        for i, v in enumerate(error_values):
            self.ax.text(i, v, f"{v:.2f}", ha='center', va='bottom')

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