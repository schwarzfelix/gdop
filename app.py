import sys
from PyQt5.QtWidgets import QApplication

import presentation
import simulation


class GDOPApp:
    """Simple application container holding scenarios."""
    def __init__(self, scenarios=None):
        self.scenarios = scenarios or []


if __name__ == "__main__":
    scenario = simulation.Scenario()
    gdop_app = GDOPApp([scenario])
    qt_app = QApplication(sys.argv)
    window = presentation.MainWindow(gdop_app)
    window.app = gdop_app
    window.show()
    sys.exit(qt_app.exec_())