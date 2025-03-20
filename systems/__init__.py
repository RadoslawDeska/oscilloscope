def get_active_channels(self) -> list:
    """'Active channels' means channels for which signals are currently displayed on screen"""
    active_channels = []
    if self.channel1["Enabled"]:
        active_channels.append(self.channel1["Enabled"])
    if self.channel2["Enabled"]:
        active_channels.append(self.channel2["Enabled"])
    
    return active_channels