from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

BLUR_RADIUS = 15
X_OFFSET = 3
Y_OFFSET = 5
COLOR = QColor(0, 0, 0, 180)

def create_shadow_effect() -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(BLUR_RADIUS)
    shadow.setXOffset(X_OFFSET)
    shadow.setYOffset(Y_OFFSET)
    shadow.setColor(COLOR)
    return shadow

def on_button_pressed(shadow):
    shadow.setOffset(int(X_OFFSET/2), int(Y_OFFSET/2))
    shadow.setBlurRadius(int(BLUR_RADIUS/2))
    shadow.setColor(COLOR)

def on_button_released(shadow):
    # Restore the original shadow effect
    shadow.setBlurRadius(BLUR_RADIUS)
    shadow.setXOffset(X_OFFSET)
    shadow.setYOffset(Y_OFFSET)
    shadow.setColor(COLOR)

# def on_button_toggled(checked, shadow_effect):
#     if checked:
#         # Change shadow color or parameters when checked
#         shadow_effect.setColor(QColor(50, 50, 50, 180))
#     else:
#         # Revert to original shadow parameters
#         shadow_effect.setColor(QColor(0, 0, 0, 180))