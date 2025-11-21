"""
Analysis tab for the GDOP application.
Shows a list of available plots and analysis options that can be opened in separate windows.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel
from .base_tab import BaseTab
from presentation.comparisonplot_window import ComparisonPlotWindow
from presentation.multi_trilatplot_window import MultiTrilatPlotWindow
from presentation.arrangementpositionerrorplot_window import ArrangementPositionErrorPlotWindow
from presentation.arrangementanchorcountpositionerrorplot_window import ArrangementAnchorCountPositionErrorPlotWindow
from presentation.arrangementdistanceerrorplot_window import ArrangementDistanceErrorPlotWindow
from presentation.arrangementdistancestddevplot_window import ArrangementDistanceStdDevPlotWindow
from presentation.accesspointmetricsplot_raw_window import AccessPointMetricsPlotRawWindow
from presentation.combinedmetricslineplot_sorted_window import CombinedMetricsLinePlotSortedWindow
from presentation.aggregationmethodaverageplot_window import AggregationMethodAveragePlotWindow
from presentation.trilaterationmethodaverageplot_window import TrilaterationMethodAveragePlotWindow
from presentation.gdop_position_error_scatterplot_window import GDOPPositionErrorScatterPlotWindow
from presentation.gdop_residualplot_window import GDOPResidualPlotWindow
from presentation.gdop_correlation_analysis import GDOPCorrelationAnalysis

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

        # Arrangement Anchor Count Position Error Plot
        arrangement_anchor_count_position_error_item = QListWidgetItem("📊 Arrangement Position Error Plot - 3A vs 4A (Grouped by Arrangement)")
        arrangement_anchor_count_position_error_item.setToolTip("Open a grouped bar chart showing position error values for 3A and 4A variants side by side, grouped by the first character of the scenario name (arrangement)")
        arrangement_anchor_count_position_error_item.setData(1, "arrangement_anchor_count_position_error_plot")  # Store identifier
        self.analysis_list.addItem(arrangement_anchor_count_position_error_item)

        # Arrangement Distance Error Plot
        arrangement_distance_error_item = QListWidgetItem("📊 Arrangement Distance Error Plot - PD vs FW (Grouped by Arrangement)")
        arrangement_distance_error_item.setToolTip("Open a grouped bar chart showing average distance error values for PD and FW variants side by side, grouped by the first 4 characters of the scenario name (arrangement)")
        arrangement_distance_error_item.setData(1, "arrangement_distance_error_plot")  # Store identifier
        self.analysis_list.addItem(arrangement_distance_error_item)

        # Arrangement Distance Std Dev Plot
        arrangement_distance_stddev_item = QListWidgetItem("📊 Arrangement Distance Std Dev Plot - PD vs FW (Grouped by Arrangement)")
        arrangement_distance_stddev_item.setToolTip("Open a grouped bar chart showing average distance standard deviation values for PD and FW variants side by side, grouped by the first 4 characters of the scenario name (arrangement)")
        arrangement_distance_stddev_item.setData(1, "arrangement_distance_stddev_plot")  # Store identifier
        self.analysis_list.addItem(arrangement_distance_stddev_item)

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

        # Aggregation Method Average Plot
        aggregation_method_average_item = QListWidgetItem("📊 Aggregation Method Average - Mean Position Error per Method")
        aggregation_method_average_item.setToolTip("Show average position error for each aggregation method across all scenarios")
        aggregation_method_average_item.setData(1, "aggregation_method_average")  # Store identifier
        self.analysis_list.addItem(aggregation_method_average_item)

        # Trilateration Method Average Plot
        trilateration_method_average_item = QListWidgetItem("📊 Trilateration Method Average - Mean Position Error per Method")
        trilateration_method_average_item.setToolTip("Show average position error for each trilateration method across all scenarios")
        trilateration_method_average_item.setData(1, "trilateration_method_average")  # Store identifier
        self.analysis_list.addItem(trilateration_method_average_item)

        # GDOP vs Position Error Scatter Plot
        gdop_scatter_item = QListWidgetItem("📈 GDOP vs Position Error - Scatter Plot with Correlation Analysis")
        gdop_scatter_item.setToolTip("Open a scatter plot showing correlation between GDOP and position error with regression line and statistics")
        gdop_scatter_item.setData(1, "gdop_position_error_scatter")  # Store identifier
        self.analysis_list.addItem(gdop_scatter_item)

        # GDOP Residual Plot
        gdop_residual_item = QListWidgetItem("📈 GDOP vs Position Error - Residual Plot")
        gdop_residual_item.setToolTip("Open a residual plot to check for non-linear patterns in GDOP vs position error relationship")
        gdop_residual_item.setData(1, "gdop_residual_plot")  # Store identifier
        self.analysis_list.addItem(gdop_residual_item)

        # GDOP Correlation Analysis (Console)
        gdop_correlation_item = QListWidgetItem("📋 GDOP vs Position Error - Correlation Analysis (Console Output)")
        gdop_correlation_item.setToolTip("Run correlation analysis (Pearson & Spearman) and print detailed statistics to console")
        gdop_correlation_item.setData(1, "gdop_correlation_analysis")  # Store identifier
        self.analysis_list.addItem(gdop_correlation_item)

    def _open_analysis(self, item):
        """Open the selected analysis in a new window."""
        analysis_type = item.data(1)

        if analysis_type == "comparison_plot":
            self._open_comparison_plot()
        elif analysis_type == "multi_trilat_plot":
            self._open_multi_trilat_plot()
        elif analysis_type == "arrangement_position_error_plot":
            self._open_arrangement_position_error_plot()
        elif analysis_type == "arrangement_anchor_count_position_error_plot":
            self._open_arrangement_anchor_count_position_error_plot()
        elif analysis_type == "arrangement_distance_error_plot":
            self._open_arrangement_distance_error_plot()
        elif analysis_type == "arrangement_distance_stddev_plot":
            self._open_arrangement_distance_stddev_plot()
        elif analysis_type == "access_point_metrics_plot_raw":
            self._open_access_point_metrics_plot_raw()
        elif analysis_type == "combined_metrics_line_plot_sorted":
            self._open_combined_metrics_line_plot_sorted()
        elif analysis_type == "aggregation_method_average":
            self._open_aggregation_method_average()
        elif analysis_type == "trilateration_method_average":
            self._open_trilateration_method_average()
        elif analysis_type == "gdop_position_error_scatter":
            self._open_gdop_position_error_scatter()
        elif analysis_type == "gdop_residual_plot":
            self._open_gdop_residual_plot()
        elif analysis_type == "gdop_correlation_analysis":
            self._run_gdop_correlation_analysis()
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

    def _open_arrangement_anchor_count_position_error_plot(self):
        """Open the arrangement anchor count position error plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = ArrangementAnchorCountPositionErrorPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Arrangement Anchor Count Position Error Plot: {str(e)}")

    def _open_arrangement_distance_error_plot(self):
        """Open the arrangement distance error plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = ArrangementDistanceErrorPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Arrangement Distance Error Plot: {str(e)}")

    def _open_arrangement_distance_stddev_plot(self):
        """Open the arrangement distance standard deviation plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = ArrangementDistanceStdDevPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Arrangement Distance Std Dev Plot: {str(e)}")

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

    def _open_aggregation_method_average(self):
        """Open the aggregation method average plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = AggregationMethodAveragePlotWindow(self.main_window, scenarios)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Aggregation Method Average Plot: {str(e)}")

    def _open_trilateration_method_average(self):
        """Open the trilateration method average plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = TrilaterationMethodAveragePlotWindow(self.main_window, scenarios)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open Trilateration Method Average Plot: {str(e)}")

    def _open_gdop_position_error_scatter(self):
        """Open the GDOP vs Position Error scatter plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = GDOPPositionErrorScatterPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open GDOP vs Position Error Scatter Plot: {str(e)}")

    def _open_gdop_residual_plot(self):
        """Open the GDOP residual plot in a new window."""
        try:
            scenarios = self.app.scenarios if self.app else []
            window = GDOPResidualPlotWindow(scenarios, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open GDOP Residual Plot: {str(e)}")

    def _run_gdop_correlation_analysis(self):
        """Run GDOP correlation analysis and print to console."""
        try:
            scenarios = self.app.scenarios if self.app else []
            if not scenarios:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self.main_window, "Warning", "No scenarios loaded. Cannot run correlation analysis.")
                return
            
            analysis = GDOPCorrelationAnalysis(scenarios)
            analysis.run_analysis()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self.main_window, "Analysis Complete", 
                                   "Correlation analysis complete. Check the console output for detailed results.")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to run GDOP Correlation Analysis: {str(e)}")

    def update(self):
        """Update the analysis tab if needed."""
        # For now, no dynamic updates needed
        pass