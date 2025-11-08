"""
Analysis tab for the GDOP application.
Shows a list of available plots and analysis options that can be opened in separate windows.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel
from .base_tab import BaseTab
from presentation.comparisonplot_window import ComparisonPlotWindow
from presentation.multi_trilatplot_window import MultiTrilatPlotWindow
from presentation.positionerrorplot_window import PositionErrorPlotWindow
from presentation.combinedmetricsplot_window import CombinedMetricsPlotWindow

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

        # Position Error Plot
        position_error_item = QListWidgetItem("📊 Position Error Plot - Position Error per Scenario")
        position_error_item.setToolTip("Open a bar chart showing position error values for the first tag in each scenario")
        position_error_item.setData(1, "position_error_plot")  # Store identifier
        self.analysis_list.addItem(position_error_item)

        # Combined Metrics Plot
        combined_metrics_item = QListWidgetItem("📊 Combined Metrics Plot - Position Error and Tag Truth GDOP per Scenario")
        combined_metrics_item.setToolTip("Open a grouped bar chart showing position error and tag truth GDOP for the first tag in each scenario")
        combined_metrics_item.setData(1, "combined_metrics_plot")  # Store identifier
        self.analysis_list.addItem(combined_metrics_item)

    def _open_analysis(self, item):
        """Open the selected analysis in a new window."""
        analysis_type = item.data(1)

        if analysis_type == "comparison_plot":
            self._open_comparison_plot()
        elif analysis_type == "multi_trilat_plot":
            self._open_multi_trilat_plot()
        elif analysis_type == "position_error_plot":
            self._open_position_error_plot()
        elif analysis_type == "combined_metrics_plot":
            self._open_combined_metrics_plot()
        # elif analysis_type == "trilat_plot":
        #     self._open_trilat_plot()
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

    def _open_position_error_plot(self):
        """Open the position error plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = PositionErrorPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Position Error Plot: {str(e)}")

    def _open_combined_metrics_plot(self):
        """Open the combined metrics plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = CombinedMetricsPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Combined Metrics Plot: {str(e)}")