import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton, QStackedWidget, QToolButton
from PyQt5.QtCore import QPropertyAnimation, QRect
import os
import res_rc

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'interface.ui')
        uic.loadUi(ui_path, self)
        
        # Panel başlangıçta kapalı olarak ayarlansın (boyutu 0 yaparak)
        self.panel_frame.setMinimumSize(0, 0)
        self.panel_frame.setMaximumSize(0, 1000000)
        
        self.currentToolButton = -1
        self.animations = []
        self.handle_button_clicks()
        
    def handle_button_clicks(self):
        self.adjust_button.clicked.connect(lambda: self.handle_button_page_binds(self.adjust_button, 0))
        self.effects_button.clicked.connect(lambda: self.handle_button_page_binds(self.effects_button, 1))
        
    def handle_button_page_binds(self, button, idx):
        self.stackedWidget_2.setCurrentIndex(idx)
        self.handle_panel_animation(idx)
         

    def handle_panel_animation(self,idx):
        clicked_button = self.sender()
        if self.currentToolButton == -1:
            self.currentToolButton = idx
            self.panel_animation("Open")
            clicked_button.setChecked(True)
        elif self.currentToolButton == idx:
            self.currentToolButton = -1
            self.panel_animation("Close")
            clicked_button.setChecked(False)
        else:
            self.currentToolButton = idx
            tool_buttons = self.findChildren(QToolButton)
            for button in tool_buttons:
                button.setChecked(False)
            clicked_button.setChecked(True)
            
    def panel_animation(self, which_anim):
        animation = QPropertyAnimation(self.panel_frame, b"minimumWidth")
        animation.setDuration(150)  # Animasyon süresi 500 milisaniye

        if which_anim == "Open":
            animation.setStartValue(0)  # Başlangıç değeri: 0 (kapalı)
            animation.setEndValue(300)  # Bitiş değeri: 300 (tam açık)
        elif which_anim == "Close":
            animation.setStartValue(300)  # Başlangıç değeri: 300 (tam açık)
            animation.setEndValue(0)  # Bitiş değeri: 0 (kapalı)

        # Debugging information
        animation.valueChanged.connect(lambda value: print(f"Animasyon değeri: {value}"))
        
        # Keep a reference to avoid garbage collection
        self.animations.append(animation)
        animation.start()






