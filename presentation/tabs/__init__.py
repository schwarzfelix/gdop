"""
Tab widgets for the GDOP application.
"""

from .base_tab import BaseTab
from .plot_tab import PlotTab
from .sandbox_tab import SandboxTab
from .stations_tab import StationsTab
from .display_tab import DisplayTab
from .data_tab import DataTab
from .measurements_tab import MeasurementsTab
from .scenarios_tab import ScenariosTab
from .tree_tab import TreeTab

__all__ = [
    'BaseTab',
    'PlotTab',
    'SandboxTab',
    'StationsTab',
    'DisplayTab',
    'DataTab',
    'MeasurementsTab',
    'ScenariosTab',
    'TreeTab'
]
