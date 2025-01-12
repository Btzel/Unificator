from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QStackedWidget
import os
import res_rc

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)  # Load the UI file
        self.button_to_panel_bind()
        
    def button_to_panel_bind(self):
        self.pushButton_6.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(0))
        self.pushButton_8.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(1))
        