"""Access Point metrics plot showing average distance error and standard deviation per AP.

This file contains the code to draw a grouped bar chart showing the average distance error
(measured distance vs. true distance) and standard deviation for each Access Point (Anchor) 
across all active scenarios. This helps identify if any anchor points are measuring 
significantly worse than others.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from collections import defaultdict


class AccessPointMetricsPlot(QObject):
    """Draw a grouped bar chart showing average distance error and standard deviation per Access Point.
    
    For each anchor across all scenarios, we calculate:
    - Average distance error (measured distance - true distance)
    - Standard deviation of distance errors
    
    Expected to show 4 anchors × 2 metrics = 8 bars total.

    Expected usage:
      plot = AccessPointMetricsPlot(window, scenarios)
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
        self.ax.set_title('Access Point Quality Metrics (Avg Distance Error & Std Dev)')
        self.ax.set_ylabel('Distance Error (m)')
        self.ax.set_xlabel('Access Point')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute average distance error and standard deviation per Access Point.

        Goes through all scenarios and collects distance errors (measured - true) for each
        anchor-tag pair. Then calculates statistics per anchor.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        # Collect distance errors per anchor
        # anchor_name -> list of distance errors (measured - true distance)
        anchor_distance_errors = defaultdict(list)

        for scenario in self.scenarios:
            # Get all anchors and tags in this scenario
            anchors = scenario.get_anchor_list() if hasattr(scenario, 'get_anchor_list') else []
            tags = scenario.get_tag_list() if hasattr(scenario, 'get_tag_list') else []
            
            # For each tag, calculate distance errors for each anchor
            for tag in tags:
                try:
                    # Get tag's true position (if available via tag_truth)
                    if not hasattr(scenario, 'tag_truth') or scenario.tag_truth is None:
                        continue
                    
                    tag_true_position = scenario.tag_truth.position()
                    
                    # Find measurements for this tag
                    if hasattr(scenario, 'measurements') and scenario.measurements:
                        tag_relations = scenario.measurements.find_relation_single(tag)
                        
                        # For each anchor-tag measurement
                        for pair, measured_distance in tag_relations:
                            # Extract the anchor from the pair
                            partner = next(iter(pair - {tag}), None)
                            if partner is not None and hasattr(partner, 'name'):
                                from simulation.station import Anchor
                                if isinstance(partner, Anchor):
                                    # Calculate true distance (anchor to tag_truth)
                                    anchor_position = partner.position()
                                    from simulation import geometry
                                    true_distance = geometry.distance_between(anchor_position, tag_true_position)
                                    
                                    # Calculate distance error (measured - true)
                                    distance_error = measured_distance - true_distance
                                    anchor_distance_errors[partner.name].append(float(distance_error))
                except Exception as e:
                    # Skip tags that cause errors
                    continue

        if not anchor_distance_errors:
            self.ax.clear()
            self.ax.set_title('Access Point Quality Metrics (Avg Distance Error & Std Dev)')
            self.ax.set_ylabel('Distance Error (m)')
            self.ax.set_xlabel('Access Point')
            self.ax.text(0.5, 0.5, 'No data available', 
                        transform=self.ax.transAxes,
                        ha='center', va='center', fontsize=12)
            return

        # Sort anchors by name for consistent ordering
        anchor_names = sorted(anchor_distance_errors.keys())
        
        # Calculate statistics
        avg_distance_errors = []
        std_distance_errors = []
        
        for anchor_name in anchor_names:
            errors = anchor_distance_errors[anchor_name]
            avg_distance_errors.append(np.mean(errors))
            std_distance_errors.append(np.std(errors))

        # Create grouped bar chart
        x = np.arange(len(anchor_names))
        width = 0.35
        
        self.ax.clear()
        
        # Plot bars
        bars_avg = self.ax.bar(x - width/2, avg_distance_errors, width, 
                              label='Avg Distance Error', color='steelblue', alpha=0.8)
        bars_std = self.ax.bar(x + width/2, std_distance_errors, width,
                              label='Std Deviation', color='coral', alpha=0.8)
        
        # Labels and formatting
        self.ax.set_xlabel('Access Point', fontsize=11)
        self.ax.set_ylabel('Distance Error (m)', fontsize=11)
        self.ax.set_title('Access Point Quality Metrics (Avg Distance Error & Std Dev)', fontsize=12)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(anchor_names, rotation=45, ha='right')
        self.ax.legend()
        
        # Set y-limit with some headroom (considering both positive and negative errors)
        all_values = avg_distance_errors + std_distance_errors
        max_value = max(all_values) if all_values else 3
        min_value = min(avg_distance_errors) if avg_distance_errors else 0
        y_margin = max(abs(max_value), abs(min_value)) * 0.2
        self.ax.set_ylim(min(0, min_value - y_margin), max(3, max_value + y_margin))
        
        # Add a horizontal line at y=0 for reference
        self.ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        
        # Add value labels on bars
        for i, (avg_val, std_val) in enumerate(zip(avg_distance_errors, std_distance_errors)):
            # For average, place label above or below depending on sign
            va_avg = 'bottom' if avg_val >= 0 else 'top'
            self.ax.text(x[i] - width/2, avg_val, f"{avg_val:.2f}", 
                       ha='center', va=va_avg, fontsize=8)
            # Std dev is always positive, place above
            self.ax.text(x[i] + width/2, std_val, f"{std_val:.2f}",
                       ha='center', va='bottom', fontsize=8)
        
        # Add sample count info
        info_text = f"Total samples per AP: " + ", ".join([f"{name}: {len(anchor_distance_errors[name])}" 
                                                            for name in anchor_names])
        self.ax.text(0.5, -0.25, info_text, 
                    transform=self.ax.transAxes,
                    ha='center', va='top', fontsize=8, style='italic')
        
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
