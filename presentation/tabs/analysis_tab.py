"""
Analysis tab for the GDOP application.
Shows a list of available plots and analysis options that can be opened in separate windows.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel
from .base_tab import BaseTab
from presentation.comparisonplot_window import ComparisonPlotWindow
from presentation.multi_trilatplot_window import MultiTrilatPlotWindow
from presentation.arrangementpositionerrorplot_window import ArrangementPositionErrorPlotWindow
from presentation.accesspointmetricsplot_raw_window import AccessPointMetricsPlotRawWindow
from presentation.combinedmetricslineplot_sorted_window import CombinedMetricsLinePlotSortedWindow

class AnalysisTab(BaseTab):
    """Tab for analysis options and plots that can be opened in separate windows."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.analysis_list = None

    @property
    def tab_name(self):
        return "Analysis"

    def create_widget(self):
        """Create and return the analysis tab widget."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Header
        header = QLabel("Click on an analysis option to open it in a new window:")
        layout.addWidget(header)

        # List of available analyses
        self.analysis_list = QListWidget()
        self.analysis_list.itemDoubleClicked.connect(self._open_analysis)

        # Add available analysis options
        self._add_analysis_options()

        layout.addWidget(self.analysis_list)
        widget.setLayout(layout)

        return widget

    def _add_analysis_options(self):
        """Add available analysis options to the list."""
        # Comparison Plot
        comparison_item = QListWidgetItem("📊 Comparison Plot - GDOP per Scenario")
        comparison_item.setToolTip("Open a bar chart showing GDOP values for the first tag in each scenario")
        comparison_item.setData(1, "comparison_plot")  # Store identifier
        self.analysis_list.addItem(comparison_item)

        # Multi-Scenario Trilateration Plot
        multi_trilat_item = QListWidgetItem("📈 Multi-Scenario Trilateration Plot")
        multi_trilat_item.setToolTip("Open a plot showing all loaded scenarios simultaneously in subplots")
        multi_trilat_item.setData(1, "multi_trilat_plot")  # Store identifier
        self.analysis_list.addItem(multi_trilat_item)

        # Arrangement Position Error Plot
        arrangement_position_error_item = QListWidgetItem("📊 Arrangement Position Error Plot - PD vs FW (Grouped by Arrangement)")
        arrangement_position_error_item.setToolTip("Open a grouped bar chart showing position error values for PD and FW variants side by side, grouped by the first 4 characters of the scenario name (arrangement)")
        arrangement_position_error_item.setData(1, "arrangement_position_error_plot")  # Store identifier
        self.analysis_list.addItem(arrangement_position_error_item)

        # Access Point Metrics Plot (RAW DATA)
        access_point_metrics_raw_item = QListWidgetItem("📊 Access Point Quality Metrics - RAW DATA (All CSV Entries)")
        access_point_metrics_raw_item.setToolTip("Open a grouped bar chart showing average distance error and standard deviation for each Access Point using ALL raw CSV measurements (no aggregation)")
        access_point_metrics_raw_item.setData(1, "access_point_metrics_plot_raw")  # Store identifier
        self.analysis_list.addItem(access_point_metrics_raw_item)

        # Combined Metrics Line Plot (Sorted)
        combined_metrics_line_sorted_item = QListWidgetItem("📈 Combined Metrics Line Plot (Sorted) - Position Error and Tag Truth GDOP Trends")
        combined_metrics_line_sorted_item.setToolTip("Open a line plot showing trends of position error and tag truth GDOP across scenarios sorted by tag truth GDOP")
        combined_metrics_line_sorted_item.setData(1, "combined_metrics_line_plot_sorted")  # Store identifier
        self.analysis_list.addItem(combined_metrics_line_sorted_item)

    def _open_analysis(self, item):
        """Open the selected analysis in a new window."""
        analysis_type = item.data(1)

        if analysis_type == "comparison_plot":
            self._open_comparison_plot()
        elif analysis_type == "multi_trilat_plot":
            self._open_multi_trilat_plot()
        elif analysis_type == "arrangement_position_error_plot":
            self._open_arrangement_position_error_plot()
        elif analysis_type == "access_point_metrics_plot_raw":
            self._open_access_point_metrics_plot_raw()
        elif analysis_type == "combined_metrics_line_plot_sorted":
            self._open_combined_metrics_line_plot_sorted()
        else:
            # Unknown analysis type
            pass

    def _open_comparison_plot(self):
        """Open the comparison plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = ComparisonPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Comparison Plot: {str(e)}")

    def _open_multi_trilat_plot(self):
        """Open the multi-scenario trilateration plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = MultiTrilatPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Multi-Scenario Trilateration Plot: {str(e)}")

    def _open_arrangement_position_error_plot(self):
        """Open the arrangement position error plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = ArrangementPositionErrorPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Arrangement Position Error Plot: {str(e)}")

    def _open_access_point_metrics_plot_raw(self):
        """Open the Access Point quality metrics plot (raw data) in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = AccessPointMetricsPlotRawWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Access Point Metrics Plot (Raw Data): {str(e)}")

    def _open_combined_metrics_line_plot_sorted(self):
        """Open the combined metrics line plot (sorted) in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = CombinedMetricsLinePlotSortedWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Combined Metrics Line Plot (Sorted): {str(e)}")

    def update(self):
        """Update the analysis tab if needed."""
        # For now, no dynamic updates needed
        pass