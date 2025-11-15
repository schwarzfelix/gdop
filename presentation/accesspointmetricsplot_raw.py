"""Access Point metrics plot using RAW data (all CSV entries without aggregation).

This file contains the code to draw a grouped bar chart showing the average distance error
(measured distance vs. true distance) and standard deviation for each Access Point (Anchor) 
across ALL raw CSV measurements from all active scenarios WITHOUT aggregation.
This provides a comprehensive view of AP quality using all available data points.
"""

import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import pandas as pd
from collections import defaultdict
from pathlib import Path
from presentation.plot_colors import DISTANCE_ERROR, STD_DEVIATION


class AccessPointMetricsPlotRaw(QObject):
    """Draw a grouped bar chart showing average distance error and standard deviation per Access Point
    using ALL raw CSV data (not aggregated).
    
    For each anchor across all raw CSV measurements, we calculate:
    - Average distance error (measured distance - true distance)
    - Standard deviation of distance errors
    
    Expected to show 4 anchors × 2 metrics = 8 bars total.

    Expected usage:
      plot = AccessPointMetricsPlotRaw(window, scenarios)
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

        # Create figure with single plot and two y-axes
        self.fig, self.ax1 = plt.subplots(figsize=(12, 6))
        self.ax2 = self.ax1.twinx()  # Create second y-axis sharing same x-axis
        self.fig.suptitle('Access Point Quality Metrics - RAW DATA (All CSV Entries)')

    def update_data(self, anchors=False, tags=False, measurements=False):
        """Compute average distance error and standard deviation per Access Point using RAW CSV data.

        Reads all CSV files directly and uses ALL entries (no aggregation).
        Calculates distance errors using true_range(m) column if available.

        Signature accepts optional flags for compatibility with MainWindow.update_all().
        """
        from data.import_measurements import read_workspace_csvs
        
        # Collect distance errors per anchor from raw CSV data
        # anchor_name -> list of distance errors (measured - true distance)
        anchor_distance_errors = defaultdict(list)
        
        try:
            # Load all raw CSV data
            df = read_workspace_csvs(workspace_dir='workspace')
            
            if df.empty:
                self._show_no_data()
                return
            
            # Filter for scenarios that are currently active/loaded
            active_scenario_names = [getattr(s, 'name', str(s)) for s in self.scenarios]
            if active_scenario_names:
                df = df[df['scenario'].isin(active_scenario_names)]
            
            if df.empty:
                self._show_no_data()
                return
            
            # Required columns: 'ap-ssid', 'est._range(m)', 'true_range(m)'
            required_cols = ['ap-ssid', 'est._range(m)', 'true_range(m)']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                self._show_no_data(f"Missing columns: {', '.join(missing_cols)}")
                return
            
            # Clean and filter data
            valid_df = df.copy()
            valid_df['est_range'] = pd.to_numeric(valid_df['est._range(m)'], errors='coerce')
            valid_df['true_range'] = pd.to_numeric(valid_df['true_range(m)'], errors='coerce')
            
            # Remove invalid entries
            valid_df = valid_df.dropna(subset=['est_range', 'true_range'])
            valid_df = valid_df[(valid_df['est_range'] > 0) & (valid_df['true_range'] > 0)]
            
            if valid_df.empty:
                self._show_no_data("No valid measurements found")
                return
            
            # Calculate distance error for each row
            valid_df['distance_error'] = valid_df['est_range'] - valid_df['true_range']
            
            # Group by AP and collect all errors
            for ap_name, group in valid_df.groupby('ap-ssid'):
                errors = group['distance_error'].tolist()
                anchor_distance_errors[str(ap_name)].extend(errors)
            
        except Exception as e:
            self._show_no_data(f"Error loading data: {str(e)}")
            return
        
        if not anchor_distance_errors:
            self._show_no_data()
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

        # Prepare x-axis positions
        x = np.arange(len(anchor_names))
        width = 0.35
        
        # Clear both axes
        self.ax1.clear()
        self.ax2.clear()
        
        # ========== Plot bars on both axes ==========
        # Left axis (ax1): Average Distance Error
        bars_avg = self.ax1.bar(x - width/2, avg_distance_errors, width, 
                                label='Avg Distance Error', 
                                color=DISTANCE_ERROR, edgecolor='black', linewidth=1.5)
        
        # Right axis (ax2): Standard Deviation
        bars_std = self.ax2.bar(x + width/2, std_distance_errors, width,
                                label='Std Deviation',
                                color=STD_DEVIATION, edgecolor='black', linewidth=1.5)
        
        # ========== Configure left y-axis (Average Distance Error) ==========
        self.ax1.set_xlabel('Access Point')
        self.ax1.set_ylabel('Average Distance Error (m)')
        self.ax1.tick_params(axis='y')
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(anchor_names, rotation=0, ha='center')
        
        # Set y-limit for avg error (with margin, considering positive/negative)
        min_avg = min(avg_distance_errors) if avg_distance_errors else 0
        max_avg = max(avg_distance_errors) if avg_distance_errors else 3
        y_margin_avg = max(abs(max_avg), abs(min_avg)) * 0.2
        self.ax1.set_ylim(min(0, min_avg - y_margin_avg), max(3, max_avg + y_margin_avg))
        
        # Add grid and zero line
        self.ax1.grid(axis='y', alpha=0.3, linestyle='--')
        self.ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        
        # ========== Configure right y-axis (Standard Deviation) ==========
        self.ax2.set_ylabel('Standard Deviation (m)')
        self.ax2.tick_params(axis='y')
        
        # Set y-limit for std dev (always positive, start from 0)
        max_std = max(std_distance_errors) if std_distance_errors else 3
        self.ax2.set_ylim(0, max(3, max_std * 1.15))
        
        # ========== Add value labels on bars ==========
        for i, val in enumerate(avg_distance_errors):
            va = 'bottom' if val >= 0 else 'top'
            self.ax1.text(x[i] - width/2, val, f"{val:.2f}", 
                         ha='center', va=va)
        
        for i, val in enumerate(std_distance_errors):
            self.ax2.text(x[i] + width/2, val, f"{val:.2f}",
                         ha='center', va='bottom')
        
        # ========== Add combined legend ==========
        lines1, labels1 = self.ax1.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Add sample count info at the bottom of the figure
        info_text = "RAW samples per AP: " + ", ".join([f"{name}: {len(anchor_distance_errors[name])}" 
                                                         for name in anchor_names])
        self.fig.text(0.5, 0.02, info_text, ha='center')
        
        self.fig.tight_layout(rect=[0, 0.05, 1, 0.96])  # Leave space for suptitle and info text

    def _show_no_data(self, message="No data available"):
        """Helper to display a 'no data' message on the plot."""
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.text(0.5, 0.5, message, 
                     transform=self.ax1.transAxes,
                     ha='center', va='center')

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
