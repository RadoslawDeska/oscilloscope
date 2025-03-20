from PyQt5 import QtWidgets, QtCore, QtGui

class CustomListView(QtWidgets.QListView):
    """ListView to show QComboBox dropdown always on top."""
    def __init__(self, combo, parent=None):
        super().__init__(parent)
        self.combo = combo

    def showEvent(self, event):
        super().showEvent(event)
        # The view is displayed in a top-level popup window.
        popup = self.window()
        if popup:
            # Get the combo box's top-left corner (global coordinates)
            combo_global_top_left = self.combo.mapToGlobal(self.combo.rect().topLeft())
            # Calculate the new y-coordinate so that the popup appears above the combo
            new_y = combo_global_top_left.y() - popup.height()
            # Reposition the popup while keeping its x-coordinate unchanged
            popup.move(popup.x(), new_y)

class CenteredDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate that centers text in the list items."""
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Center the text horizontally and vertically.
        option.displayAlignment = QtCore.Qt.AlignCenter

class NoArrowStyle(QtWidgets.QProxyStyle):
    """Remove drop-down arrow from QComboBox and give back the reserved space"""
    def subControlRect(self, cc, opt, sc, widget) -> QtCore.QRect:
        if cc == QtWidgets.QStyle.CC_ComboBox:
            if sc == QtWidgets.QStyle.SC_ComboBoxArrow:
                # Do not reserve any space for the arrow.
                return QtCore.QRect()
            elif sc == QtWidgets.QStyle.SC_ComboBoxEditField:
                # Get the default rectangle for the edit field.
                rect = super().subControlRect(cc, opt, sc, widget)
                # Also get the default rectangle for the arrow (which is normally reserved).
                arrowRect = super().subControlRect(cc, opt, QtWidgets.QStyle.SC_ComboBoxArrow, widget)
                # Expand the edit field rectangle horizontally to include the arrow area.
                rect.setRight(rect.right() + arrowRect.width())
                return rect
        return super().subControlRect(cc, opt, sc, widget)

class Dropdown(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use our custom list view for the popup.
        self.setView(CustomListView(self))
        # Set a default title.
        self._title = "TYPE"
        # Set the delegate for the view so that list items are centered.
        self.view().setItemDelegate(CenteredDelegate(self.view()))
        # Set stylesheet
        # Apply the NoArrowStyle (passing the current style as the base)
        self.setStyle(NoArrowStyle(self.style()))
        # Optionally, also clear the drop-down border via a stylesheet.
        self.setStyleSheet("QComboBox::drop-down { border: none; }")

    def setTitle(self, title):
        self._title = title
        self.update()

    def title(self):
        return self._title

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)
        self.style().drawComplexControl(QtWidgets.QStyle.CC_ComboBox, option, painter, self)
        
        text_rect = self.style().subControlRect(QtWidgets.QStyle.CC_ComboBox, option, 
                                                QtWidgets.QStyle.SC_ComboBoxEditField, self)
        
        fontMetrics = painter.fontMetrics()
        line_height = fontMetrics.lineSpacing()  # Height for one line.
        total_text_height = 2 * line_height
        
        extra_space = text_rect.height() - total_text_height
        y_offset = extra_space // 2  if extra_space > 0 else 0
        
        title_rect = QtCore.QRect(text_rect.x(), text_rect.y() + y_offset, text_rect.width(), line_height)
        value_rect = QtCore.QRect(text_rect.x(), text_rect.y() + y_offset + line_height, text_rect.width(), line_height)
        
        painter.setPen(self.palette().color(QtGui.QPalette.Text))
        painter.drawText(title_rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, self._title)
        painter.drawText(value_rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, self.currentText())

    def sizeHint(self):
        base_size = super().sizeHint()
        extra_height = self.fontMetrics().lineSpacing()  # Add one extra line's height.
        return QtCore.QSize(base_size.width(), base_size.height() + extra_height)