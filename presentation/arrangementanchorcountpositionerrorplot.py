"""Position error plot showing position error of the first tag in each scenario, grouped by arrangement.

This file contains the code to draw a grouped bar chart comparing the position error value
for the first tag in each provided scenario, grouped by the first character of the scenario
name (arrangement number), with 3A and 4A variants shown in different colors side by side.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal


class ArrangementAnchorCountPositionErrorPlot(QObject):
    """Draw a grouped bar chart where bars are position errors of the first tag,
    grouped by the first character of the scenario name (arrangement number),
    with 3A (blue) and 4A (orange) variants shown side by side.

    Expected usage:
      plot = ArrangementAnchorCountPositionErrorPlot(window, scenarios)
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
        self.ax.set_title('First-tag Position Error per Arrangement (3A vs 4A)')
        self.ax.set_ylabel('Position Error (m)')
        self.ax.set_xlabel('Arrangement')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute position error for the first tag of each scenario and update the grouped bar chart.

        Scenarios are grouped by the first character of their name (arrangement number),
        with 3A and 4A variants displayed in different colors.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        from collections import defaultdict

        # Group scenarios by arrangement (first character) and anchor count (3A/4A)
        arrangement_data = defaultdict(lambda: {'3A': [], '4A': []})

        for s in self.scenarios:
            name = getattr(s, 'name', str(s))
            
            # Extract arrangement number (first character)
            if len(name) >= 1:
                arrangement = name[0]
            else:
                arrangement = 'Unknown'
            
            # Determine anchor count (3A or 4A)
            anchor_count = None
            if '3A' in name.upper():
                anchor_count = '3A'
            elif '4A' in name.upper():
                anchor_count = '4A'
            
            if anchor_count is None:
                continue  # Skip scenarios without 3A or 4A designation
            
            # Get position error
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
            
            arrangement_data[arrangement][anchor_count].append(float(error))

        # Sort arrangements
        arrangements = sorted(arrangement_data.keys())
        if not arrangements:
            self.ax.clear()
            self.ax.set_title('First-tag Position Error per Arrangement (3A vs 4A)')
            self.ax.set_ylabel('Position Error (m)')
            self.ax.set_xlabel('Arrangement')
            return

        # Prepare data for plotting
        a3_values = []
        a4_values = []
        
        for arr in arrangements:
            # Average if multiple scenarios exist for same arrangement+anchor count
            a3_errors = arrangement_data[arr]['3A']
            a4_errors = arrangement_data[arr]['4A']
            
            a3_avg = sum(a3_errors) / len(a3_errors) if a3_errors else 0.0
            a4_avg = sum(a4_errors) / len(a4_errors) if a4_errors else 0.0
            
            a3_values.append(a3_avg)
            a4_values.append(a4_avg)

        # Create grouped bar chart
        x = range(len(arrangements))
        width = 0.35
        
        self.ax.clear()
        
        # Plot bars
        bars_3a = self.ax.bar([i - width/2 for i in x], a3_values, width, 
                              label='3A', color='blue', alpha=0.8)
        bars_4a = self.ax.bar([i + width/2 for i in x], a4_values, width,
                              label='4A', color='orange', alpha=0.8)
        
        # Labels and formatting
        self.ax.set_xlabel('Arrangement')
        self.ax.set_ylabel('Position Error (m)')
        self.ax.set_title('First-tag Position Error per Arrangement (3A vs 4A)')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(arrangements, rotation=45, ha='right')
        self.ax.legend()
        
        # Set y-limit with some headroom
        max_error = max(max(a3_values) if a3_values else 0, 
                       max(a4_values) if a4_values else 0)
        self.ax.set_ylim(0, max(5, max_error * 1.2))
        
        # Add value labels on bars
        for i, (a3_val, a4_val) in enumerate(zip(a3_values, a4_values)):
            if a3_val > 0:
                self.ax.text(i - width/2, a3_val, f"{a3_val:.2f}", 
                           ha='center', va='bottom', fontsize=8)
            if a4_val > 0:
                self.ax.text(i + width/2, a4_val, f"{a4_val:.2f}",
                           ha='center', va='bottom', fontsize=8)
        
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
