from PyQt5.QtWidgets import QDial
from PyQt5.QtCore import Qt, QPointF
import math

class CustomDial(QDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWrapping(False)
        self.setMouseTracking(True)  # Enable mouse tracking

        # Variable to store the initial mouse position during a press
        self.initial_angle = 0
        self.angle_diff = 0
        self.is_dragging = False
        
        self.restricted = False
        
        self.allow_precise = False  # determine whether to allow fine stepping
        self.coarse_min = None  # To be initialized later
        self.coarse_max = None  # To be initialized later
        self.shift_flag = False  # Flag to detect the Shift key press

    def initialize_precision_features(self, allow_precise=False, fine_step_factor: int = 10):
        self.allow_precise = allow_precise
        if self.coarse_min is None or self.coarse_max is None:
            self.coarse_min = self.minimum()
            self.coarse_max = self.maximum()
        
        self.fine_step_factor: int = fine_step_factor
    
    def mousePressEvent(self, event):
        self.h = self.size().height()
        self.w = self.size().width()
                
        # Calculate the initial angle when the mouse is pressed
        if event.button() == Qt.LeftButton:  # type: ignore
            self.is_dragging = True
            self.initial_angle = self.calculate_angle(event.pos())
            self.previous_mouse_position = event.pos()
            
            self.quad = self.get_current_quadrant(event)
            self.previous_quad = self.get_current_quadrant(event)
                                    
            super().mousePressEvent(event)

    def get_current_quadrant(self, event):
        # Mouse location quadrant
        if event.x() > self.w/2 and event.y() <= self.h/2:
            return 1
        elif event.x() > self.w/2 and event.y() > self.h/2:
            return 2
        elif event.x() <= self.w/2 and event.y() > self.h/2:
            return 3
        elif event.x() <= self.w/2 and event.y() <= self.h/2:
            return 4
        
        return 0
                
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Get current quadrant of the mouse position
            self.quad = self.get_current_quadrant(event)
            
            # Calculate the current angle when the mouse moves
            current_angle = self.calculate_angle(event.pos())
            
            # Calculate angle difference between last known position and new position
            self.angle_diff = current_angle - self.initial_angle
            
            # Check if the Shift key is pressed for precision
            shift_pressed = event.modifiers() & Qt.ShiftModifier  # type: ignore

            if self.allow_precise:
                if shift_pressed and not self.shift_flag:
                    # Or if the shift key was detected for the first time
                    # flag the event and change the stepping
                    self.shift_flag = True
                    self.shift_stepping(shift_pressed)
                elif shift_pressed and self.shift_flag:
                    # or if the shift key is still pressed
                    pass
                else:
                    # or if the shift key was released
                    self.shift_flag = False  # Reset the flag
                    self.shift_stepping(shift_pressed)  # Restore the original stepping
            
            # Restrictions are only for non-wrapped dials
            if not self.wrapping():
                ### ALL BELOW CHECKS FOR RESTRICTIONS SEEM REQUIRED FOR SMOOTH OPERATION OF DIAL ###
                
                if not self.restricted and self.value() == self.minimum() and self.angle_diff < 0:
                    self.restricted = True
                    # print("Restriction applied due to minimum and counter-clockwise rotation")
                    return
                
                if not self.restricted and self.value() == self.maximum() and self.angle_diff > 0:
                    self.restricted = True
                    # print("Restriction applied due to maximum and clockwise rotation")
                    return
                
                # Set restriction for the revolution direction
                # if the crossing through non-valued area occurs
                if not self.restricted and \
                        (self.quad == 2 and self.previous_quad == 3) or \
                        (self.quad == 3 and self.previous_quad == 2):
                    self.restricted = True
                    # print("Restriction applied due to crossing between quadrants 2 and 3")
                    return
                
                # Lift restriction only:
                # when mouse is back to the last valid quadrant
                # and the value is not at extreme and mouse not continuing past the extreme.
                if self.restricted and self.quad == self.previous_quad:
                    if self.value() == self.minimum() and self.angle_diff < 0:
                        return
                    if self.value() == self.maximum() and self.angle_diff > 0:
                        return
                    # print("Restriction lifted")
                    self.restricted = False
                
                if abs(self.value() - self.maximum()) > 0:
                    if self.restricted:
                        # print("maximum value: jumping to minimum in restricted mode")
                        return
                if abs(self.value() - self.minimum()) > 0:
                    if self.restricted:
                        # print("minimum value: jumping to maximum in restricted mode")
                        return
                
                ### END OF RESTRICTION CHECKS ###
            
            # Calculate the new value based on the angle difference
            # The maximum and minimum difference comes from the Shift key interaction
            value_change = self.angle_diff / 360 * (self.maximum() - self.minimum())
            
            # Change result based on Shift key (step is controlled by Shift key)
            new_value = self.value() - value_change
            
            # Restrictions are only for non-wrapped dials
            if not self.wrapping():
                if new_value > self.maximum():
                    new_value = self.maximum()  # Lock to the maximum value
                elif new_value < self.minimum():
                    new_value = self.minimum()  # Lock to the minimum value
                     
            self.setValue(int(new_value))
                            
            # Update initial angle for the next movement
            self.initial_angle = current_angle
                
            # Update previous mouse position
            self.previous_mouse_position = event.pos()
            
            if self.restricted:
                return
            
            # Update previous quadrant of the dial
            self.previous_quad = self.get_current_quadrant(event)
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Reset dragging state on mouse release
        self.is_dragging = False
        
        if self.restricted:
            return
        
        if self.shift_flag:
            self.shift_stepping(False)
        
        super().mouseReleaseEvent(event)

    def calculate_angle(self, mouse_position):
        # Calculate the angle between the center of the dial and the mouse position
        center = self.rect().center()
        delta = QPointF(mouse_position.x() - center.x(), mouse_position.y() - center.y())
        angle = math.degrees(math.atan2(delta.y(), delta.x()))  # Angle in degrees
        
        # Normalize angle to be between 0 and 360 degrees
        if angle < 0:
            angle += 360
        
        return angle
    
    def shift_stepping(self, shift_pressed):
        if shift_pressed:
            # Fine stepping - increase the resolution
            self.setMinimum(self.minimum()*self.fine_step_factor)
            self.setMaximum(self.maximum()*self.fine_step_factor)
        
        else:
            # Define self.coarse_min and self.coarse_max if necessary
            self.initialize_precision_features(self.allow_precise, self.fine_step_factor)
            
            # Coarse stepping - restore the original resolution
            self.setMinimum(self.coarse_min)  # type: ignore
            self.setMaximum(self.coarse_max)  # type: ignore