import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication

from plot import GdopPlot
from simulation import Simulation
from window import MainWindow

mpl.use('macosx')

if __name__ == "__main__":
    gdop_sim = Simulation()
    gdop_plt = GdopPlot(gdop_sim, show=False)

    app = QApplication(sys.argv)
    window = MainWindow(gdop_sim, gdop_plt)
    gdop_plt.window = window
    window.show()
    sys.exit(app.exec_())