from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QToolButton

class PanelManager:
    """Manages the side panel animations and state."""
    
    def __init__(self, panel_frame):
        
        self.panel_frame = panel_frame
        self.panel_frame.setMinimumSize(0, 0)
        self.panel_frame.setMaximumSize(0, 1000000)
        self.current_tool_button = -1
        self.animations = []

    def handle_panel_animation(self, idx, clicked_button):
        """Handle panel animation state and button toggles."""
        if self.current_tool_button == -1:
            self.current_tool_button = idx
            self.animate_panel("Open")
            clicked_button.setChecked(True)
        elif self.current_tool_button == idx:
            self.current_tool_button = -1
            self.animate_panel("Close")
            clicked_button.setChecked(False)
        else:
            self.current_tool_button = idx
            tool_buttons = clicked_button.parent().findChildren(QToolButton)
            for button in tool_buttons:
                button.setChecked(False)
            clicked_button.setChecked(True)

    def animate_panel(self, which_anim):
        """Animate the panel opening/closing."""
        animation = QPropertyAnimation(self.panel_frame, b"minimumWidth")
        animation.setDuration(150)
        
        if which_anim == "Open":
            animation.setStartValue(0)
            animation.setEndValue(300)
        elif which_anim == "Close":
            animation.setStartValue(300)
            animation.setEndValue(0)
            
        self.animations.append(animation)
        animation.start()