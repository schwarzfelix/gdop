"""Position error plot showing position error of the first tag in each scenario, grouped by arrangement.

This file contains the code to draw a grouped bar chart comparing the position error value
for the first tag in each provided scenario, grouped by the first 4 characters of the scenario
name (arrangement), with PD and FW variants shown in different colors side by side.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal
from presentation.plot_colors import PD_COLOR, FW_COLOR


class ArrangementPositionErrorPlot(QObject):
    """Draw a grouped bar chart where bars are position errors of the first tag,
    grouped by the first 4 characters of the scenario name (arrangement),
    with PD (blue) and FW (orange) variants shown side by side.

    Expected usage:
      plot = ArrangementPositionErrorPlot(window, scenarios)
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
        self.ax.set_title('First-tag Position Error per Arrangement (PD vs FW)')
        self.ax.set_ylabel('Position Error (m)')
        self.ax.set_xlabel('Arrangement')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute position error for the first tag of each scenario and update the grouped bar chart.

        Scenarios are grouped by the first 4 characters of their name (arrangement),
        with PD and FW variants displayed in different colors.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        from collections import defaultdict

        # Group scenarios by arrangement (first 4 chars) and variant (PD/FW)
        arrangement_data = defaultdict(lambda: {'PD': [], 'FW': []})

        for s in self.scenarios:
            name = getattr(s, 'name', str(s))
            
            # Extract arrangement (first 4 characters)
            if len(name) >= 4:
                arrangement = name[:4]
            else:
                arrangement = 'Unknown'
            
            # Determine variant (PD or FW)
            variant = None
            if 'PD' in name.upper():
                variant = 'PD'
            elif 'FW' in name.upper():
                variant = 'FW'
            
            if variant is None:
                continue  # Skip scenarios without PD or FW designation
            
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
            
            arrangement_data[arrangement][variant].append(float(error))

        # Sort arrangements
        arrangements = sorted(arrangement_data.keys())
        if not arrangements:
            self.ax.clear()
            self.ax.set_title('First-tag Position Error per Arrangement (PD vs FW)')
            self.ax.set_ylabel('Position Error (m)')
            self.ax.set_xlabel('Arrangement')
            return

        # Prepare data for plotting
        pd_values = []
        fw_values = []
        
        for arr in arrangements:
            # Average if multiple scenarios exist for same arrangement+variant
            pd_errors = arrangement_data[arr]['PD']
            fw_errors = arrangement_data[arr]['FW']
            
            pd_avg = sum(pd_errors) / len(pd_errors) if pd_errors else 0.0
            fw_avg = sum(fw_errors) / len(fw_errors) if fw_errors else 0.0
            
            pd_values.append(pd_avg)
            fw_values.append(fw_avg)

        # Create grouped bar chart
        x = range(len(arrangements))
        width = 0.35
        
        self.ax.clear()
        
        # Plot bars
        bars_pd = self.ax.bar([i - width/2 for i in x], pd_values, width, 
                              label='PD', color=PD_COLOR)
        bars_fw = self.ax.bar([i + width/2 for i in x], fw_values, width,
                              label='FW', color=FW_COLOR)
        
        # Labels and formatting
        self.ax.set_xlabel('Arrangement')
        self.ax.set_ylabel('Position Error (m)')
        self.ax.set_title('First-tag Position Error per Arrangement (PD vs FW)')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(arrangements, rotation=45, ha='right')
        self.ax.legend()
        
        # Set y-limit with some headroom
        max_error = max(max(pd_values) if pd_values else 0, 
                       max(fw_values) if fw_values else 0)
        self.ax.set_ylim(0, max(5, max_error * 1.2))
        
        # Add value labels on bars
        for i, (pd_val, fw_val) in enumerate(zip(pd_values, fw_values)):
            if pd_val > 0:
                self.ax.text(i - width/2, pd_val, f"{pd_val:.2f}", 
                           ha='center', va='bottom')
            if fw_val > 0:
                self.ax.text(i + width/2, fw_val, f"{fw_val:.2f}",
                           ha='center', va='bottom')
        
        # Add sample count info
        total_scenarios = sum(len(arrangement_data[arr]['PD']) + len(arrangement_data[arr]['FW']) 
                            for arr in arrangements)
        self.fig.text(0.5, 0.02, f'Total scenarios: {total_scenarios}', ha='center')
        
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
