import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication

import presentation
import simulation

mpl.use('macosx')

if __name__ == "__main__":
    scenario = simulation.Scenario()
    app = QApplication(sys.argv)
    window = presentation.MainWindow(scenario)
    window.show()
    sys.exit(app.exec_())