import sys
import threading
from PyQt5.QtWidgets import QApplication

import presentation
import simulation
from data.sse import test_function

if __name__ == "__main__":
    scenario = simulation.Scenario()

    test_thread = threading.Thread(target=test_function, args=(scenario,), daemon=True)
    test_thread.start()

    app = QApplication(sys.argv)
    window = presentation.MainWindow(scenario)
    window.show()
    sys.exit(app.exec_())