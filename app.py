import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication

import presentation
import simulation

mpl.use('macosx')

if __name__ == "__main__":
    gdop_sim = simulation.Scenario()
    gdop_plt = presentation.TrilatPlot(gdop_sim, show=False)

    app = QApplication(sys.argv)
    window = presentation.MainWindow(gdop_sim, gdop_plt)
    gdop_plt.window = window
    window.show()
    sys.exit(app.exec_())