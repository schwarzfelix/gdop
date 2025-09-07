"""
Plot tab for the GDOP application.
"""

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .base_tab import BaseTab


class PlotTab(BaseTab):
    """Tab containing the matplotlib navigation toolbar."""
    
    @property
    def tab_name(self):
        return "Plot"
        
    def create_widget(self):
        """Create and return the plot tab widget."""
        return NavigationToolbar(self.main_window.canvas, self.main_window)
