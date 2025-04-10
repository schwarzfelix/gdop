import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication
from window import MainWindow

mpl.use('macosx')

if __name__ == "__main__":
    #simulation = Simulation()
    #p = Plot(simulation)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())