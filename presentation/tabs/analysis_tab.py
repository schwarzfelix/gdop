"""
Analysis tab for the GDOP application.
Shows a list of available plots and analysis options that can be opened in separate windows.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel
from .base_tab import BaseTab
from presentation.comparisonplot_window import ComparisonPlotWindow

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

        # Future analyses can be added here
        # trilat_item = QListWidgetItem("📈 Trilateration Plot")
        # trilat_item.setData(1, "trilat_plot")
        # self.analysis_list.addItem(trilat_item)

    def _open_analysis(self, item):
        """Open the selected analysis in a new window."""
        analysis_type = item.data(1)

        if analysis_type == "comparison_plot":
            self._open_comparison_plot()
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

    # def _open_trilat_plot(self):
    #     """Open the trilateration plot in a new window (placeholder for future)."""
    #     # This could be implemented later if needed
    #     pass

    def update(self):
        """Update the analysis tab if needed."""
        # For now, no dynamic updates needed
        pass