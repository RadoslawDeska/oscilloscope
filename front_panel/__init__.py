from decimal import Decimal
from typing import Dict, List

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from .graphics_effects import qss, shadows
from systems.horizontal_system import horizontal_functions as hf
from systems.vertical_system import available_scales, vertical_functions as vf
from .actions.display import update_timebase_label, update_delay_label
from .actions.connectors import use_plug

from front_panel.custom_widgets.chart import MplCanvas


def initialize_gui(self):
    self.illuminable_buttons: List[QtWidgets.QPushButton] = [  # type: ignore
        # top section
        self.cursors_button,
        self.measure_button,
        self.displayPersist_button,
        self.history_button,
        self.decode_button,
        self.runStop_button,
        # trigger
        self.auto_button,
        self.normal_button,
        self.single_button,
        # horizontal
        self.roll_button,
        # vertical
        self.channel1sw_button,
        self.channel2sw_button,
        self.Math_button,
        self.Ref_button,
    ]

    self.nonilluminable_buttons: List[QtWidgets.QPushButton] = [  # type: ignore
        self.option1_button,
        self.option2_button,
        self.option3_button,
        self.option4_button,
        self.option5_button,
        self.option6_button,
        self.default_button,
        self.acquire_button,
        self.clearSweeps_button,
        self.saveRecall_button,
        self.utility_button,
        self.print_button,
        self.autoSetup_button,
        self.setup_button,
        self.menu_button,
    ]

    self.connectors: List[QtWidgets.QPushButton] = [  # type: ignore
        self.channel1_connector,
        self.channel2_connector,
        self.external_connector,
        self.ground_connector,
    ]

    self.channel_connectors: Dict[QtWidgets.QPushButton, int] = {  # type: ignore
        self.channel1_connector: 1,
        self.channel2_connector: 2,
    }

    self.channel_switches: Dict[QtWidgets.QPushButton, int] = {  # type: ignore
        self.channel1sw_button: 1,
        self.channel2sw_button: 2,
    }

    self.large_knobs: List[QtWidgets.QDial] = [  # type: ignore
        self.channel1var_dial,
        self.channel2var_dial,
        self.horizontalScaleKnob,
    ]

    self.small_knobs: List[QtWidgets.QDial] = [  # type: ignore
        self.universalSelectionKnob,
        self.channel1pos_dial,
        self.channel2pos_dial,
        self.triggerDelayKnob,
        self.triggerLevelKnob,
    ]

    self.channel_pos_knobs: List[QtWidgets.QDial] = [  # type: ignore
        self.channel1pos_dial,
        self.channel2pos_dial,
    ]

    # Make the dial ignore mouse events
    for knob in self.small_knobs + self.large_knobs:
        knob.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # type: ignore

    for button in self.illuminable_buttons + [self.onOff_button]:
        button.setStyleSheet(qss.illuminated_button_style)

    # Add shadows to the dials
    for knob in self.small_knobs + self.large_knobs:
        knob.setGraphicsEffect(shadows.create_shadow_effect())

    # Add shadows to the buttons
    # Create a dictionary to store shadow effects
    self.shadow_effects = {}

    for button in self.illuminable_buttons + self.nonilluminable_buttons + [self.onOff_button]:
        shadow_effect = shadows.create_shadow_effect()
        button.setGraphicsEffect(shadow_effect)
        self.shadow_effects[button] = shadow_effect

        button.pressed.connect(lambda b=button: shadows.on_button_pressed(self.shadow_effects[b]))
        button.released.connect(lambda b=button: shadows.on_button_released(self.shadow_effects[b]))

    # Set fixed size property for smooth operation of CustomDial class
    for knob in self.large_knobs:
        knob.setFixedSize(80, 80)

    for knob in self.small_knobs:
        knob.setFixedSize(60, 60)

    # Set extremes for the CustomDial class
    self.triggerDelayKnob.setMinimum(-50)
    self.triggerDelayKnob.setMaximum(50)
    self.triggerDelayKnob.initialize_precision_features(allow_precise=True, fine_step_factor=7)

    for knob in self.large_knobs[:2]:  # vertical scale knobs
        knob.setMinimum(0)
        knob.setMaximum(len(available_scales) - 1)

def toggle_front_panel(self):
    """(De-)Activate the front panel of the oscilloscope by activating signal/slot connections."""
    state = self.onOff_button.isChecked()

    # Make the dials (not) ignore mouse events
    for knob in self.small_knobs + self.large_knobs:
        knob.setAttribute(Qt.WA_TransparentForMouseEvents, not (state))  # type: ignore

    for item in self.connectors + self.illuminable_buttons + self.nonilluminable_buttons:
        item.setEnabled(state)

    if state:  # Activate the front panel
        activate_front_panel(self)

    else:  # Deactivate the front panel
        deactivate_front_panel(self)


def set_dials_from_settings(self):
    """SET DIALS BASED ON SETTINGS"""
    # Horizontal
    self.timebase = Decimal(self.settings["Horizontal"]["timebase"])
    hf.set_horizontalScaleKnob(self, self.timebase)
    self.delay = Decimal(self.settings["Horizontal"]["delay"])
    hf.set_triggerDelayKnob(self, self.delay, self.timebase)

    # Vertical
    vf.set_current_scale(self, channel=1, scale=self.channel1.Vdiv)
    vf.set_current_scale(self, channel=2, scale=self.channel2.Vdiv)
    ## using current scale set limits on position dials
    vf.set_posdial_limits(self.channel1.Vdiv, self.channel1pos_dial)
    vf.set_posdial_limits(self.channel2.Vdiv, self.channel2pos_dial)
    ## set current offset within the set limits
    vf.set_current_offset(self, channel=1, offset_data=self.channel1.Offset)
    vf.set_current_offset(self, channel=2, offset_data=self.channel2.Offset)


def update_labels_on_display(self):
    """Update labels on the Oscilloscope display"""
    update_timebase_label(self, self.timebase)
    update_delay_label(self, self.delay)


def add_chart_to_layout(self):
    self.canvas = MplCanvas(
        parent=self,
        delay_position=float(self.delay),
        xlim=hf.calculate_chart_xlimit(self, self.timebase, self.delay),
        ylim1=vf.calculate_chart_ylimits(self.channel1.Vdiv, self.channel1.Offset),
        ylim2=vf.calculate_chart_ylimits(self.channel2.Vdiv, self.channel2.Offset),
    )
    self.chartLayout.addWidget(self.canvas)
    for channel in [1, 2]:
        indicator = getattr(self.canvas, f"channel{channel}_offset_indicator")
        indicator.show() if getattr(self, f"channel{channel}").Enabled else indicator.hide()
        vf.relim_and_update_chart(
            self,
            getattr(self, f"channel{channel}").Vdiv,
            getattr(self, f"channel{channel}").Offset,
            channel=channel,
        )


def activate_dials(self):
    """CONNECT DIALS TO FUNCTIONS"""
    # horizontal
    self.horizontalScaleKnob.valueChanged.connect(lambda: hf.adjust_horizontal_scale(self))
    self.timebase_selected.connect(lambda tb, self=self: update_timebase_label(self, tb))
    self.timebase_selected.connect(self.canvas.update_trigger_triangle_position)

    self.triggerDelayKnob.valueChanged.connect(lambda: hf.adjust_trigger_delay(self))
    self.delay_selected.connect(lambda delay, self=self: update_delay_label(self, delay))
    self.delay_selected.connect(self.canvas.update_trigger_triangle_position)

    # vertical
    self.channel1var_dial.valueChanged.connect(
        lambda _, self=self: vf.adjust_vertical_scale(self, channel=1)
    )
    self.channel2var_dial.valueChanged.connect(
        lambda _, self=self: vf.adjust_vertical_scale(self, channel=2)
    )

    self.channel1pos_dial.valueChanged.connect(
        lambda _, self=self: vf.adjust_vertical_position(self, channel=1)
    )
    self.channel2pos_dial.valueChanged.connect(
        lambda _, self=self: vf.adjust_vertical_position(self, channel=2)
    )


def activate_connectors(self):
    for connector, id in self.channel_connectors.items():
        connector.toggled.connect(
            lambda state, conn=connector, id=id, self=self: use_plug(self, conn, id, state)
        )


def activate_channel_switches(self):
    for switch, id in self.channel_switches.items():
        switch.toggled.connect(
            lambda checked, self=self, id=id: vf.enable_channel(self, id, checked)
        )


def activate_front_panel(self):
    # SIGNAL GENERATION
    self.channel1_thread = None
    self.channel1_generator = None
    self.channel2_thread = None
    self.channel2_generator = None

    set_dials_from_settings(self)
    update_labels_on_display(self)
    add_chart_to_layout(self)

    activate_dials(self)
    activate_connectors(self)

    activate_channel_switches(self)


def deactivate_front_panel(self):
    self.chartLayout.removeWidget(self.canvas)
    self.canvas.deleteLater()  # This causes the error in canvas reference
    # (C/C++ wrapped object is removed but the program still tries to update the canvas)
    # it is not enough to remove this line, because after re-activating front panel delay is not updating.

    for connector in self.connectors:
        try:
            connector.clicked.disconnect()
        except Exception:
            pass

    try:
        self.timebase_selected.disconnect()
    except Exception:
        pass
