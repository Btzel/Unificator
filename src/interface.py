import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QStackedWidget
import os
import res_rc

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)  # Load the UI file
        #panel
        self.currentPanel = 0
        self.handle_button_clicks()
        
    def handle_button_clicks(self):
        self.toolButton.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(0))
        self.toolButton_3.clicked.connect(lambda: self.stackedWidget_2.setCurrentIndex(1))
        
        
    

        

    

