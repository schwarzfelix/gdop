import sys
from PyQt5.QtWidgets import QApplication

import presentation
import simulation


class GDOPApp:
    def __init__(self, scenarios=None):
        self._scenarios = scenarios or []

    @property
    def scenarios(self):
        return self._scenarios


if __name__ == "__main__":
    scenario = simulation.SandboxScenario("Sandbox")
    gdop_app = GDOPApp([scenario])
    qt_app = QApplication(sys.argv)
    window = presentation.MainWindow(gdop_app)
    window.show()
    sys.exit(qt_app.exec_())