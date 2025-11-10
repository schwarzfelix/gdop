"""Minimal position error plot showing position error of the first tag in each scenario, grouped by environment.

This file intentionally contains only the code required to draw a grouped bar chart
comparing the position error value for the first tag in each provided scenario,
categorized by the 6th and 7th characters of the scenario name (environment).
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal


class EnvironmentPositionErrorPlot(QObject):
    """Draw a grouped bar chart where each bar is the position error of the first tag
    in a scenario, grouped by the 6th and 7th characters of the scenario name (environment).

    Expected usage:
      plot = EnvironmentPositionErrorPlot(window, scenarios)
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
        self.ax.set_title('First-tag Position Error per Scenario (Grouped by Environment)')
        self.ax.set_ylabel('Position Error (m)')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute position error for the first tag of each scenario and update the grouped bar chart.

        Scenarios are grouped by the 6th and 7th characters of their name (environment), with bars for each scenario within groups.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        from collections import defaultdict

        group_to_scenarios = defaultdict(list)
        scenario_errors = []
        scenario_names = []

        for s in self.scenarios:
            name = getattr(s, 'name', str(s))
            if len(name) >= 7:
                group_key = name[5:7]
            elif len(name) >= 6:
                group_key = name[5:]
            else:
                group_key = 'Unknown'
            group_to_scenarios[group_key].append(s)
            
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
            scenario_errors.append(float(error))
            scenario_names.append(name)

        # Prepare grouped bar positions
        groups = sorted(group_to_scenarios.keys())
        if not groups:
            return
        
        max_per_group = max(len(group_to_scenarios[g]) for g in groups)
        width = 0.8 / max_per_group if max_per_group > 0 else 0.8
        x_positions = []
        current_x = 0
        group_centers = []
        
        for group in groups:
            group_scenarios = group_to_scenarios[group]
            group_start = current_x
            for _ in group_scenarios:
                x_positions.append(current_x)
                current_x += width
            group_centers.append((group_start + current_x - width) / 2)
            current_x += 0.2  # Space between groups

        # draw bars
        self.ax.clear()
        self.ax.bar(x_positions, scenario_errors, width=width, color='blue')
        self.ax.set_xticks(group_centers)
        self.ax.set_xticklabels(groups, rotation=90)
        self.ax.set_ylim(0, max(5, max(scenario_errors) * 1.2 if scenario_errors else 5))
        for i, v in enumerate(scenario_errors):
            self.ax.text(x_positions[i], v, f"{v:.2f}", ha='center', va='bottom', fontsize=8)

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