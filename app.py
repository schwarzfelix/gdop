import sys
from PyQt5.QtWidgets import QApplication

import presentation
import simulation
from data.sse import test_function

if __name__ == "__main__":
    test_function()
    scenario = simulation.Scenario()
    app = QApplication(sys.argv)
    window = presentation.MainWindow(scenario)
    window.show()
    sys.exit(app.exec_())