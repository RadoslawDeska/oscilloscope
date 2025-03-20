from decimal import Decimal
import json

from settings.channel import Channel


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
    

class SettingsManager:
    input_impedance = {"50": 50, "1M": 1e6}  # Ohm
    trigger_options = {
        "Type": ["Edge", "Slope", "Pulse", "Video", "Window", "Interval", "DropOut", "Runt", "Pattern"],
        "Source": ["CH1", "CH2", "EXT", "EXT/5", "AC LINE"],
        "Slope": ["Rising", "Falling"],
        "Coupling": ["AC", "DC", "HF REJECT", "LF REJECT"],
        "Mode": ["AUTO", "NORMAL", "SINGLE"],
    }
    channel_options = {
        "Unit": ["V", "I"],
        "Coupling": ["DC", "AC", "GND"],
        "BW_limit": ["Full", "20MHz"],
        "Adjust": ["Coarse", "Fine"],
        "Impedance": ["50", "1M"],
        "Probe": [.1, .2, .5,
                  1, 2, 5,
                  10, 20, 500,
                  100, 200, 500,
                  1000, 2000, 5000,
                  10000],
    }

    default_trigger = {
        "Type": trigger_options["Type"][0],
        "Source": trigger_options["Source"][0],
        "Slope": trigger_options["Slope"][0],
        "Holdoff": 0,
        "Coupling": trigger_options["Coupling"][1],
        "Noise reject": False,
        "Mode": trigger_options["Mode"][0],
    }

    default_channels = {
        "1": {
            "Enabled": True,
            "Vdiv": 1,
            "Offset": 0,
            "Coupling": channel_options["Coupling"][0],
            "BW_limit": channel_options["BW_limit"][0],
            "Adjust": channel_options["Adjust"][0],
            "Probe": channel_options["Probe"][3],
            "Impedance": input_impedance["1M"],
            "Unit": channel_options["Unit"][0],
            "Invert": False,
        },
        "2": {
            "Enabled": False,
            "Vdiv": 1,
            "Offset": 0,
            "Coupling": channel_options["Coupling"][0],
            "BW_limit": channel_options["BW_limit"][0],
            "Adjust": channel_options["Adjust"][0],
            "Probe": channel_options["Probe"][3],
            "Impedance": input_impedance["1M"],
            "Unit": channel_options["Unit"][0],
            "Invert": False,
        },
    }
    
    ## Default settings must be instance of SettingsManager class to exist in FrontPanel class
    # Horizontal
    timebase = 1e-6  # s/div
    letter = "u"  # to match self.Tdiv
    delay = 0  # s
    zoom = False
    format = "YT"

    # Vertical
    channel1 = Channel(**default_channels["1"])
    channel2 = Channel(**default_channels["2"])

    # Acquire
    acquisition = "Normal"
    sinxx = "Sinx"
    mem_depth = 14e6  # points

    # Trigger
    trigger = default_trigger

    # Here go other default properties
    pass

    def read_settings(self):
        """Read the settings from the oscilloscope."""
        with open("settings/settings.json", "r") as file:
            self.settings = json.load(file)
        # Tweak the parameters
        channels = ["Channel1", "Channel2"]
        fields = ["Vdiv", "Offset"]
        for channel in channels:
            for field in fields:
                # Force reading Vdiv and Offset as Decimal
                self.settings["Vertical"][channel][field] = Decimal(self.settings["Vertical"][channel][field])
                # Force reading channel as Disabled initially
                self.settings["Vertical"][channel]["Enabled"] = False
        self.set_settings()
    
    def save_settings(self):
        """Save the settings to the oscilloscope."""
        self.get_settings()
        
        with open("settings/settings.json", "w") as f:
            json.dump(self.settings, f, indent=4, cls=CustomJSONEncoder)

    def factory_defaults(self):
        # Horizontal
        self.timebase = Decimal('1e-6')  # s/div
        self.letter = "u"  # to match self.Tdiv
        self.delay = Decimal(0)  # s
        self.zoom = False
        self.format = "YT"

        # Vertical
        self.channel1 = Channel(**self.default_channels["1"]) if isinstance(self.channel1, Channel) else self.channel1
        self.channel2 = Channel(**self.default_channels["2"]) if isinstance(self.channel2, Channel) else self.channel2

        # Acquire
        self.acquisition = "Normal"
        self.sinxx = "Sinx"
        self.mem_depth = 14e6  # points

        # Trigger
        self.trigger = self.default_trigger

        # Here go other default properties
        pass
        
        self.get_settings()

    def get_settings(self):
        self.settings = {
            "Horizontal": {
                "timebase": self.timebase,
                "letter": self.letter,
                "delay": self.delay,
                "zoom": self.zoom,
                "format": self.format,
            },
            "Vertical": {
                "Channel1": self.channel1.to_dict(),
                "Channel2": self.channel2.to_dict(),
            },
            "Acquire": {
                "acquisition": self.acquisition,
                "sinxx": self.sinxx,
                "mem_depth": self.mem_depth,
            },
            "Trigger": self.trigger,
        }
    
    def set_settings(self):
        if "Horizontal" in self.settings and "Vertical" in self.settings:
            self.timebase = Decimal(self.settings["Horizontal"]["timebase"])
            self.letter = self.settings["Horizontal"]["letter"]
            self.delay = Decimal(self.settings["Horizontal"]["delay"])
            self.zoom = self.settings["Horizontal"]["zoom"]
            self.format = self.settings["Horizontal"]["format"]

            self.channel1 = Channel(**self.settings["Vertical"]["Channel1"])
            self.channel2 = Channel(**self.settings["Vertical"]["Channel2"])

            self.acquisition = self.settings["Acquire"]["acquisition"]
            self.sinxx = self.settings["Acquire"]["sinxx"]
            self.mem_depth = self.settings["Acquire"]["mem_depth"]

            self.trigger = self.settings["Trigger"]
        else:
            raise ValueError("Invalid settings structure")