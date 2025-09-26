"""
Base tab class for GDOP application tabs.
"""

from abc import ABC, abstractmethod


class BaseTab(ABC):
    """Base class for all tabs in the GDOP application."""
    
    def __init__(self, main_window):
        """
        Initialize the base tab.
        
        Args:
            main_window: Reference to the main window instance
        """
        self.main_window = main_window
        # Reference to application container (holds all scenarios)
        self.app = getattr(main_window, 'app', None)
        self.display_config = main_window.display_config
        self.widget = None

    @property
    def scenario(self):
        return self.main_window.plot.scenario

    @abstractmethod
    def create_widget(self):
        """
        Create and return the widget for this tab.
        
        Returns:
            QWidget: The widget to be added to the tab
        """
        pass
        
    @property
    @abstractmethod
    def tab_name(self):
        """
        Return the name of the tab.
        
        Returns:
            str: The name to display in the tab
        """
        pass
        
    def get_widget(self):
        """
        Get the widget for this tab, creating it if necessary.
        
        Returns:
            QWidget: The widget for this tab
        """
        if self.widget is None:
            self.widget = self.create_widget()
        return self.widget
        
    def update(self):
        """Update the tab content. Override in subclasses if needed."""
        pass
