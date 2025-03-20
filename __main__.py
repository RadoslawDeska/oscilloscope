from decimal import Decimal
import logging
import os
import subprocess
import sys


from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

import front_panel
from settings.settings_manager import SettingsManager
from signal_generator.signals import SignalManager

# from systems.sample_system import sample_functions as sf
# from systems.trigger_system import trigger_functions as tf
# from systems.vertical_system import vertical_functions as vf

try:
    subprocess.run(["pyuic5", "./front_panel/gui.ui", "-o", "./front_panel/gui.py"])
    # print("front panel gui updated")
except Exception:
    sys.exit()

from front_panel.gui import Ui_MainWindow  # noqa

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
            
class Oscilloscope(QtWidgets.QMainWindow, Ui_MainWindow, SettingsManager, SignalManager):
    timebase_selected = pyqtSignal(Decimal)
    delay_selected = pyqtSignal(Decimal)
    connector1_toggled = pyqtSignal(bool)
    connector2_toggled = pyqtSignal(bool)
    channel_toggled = pyqtSignal(int, bool)  # channel, state
    channel_scale_selected = pyqtSignal(object)
    channel_position_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
                
        front_panel.initialize_gui(self)
        self.signalmanager = SignalManager(self)
        
        self.setWindowTitle("Python oscilloscope")
                
        if os.path.exists("settings/settings.json"):
            self.read_settings()
        else:
            self.factory_defaults()
            self.save_settings()
        
        self.onOff_button.clicked.connect(lambda: front_panel.toggle_front_panel(self))
    
    def closeEvent(self, event):
        self.save_settings()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Oscilloscope()
    
    # TESTING

    window.show()
    app.exec_()
