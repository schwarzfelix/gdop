"""Minimal comparison plot showing GDOP of the first tag in each scenario.

This file intentionally contains only the code required to draw a single
bar chart comparing the dilution-of-precision (GDOP) value for the first
tag in each provided scenario.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal


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

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title('First-tag GDOP per scenario')
        self.ax.set_ylabel('GDOP')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute GDOP for the first tag of each scenario and update the bar chart.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        scenario_names = []
        gdop_values = []

        for s in self.scenarios:
            scenario_names.append(getattr(s, 'name', lambda: 'unnamed')() if callable(getattr(s, 'name', None)) else getattr(s, 'name', str(s)))
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
        self.ax.bar(x, gdop_values, color='orange')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(scenario_names, rotation=90)
        self.ax.set_ylim(0, max(12, max(gdop_values) * 1.2 if gdop_values else 12))
        for i, v in enumerate(gdop_values):
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
