import logging
from PyQt5 import QtWidgets

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def use_plug(self, connector: QtWidgets.QPushButton, channel, state: bool):
    if type(connector) is QtWidgets.QPushButton:
        logging.debug(f"Connector {connector.objectName()} is now {'enabled' if state else 'disabled'}.")
        if channel == 1:
            self.connector1_toggled.emit(state)
        elif channel == 2:
            self.connector2_toggled.emit(state)
        else:
            logging.error("Only channels 1 and 2 are supported.")
    else:
        logging.error("Connector is not a QPushButton object.")