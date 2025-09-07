"""
Sigma tab for the GDOP application.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QDoubleSpinBox
from .base_tab import BaseTab


class SigmaTab(BaseTab):
    """Tab for controlling sigma values."""
    
    SIGMA_SLIDER_MAX = 5
    SIGMA_SLIDER_RESOLUTION = 100
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.slider = None
        self.sigma_input = None
    
    @property
    def tab_name(self):
        return "Sigma"
        
    def create_widget(self):
        """Create and return the sigma tab widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.SIGMA_SLIDER_MAX * self.SIGMA_SLIDER_RESOLUTION)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

        # Create sigma input
        self.sigma_input = QDoubleSpinBox()
        self.sigma_input.setMinimum(0.0)
        self.sigma_input.setSingleStep(0.1)
        self.sigma_input.setValue(0.0)
        self.sigma_input.valueChanged.connect(self.sigma_input_changed)
        layout.addWidget(self.sigma_input)

        return widget
        
    def slider_changed(self):
        """Handle slider value changes."""
        self.scenario.sigma = self.slider.value() / self.SIGMA_SLIDER_RESOLUTION
        self.main_window.update_all()

    def sigma_input_changed(self):
        """Handle sigma input value changes."""
        self.scenario.sigma = self.sigma_input.value()
        self.main_window.update_all()
        
    def update_sigma(self):
        """Update sigma controls with current scenario values."""
        if self.slider and self.sigma_input:
            self.slider.setValue(int(self.scenario.sigma * self.SIGMA_SLIDER_RESOLUTION))
            self.sigma_input.setValue(self.scenario.sigma)
