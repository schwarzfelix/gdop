import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication

from plot import Plot
from simulation import Simulation
from window import MainWindow

mpl.use('macosx')

if __name__ == "__main__":
    gdop_sim = Simulation()
    gdop_plt = Plot(gdop_sim, show=False)

    app = QApplication(sys.argv)
    window = MainWindow(gdop_sim, gdop_plt)
    window.show()
    sys.exit(app.exec_())